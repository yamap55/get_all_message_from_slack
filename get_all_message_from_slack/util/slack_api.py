"""Slack APIを操作する関数群"""
from time import sleep
from typing import Any, Callable, Dict, List, Optional

from get_all_message_from_slack.settings import client
from slack_sdk.web.slack_response import SlackResponse


def get_all_public_channels() -> list[dict[str, Any]]:
    """
    全てのpublicチャンネル情報を取得する

    NOTE: 全てのメッセージをメモリに乗せる事に注意

    Returns
    -------
    list[dict[str, Any]]
        チャンネル情報
        フォーマットは下記のchannels以下を参照
        https://api.slack.com/methods/conversations.list#responses
    """
    result: list[dict[str, Any]] = []
    option = {"type:": "public_channel"}
    next_cursor = "DUMMY"  # whileを1度は回すためダミー値を設定
    while next_cursor:
        response = client.conversations_list(**option).data
        result += response["channels"]
        # チャンネルが多い場合は1度で全てを取得できない
        # 尚、メッセージ取得系と異なり「has_more」属性は持っていない
        next_cursor = response["response_metadata"]["next_cursor"]
        option["cursor"] = next_cursor
        sleep(1)  # need to wait 1 sec before next call due to rate limits
    return result


def get_channel_id(name: str) -> str:
    """
    指定されたチャンネルのチャンネルIDを取得

    Parameters
    ----------
    name : str
        チャンネル名

    Returns
    -------
    str
        チャンネルID

    Raises
    -------
    ValueError
        存在しないチャンネル名の場合
    """
    # https://api.slack.com/methods/conversations.list
    try:
        option = {}
        next_cursor = "DUMMY"  # whileを1度は回すためダミー値を設定
        while next_cursor:
            response = client.conversations_list(**option).data
            target_channnels = [
                channel["id"] for channel in response["channels"] if channel["name"] == name
            ]
            if target_channnels:
                return target_channnels[0]
            # チャンネルが多い場合は1度で全てを取得できない
            # 尚、メッセージ取得系と異なり「has_more」属性は持っていない
            next_cursor = response["response_metadata"]["next_cursor"]
            option["cursor"] = next_cursor
            sleep(1)  # need to wait 1 sec before next call due to rate limits
        raise ValueError("not exists channel name.")
    except StopIteration:
        raise ValueError("not exists channel name.")


def get_user_name(user_id: str) -> str:
    """
    指定されたユーザIDのユーザ名を取得

    Parameters
    ----------
    user_id : str
        ユーザID

    Returns
    -------
    str
        ユーザ名

    Raises
    -------
    SlackApiError
        存在しないユーザIDの場合
    """
    # https://api.slack.com/methods/users.info
    return client.users_info(user=user_id)["user"]["real_name"]


def post_message(
    channel_id: str, text: str, thread_ts: Optional[str] = None, mention_users: List[str] = None
) -> Dict[str, Any]:
    """
    指定されたチャンネルにメッセージをポスト

    Parameters
    ----------
    channel_id : str
        チャンネルID
    text : str
        ポストする内容
    thread_ts : Optional[str], optional
        リプライとしたい場合に指定するタイムスタンプ, by default None
    mention_users : List[str], optional
        メンションを指定するユーザID
        テキストの先頭に空白区切りで付与します
        2人以上が指定されている場合はメンション後に改行を追加します, by default []

    Returns
    -------
    Dict[str, Any]
        ポストしたメッセージのデータ
    """
    # https://api.slack.com/methods/chat.postMessage
    mention_users = [] if mention_users is None else mention_users
    mentions = [f"<@{u}>" for u in mention_users]
    mentions_postfix = "\n" if len(mentions) > 1 else ""
    send_message = " ".join(mentions) + mentions_postfix + text

    res = client.chat_postMessage(channel=channel_id, text=send_message, thread_ts=thread_ts)
    return res.data


def __get_all_message_by_iterating(
    func: Callable[..., SlackResponse], option: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """繰り返し処理ですべてのメッセージを取得"""
    response = func(**option).data
    messages_all = response["messages"]
    while response["has_more"]:
        sleep(1)  # need to wait 1 sec before next call due to rate limits
        response = func(**option, cursor=response["response_metadata"]["next_cursor"]).data
        messages = response["messages"]
        messages_all = messages_all + messages
    return messages_all


def get_channel_message(channel_id: str) -> List[Dict[str, Any]]:
    """
    指定されたチャンネルのメッセージを取得

    Parameters
    ----------
    channel_id : str
        チャンネルID

    Returns
    -------
    List[Dict[str, Any]]
        指定されたチャンネルのメッセージ
    """
    # https://api.slack.com/methods/conversations.history
    option = {"channel": channel_id, "limit": 1000}
    return __get_all_message_by_iterating(client.conversations_history, option)


def get_replies(channel_id: str, message: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    指定されたメッセージのリプライを取得

    Parameters
    ----------
    channel_id : str
        チャンネルID
    message : Dict[str, Any]
        リプライを取得する対象のメッセージ

    Returns
    -------
    List[Dict[str, Any]]
        リプライメッセージ
        リプライがついていない場合は空のリスト
    """
    # https://api.slack.com/methods/conversations.replies
    if "thread_ts" not in message:
        return []
    option = {"channel": channel_id, "ts": message["thread_ts"]}
    return __get_all_message_by_iterating(client.conversations_replies, option)

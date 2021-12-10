"""Slack APIを操作する関数群"""
from time import sleep
from typing import Any, Callable, Dict, List, Optional

from get_all_message_from_slack.settings import client
from slack_sdk.web.slack_response import SlackResponse


def get_all_users() -> list[dict[str, Any]]:
    """
    全てのユーザ情報を取得する

    Returns
    -------
    list[dict[str, Any]]
        ユーザ情報
        フォーマットは下記のchannels以下を参照
        https://api.slack.com/methods/users.list#responses
    """
    return __get_all_data_by_iterating(client.users_list, {}, "members", False)


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
    return __get_all_data_by_iterating(
        client.conversations_list, {"type:": "public_channel"}, "channels", False
    )


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


def __get_all_message_by_iterating(
    func: Callable[..., SlackResponse], option: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """繰り返し処理ですべてのメッセージを取得"""
    return __get_all_data_by_iterating(func, option, "messages", True)


def __get_all_data_by_iterating(
    func: Callable[..., SlackResponse],
    option: Dict[str, Any],
    data_key: str,
    has_more_attribute: bool,
) -> List[Dict[str, Any]]:
    """繰り返し処理ですべてのデータを取得"""

    def has_more(r):
        return bool(
            response["has_more"]
            if has_more_attribute
            else response["response_metadata"]["next_cursor"]
        )

    response = func(**option).data
    data_all = response[data_key]

    while has_more(response):
        sleep(1)  # need to wait 1 sec before next call due to rate limits
        response = func(**option, cursor=response["response_metadata"]["next_cursor"]).data
        data = response[data_key]
        data_all = data_all + data
    return data_all

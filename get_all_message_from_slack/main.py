"""main"""
import json
from datetime import datetime
from logging import config, getLogger
from pathlib import Path
from typing import Any

import get_all_message_from_slack.settings as settings
from get_all_message_from_slack.util.slack_api import (
    get_all_public_channels,
    get_all_users,
    get_channel_message,
    get_replies,
)

config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = getLogger(__name__)
client = settings.client


def main():
    """
    main
    """
    logger.info("get all message from slack start.")
    base_path = _create_base_path()
    channels = _get_channels(base_path)
    _get_users(base_path)
    for channel in channels:
        _get_channel_message(base_path, channel["id"], channel["name"])
    logger.info("get all message from slack finished")


def _create_base_path() -> Path:
    """
    出力ファイルのBaseとなるPathを作成

    Returns
    -------
    Path
        baseとなるPath
    """
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = Path(f"./work/{now}")
    logger.info(f"save base path: {base_path}")
    base_path.mkdir()
    return base_path


def _get_channels(base_path: Path) -> list[dict[str, Any]]:
    """
    全てのpublicチャンネル情報を取得

    Parameters
    ----------
    base_path : Path
        出力先のBaseとなるPath

    Returns
    -------
    list[dict[str, Any]]
        全てのpublicチャンネル情報
    """
    logger.info("get all public channels.")
    channels = get_all_public_channels()
    channel_path = base_path / "channel_master.json"
    logger.info(f"save all public channels. path: {channel_path}")
    _save_to_json(channels, channel_path)
    return channels


def _get_users(base_path: Path) -> list[dict[str, Any]]:
    """
    全てのユーザ情報を取得

    Parameters
    ----------
    base_path : Path
        出力先のBaseとなるPath

    Returns
    -------
    list[dict[str, Any]]
        全てのユーザ情報
    """
    logger.info("get all users.")
    users = get_all_users()
    users_path = base_path / "user_master.json"
    logger.info(f"save all users. path: {users_path}")
    _save_to_json(users, users_path)
    return users


def _get_channel_message(base_path: Path, channel_id: str, channel_name: str) -> None:
    """
    チャンネル情報を取得

    NOTE: 全てメモリに乗せるためメモリ不足に注意

    Parameters
    ----------
    base_path : Path
        出力先のBaseとなるPath
    channel_id : str
        チャンネルID
    channel_name : str
        チャンネル名
    """
    channel_info = f"id:{channel_id}, name: {channel_name}"
    logger.info(f"get channel_message. {channel_info}")
    messages = get_channel_message(channel_id)

    messages_path = base_path / channel_id
    messages_path.mkdir()
    channel_message_path = messages_path / "nomal_messages.json"
    logger.info(f"save channel message. {channel_info}, path: {channel_message_path}")
    _save_to_json(messages, channel_message_path)  # type: ignore

    logger.info(f"get replies_message. {channel_info}")
    for message in messages:
        _get_replies(messages_path, message, channel_id, channel_info)


def _get_replies(
    base_path: Path, message: dict[str, Any], channel_id: str, channel_info: str
) -> None:
    """
    リプライメッセージを取得

    Parameters
    ----------
    base_path : Path
        出力先のBaseとなるPath
    message : dict[str, Any]
        メッセージ情報
    channel_id : str
        チャンネルID
    channel_info : str
        チャンネル情報
    """
    replies = get_replies(channel_id, message)
    if replies:
        # NOTE: '1638883139.000600' のように「.」が入るとファイル名として不適格なので「_」に置換
        thread_ts = message["thread_ts"].replace(".", "_")
        replies_path = base_path / f"{thread_ts}.json"
        logger.info(f"save replies message. {channel_info}, path: {replies_path}")
        _save_to_json(replies, replies_path)  # type: ignore


def _save_to_json(data: Any, path: Path) -> Path:
    """
    json形式で保存する

    Parameters
    ----------
    data : Any
        保存対象のデータ
    path : Path
        保存先

    Returns
    -------
    Path
        保存されたPath
    """
    with open(path, "w") as f:
        json.dump(data, f)
    return path


if __name__ == "__main__":
    main()

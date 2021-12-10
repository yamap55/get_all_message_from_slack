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
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = Path(f"./work/{now}")
    base_path.mkdir()

    logger.info("get all public channels.")
    channels = get_all_public_channels()
    channel_path = base_path / "channel_master.json"
    logger.info(f"save all public channels. path: {channel_path}")
    _save_to_json(channels, channel_path)

    logger.info("get all users.")
    users = get_all_users()
    users_path = base_path / "user_master.json"
    logger.info(f"save all users. path: {users_path}")
    _save_to_json(users, users_path)

    for channel in channels:
        channel_id = channel["id"]
        channel_name = channel["name"]
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
            replies = get_replies(channel_id, message)
            if replies:
                # '1638883139.000600' のように「.」が入るとファイル名として不適格なので「_」に置換
                thread_ts = message["thread_ts"].replace(".", "_")
                replies_path = messages_path / f"{thread_ts}.json"
                logger.info(f"save replies message. {channel_info}, path: {replies_path}")
                _save_to_json(replies, replies_path)  # type: ignore

    logger.info("get all message from slack finished")


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

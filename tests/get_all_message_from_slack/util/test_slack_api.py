from typing import Any, Dict
from unittest import mock

import pytest
from get_all_message_from_slack.util.slack_api import (
    get_all_public_channels,
    get_channel_id,
    get_channel_message,
    get_replies,
    get_user_name,
    post_message,
)
from slack_sdk.errors import SlackApiError


class ReturnValue:
    data = {}


def create_return_object(data: Dict[str, Any]):
    return_value = ReturnValue()
    return_value.data = data
    return return_value


class TestGetUserName:
    @pytest.fixture(autouse=True)
    def setUp(self):
        with mock.patch(
            "get_all_message_from_slack.util.slack_api.client.users_info",
        ) as mock_method:
            self.mock_method = mock_method
            yield

    def test_nomal_case(self):
        self.mock_method.return_value = {"user": {"real_name": "REAL_NAME"}}

        actual = get_user_name("USER_ID")
        expected = "REAL_NAME"

        assert actual == expected
        self.mock_method.assert_called_once_with(user="USER_ID")

    def test_not_exists_user_id(self):
        # APIにアクセスしたくないため、モックで例外を投げている
        # ユニットテストとしては意味がないが、仕様記載の意味で記載しておく
        self.mock_method.side_effect = SlackApiError("a", "b")

        with pytest.raises(SlackApiError):
            get_user_name("NOT_EXISTS_USER_ID")


class TestGetChannelId:
    @pytest.fixture(autouse=True)
    def setUp(self):

        self.return_value: Dict[str, Any] = {"response_metadata": {"next_cursor": ""}}

        with mock.patch(
            "get_all_message_from_slack.util.slack_api.client.conversations_list",
        ) as mock_method:
            self.mock_method = mock_method
            yield

    def test_nomal_case(self):
        self.mock_method.return_value = create_return_object(
            {
                "channels": [
                    {"name": "CHANNEL_NAME1", "id": "CHANNEL_ID1"},
                    {"name": "CHANNEL_NAME2", "id": "CHANNEL_ID2"},
                ]
            }
        )
        actual = get_channel_id("CHANNEL_NAME1")
        expected = "CHANNEL_ID1"

        assert actual == expected
        self.mock_method.assert_called_once_with()

    def test_not_exists_channel_name(self):
        self.mock_method.return_value = create_return_object(
            {
                "channels": [],
                "response_metadata": {"next_cursor": ""},
            }
        )
        with pytest.raises(ValueError):
            get_channel_id("CHANNEL_NAME")

    def test_next_cursor_true(self):
        self.mock_method.side_effect = [
            create_return_object(
                {
                    "channels": [],
                    "response_metadata": {"next_cursor": "NEXT_CURSOR"},
                }
            ),
            create_return_object(
                {
                    "channels": [{"name": "CHANNEL_NAME1", "id": "CHANNEL_ID1"}],
                    "response_metadata": {"next_cursor": ""},
                }
            ),
        ]
        actual = get_channel_id("CHANNEL_NAME1")
        expected = "CHANNEL_ID1"

        assert actual == expected
        self.mock_method.assert_has_calls(
            [
                mock.call(),
                mock.call(cursor="NEXT_CURSOR"),
            ]
        )


class TestPostMessage:
    @pytest.fixture(autouse=True)
    def setUp(self):
        class ReturnValue:
            data = {"ok": True, "ts": "1234567890.000002", "message": {}}

        with mock.patch(
            "get_all_message_from_slack.util.slack_api.client.chat_postMessage",
            return_value=ReturnValue(),
        ) as mock_method:
            self.mock_method = mock_method
            yield

    def test_all_args(self):
        actual = post_message(
            "CHANNEL_ID",
            "POST_MESSAGE",
            thread_ts="1234567890.000001",
            mention_users=["USER_ID_1", "USER_ID_2"],
        )
        expected = {"ok": True, "ts": "1234567890.000002", "message": {}}

        assert actual == expected
        self.mock_method.assert_called_once_with(
            channel="CHANNEL_ID",
            text="<@USER_ID_1> <@USER_ID_2>\nPOST_MESSAGE",
            thread_ts="1234567890.000001",
        )

    def test_required_args_only(self):
        actual = post_message("CHANNEL_ID", "POST_MESSAGE")
        expected = {"ok": True, "ts": "1234567890.000002", "message": {}}

        assert actual == expected
        self.mock_method.assert_called_once_with(
            channel="CHANNEL_ID", text="POST_MESSAGE", thread_ts=None
        )


class TestGetChannelMessage:
    @pytest.fixture(autouse=True)
    def setUp(self):
        with mock.patch(
            "get_all_message_from_slack.util.slack_api.client.conversations_history",
        ) as mock_method:
            self.mock_method = mock_method
            yield

    def test_not_has_more(self):
        messages = [
            {
                "ts": "1234567890.000001",
                "text": "TEXT_MESSAGE_1",
                "user": "USER_1",
            }
        ]
        self.mock_method.return_value = create_return_object(
            {
                "has_more": False,
                "messages": messages,
            }
        )
        actual = get_channel_message("CHANNEL_ID", float(1.23), float(4.56))
        expected = messages

        assert actual == expected
        self.mock_method.assert_called_once_with(
            channel="CHANNEL_ID", oldest=float(1.23), latest=float(4.56)
        )

    def test_has_more(self):
        messages_1 = [
            {
                "ts": "1234567890.000001",
                "text": "TEXT_MESSAGE_1",
                "user": "USER_1",
            }
        ]
        messages_2 = [
            {
                "ts": "1234567890.000002",
                "text": "TEXT_MESSAGE_2",
                "user": "USER_2",
            }
        ]
        self.mock_method.side_effect = [
            create_return_object(
                {
                    "has_more": True,
                    "messages": messages_1,
                    "response_metadata": {"next_cursor": "abcdefg"},
                }
            ),
            create_return_object(
                {
                    "has_more": False,
                    "messages": messages_2,
                }
            ),
        ]

        actual = get_channel_message("CHANNEL_ID", float(1.23), float(4.56))
        expected = messages_1 + messages_2

        assert actual == expected
        self.mock_method.assert_has_calls(
            [
                mock.call(channel="CHANNEL_ID", oldest=float(1.23), latest=float(4.56)),
                mock.call(
                    channel="CHANNEL_ID", oldest=float(1.23), latest=float(4.56), cursor="abcdefg"
                ),
            ]
        )


class TestGetReplies:
    @pytest.fixture(autouse=True)
    def setUp(self):
        with mock.patch(
            "get_all_message_from_slack.util.slack_api.client.conversations_replies",
        ) as mock_method:
            self.mock_method = mock_method
            yield

    def test_not_exists_thread_ts_in_message(self):
        actual = get_replies("CHANNEL_ID", {})
        expected = []

        assert actual == expected
        self.mock_method.assert_not_called()

    def test_exists_thread_ts_in_message_and_not_has_more(self):
        arg_message = {
            "thread_ts": "1234567890.000001",
            "ts": "1234567890.000001",
            "text": "TEXT_MESSAGE_1",
            "user": "USER_1",
        }
        messages = [
            {
                "ts": "1234567890.000010",
                "text": "TEXT_MESSAGE_10",
                "user": "USER_10",
            }
        ]
        self.mock_method.return_value = create_return_object(
            {
                "has_more": False,
                "messages": messages,
            }
        )
        actual = get_replies("CHANNEL_ID", arg_message)
        expected = messages

        assert actual == expected
        self.mock_method.assert_called_once_with(channel="CHANNEL_ID", ts="1234567890.000001")

    def test_exists_thread_ts_in_message_and_has_more(self):
        arg_message = {
            "thread_ts": "1234567890.000001",
            "ts": "1234567890.000001",
            "text": "TEXT_MESSAGE_1",
            "user": "USER_1",
        }

        messages_1 = [
            {
                "ts": "1234567890.000010",
                "text": "TEXT_MESSAGE_10",
                "user": "USER_1",
            }
        ]
        messages_2 = [
            {
                "ts": "1234567890.000020",
                "text": "TEXT_MESSAGE_20",
                "user": "USER_2",
            }
        ]
        self.mock_method.side_effect = [
            create_return_object(
                {
                    "has_more": True,
                    "messages": messages_1,
                    "response_metadata": {"next_cursor": "abcdefg"},
                }
            ),
            create_return_object(
                {
                    "has_more": False,
                    "messages": messages_2,
                }
            ),
        ]

        actual = get_replies("CHANNEL_ID", arg_message)
        expected = messages_1 + messages_2

        assert actual == expected
        self.mock_method.assert_has_calls(
            [
                mock.call(channel="CHANNEL_ID", ts="1234567890.000001"),
                mock.call(channel="CHANNEL_ID", ts="1234567890.000001", cursor="abcdefg"),
            ]
        )


class TestGetAllPublicChannels:
    @pytest.fixture(autouse=True)
    def setUp(self):

        with mock.patch(
            "get_all_message_from_slack.util.slack_api.client.conversations_list",
        ) as mock_method:
            self.mock_method = mock_method
            yield

    def test_nomal_case(self):
        self.mock_method.return_value = create_return_object(
            {
                "channels": [
                    {"name": "CHANNEL_NAME1", "id": "CHANNEL_ID1"},
                    {"name": "CHANNEL_NAME2", "id": "CHANNEL_ID2"},
                ],
                "response_metadata": {"next_cursor": ""},
            }
        )
        actual = get_all_public_channels()
        expected = [
            {"name": "CHANNEL_NAME1", "id": "CHANNEL_ID1"},
            {"name": "CHANNEL_NAME2", "id": "CHANNEL_ID2"},
        ]

        assert actual == expected
        self.mock_method.assert_called_once_with(**{"type:": "public_channel"})

    def test_next_cursor_true(self):
        self.mock_method.side_effect = [
            create_return_object(
                {
                    "channels": [{"name": "CHANNEL_NAME1", "id": "CHANNEL_ID1"}],
                    "response_metadata": {"next_cursor": "NEXT_CURSOR"},
                }
            ),
            create_return_object(
                {
                    "channels": [{"name": "CHANNEL_NAME2", "id": "CHANNEL_ID2"}],
                    "response_metadata": {"next_cursor": ""},
                }
            ),
        ]
        actual = get_all_public_channels()
        expected = [
            {"name": "CHANNEL_NAME1", "id": "CHANNEL_ID1"},
            {"name": "CHANNEL_NAME2", "id": "CHANNEL_ID2"},
        ]

        assert actual == expected
        # self.mock_method.assert_called_once_with(**{"type:": "public_channel"})
        self.mock_method.assert_has_calls(
            [
                mock.call(**{"type:": "public_channel"}),
                mock.call(**{"type:": "public_channel", "cursor": "NEXT_CURSOR"}),
            ]
        )

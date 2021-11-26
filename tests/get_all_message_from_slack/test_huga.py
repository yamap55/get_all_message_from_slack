from get_all_message_from_slack.huga import Huga


class TestHuga:
    def test_huga(self):
        assert Huga().piyo() == "piyo"

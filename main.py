"""main"""
from logging import config

from get_all_message_from_slack.huga import Huga

config.fileConfig("logging.conf", disable_existing_loggers=False)

if __name__ == "__main__":
    Huga().piyo()

"""main"""
from logging import config, getLogger

import get_all_message_from_slack.settings as settings

config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = getLogger(__name__)
client = settings.client

def main():
    pass

if __name__ == "__main__":
    main()

class Huga:
    """
    Huga class
    """

    def piyo(self) -> str:
        """return piyo"""
        logger.info("piyo")
        return "piyo"

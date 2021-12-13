"""ログ設定"""

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "%(levelname)-8s %(asctime)s %(module)s %(process)s %(pathname)s:%(lineno)d %(message)s"  # noqa: E501
        },
    },
    "handlers": {
        "console_handler": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        # "file_handler": {
        #     "level": "DEBUG",
        #     "formatter": "standard",
        #     "class": "logging.handlers.TimedRotatingFileHandler",
        #     "filename": "logs/python.log",
        #     "when": "MIDNIGHT",
        #     "interval": 1,
        #     "backupCount": 30,
        #     "encoding": "utf8",
        # },
    },
    "loggers": {
        "": {"handlers": ["console_handler"], "level": "INFO", "propagate": False},
        "get_all_message_from_slack": {
            "handlers": ["console_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
        "__main__": {
            "handlers": ["console_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

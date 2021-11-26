"""application settings"""
import locale
import os

from slack_sdk import WebClient

locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
client = WebClient(token=os.environ["SLACK_TOKEN"])

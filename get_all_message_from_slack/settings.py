"""application settings"""
import os

from slack_sdk.web.client import WebClient

client = WebClient(token=os.environ["SLACK_TOKEN"])

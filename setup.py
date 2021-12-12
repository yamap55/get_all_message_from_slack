"""モジュールをインストールし、コマンドとして使用できるようにする setup.py."""
from setuptools import find_packages, setup

setup(
    name="get_all_message_from_slack",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["slack-sdk"],
    # コマンドが実行されたときのエントリーポイント.
    entry_points={
        "console_scripts": ["get_all_message_from_slack=get_all_message_from_slack.main:main"]
    },
)

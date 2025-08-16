import os
import requests
from notification_enum import NOTIFICATION_ENUM

class Notification:
    """
        Notification is optional, dont need to show in log if not defined
    """
    def __init__(self, webhook_url:str | None = None) -> None:
        if webhook_url is None:
            raise ValueError("Webhook URL must be provided for notifications.")
        self.webhook_url = webhook_url

    def send_notification(self, message: str) -> None:
        if os.getenv("NOTIFICATION_SERVICE") is None or os.getenv("WEBHOOK_URL") is None:
            print("Notification service or webhook URL is not set. Skipping notification.")
            return

        if os.getenv("NOTIFICATION_SERVICE") is not None and not NOTIFICATION_ENUM.is_valid(os.getenv("NOTIFICATION_SERVICE", "")):
            print(f"Notification service {os.getenv('NOTIFICATION_SERVICE')} is not supported. Please use 'apprise' or 'discord'.")
            return

        payload = {}
        headers = {}
        if os.getenv("NOTIFICATION_SERVICE") == NOTIFICATION_ENUM.APPRISE:
            # apprise only support plain text
            payload = {
                "body": message,
                "tags": "all" if os.getenv("APPRISE_TAG") is None else os.getenv("APPRISE_TAG")
            }
            headers = {}

        elif os.getenv("NOTIFICATION_SERVICE") == NOTIFICATION_ENUM.DISCORD:
            # Only vanilla Discord Webhook support embeds
            payload = {
                "embeds": [
                    {
                        "title": message,
                        "color": 65280
                    }
                ]
            }
            headers = {
                "Content-Type": "application/json"
            }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send notification: {e}")
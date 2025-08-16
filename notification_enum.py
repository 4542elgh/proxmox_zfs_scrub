from enum import Enum

class NOTIFICATION_ENUM(Enum):
    APPRISE = "apprise"
    DISCORD = "discord"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        Check if the provided value is a valid notification service.
        """
        return value.lower() in [service.value for service in cls]
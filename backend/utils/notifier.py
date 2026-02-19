from utils.logger import get_logger

logger = get_logger("Notifier")


def notify_guardians(message: str):
    logger.warning(f"Guardian notification sent: {message}")


def notify_authorities(message: str):
    logger.critical(f"Authority notification sent: {message}")

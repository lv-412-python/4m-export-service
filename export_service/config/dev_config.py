"""Development config."""
from export_service.config.base_config import Config


class DevelopmentConfig(Config):  # pylint: disable=too-few-public-methods
    """Development config."""
    DEVELOPMENT = True
    DEBUG = True

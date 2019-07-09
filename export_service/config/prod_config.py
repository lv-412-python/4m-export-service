"""Production config."""
from export_service.config.base_config import Config


class ProductionConfig(Config):  # pylint: disable=too-few-public-methods
    """Production config."""
    DEBUG = False

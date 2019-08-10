"""Config."""


class Config:
    """
    Implementation of Configuration class.
    """
    DEBUG = False
    TESTING = False
    FORM_SERVICE_URL = "http://forms-service:5050/form"
    GROUPS_SERVICE_URL = "http://groups-service:5050/group"
    ANSWERS_SERVICE_URL = "http://answers-service:5050/answers"
    USERS_SERVICE_URL = "http://users-service:5050/users"

from faker import Faker

fake = Faker()


def create_config_overrides(**kwargs: str | int) -> dict[str, str | int]:
    """
    Generates a dictionary of configuration overrides.
    """
    defaults: dict[str, str | int] = {
        "LOG_LEVEL": "INFO",
        "ALLURE_API_TOKEN": fake.password(length=32),
        "HOST": "127.0.0.1",
        "PORT": fake.port_number(),
        "MCP_MODE": "http",
    }
    defaults.update(kwargs)
    return defaults

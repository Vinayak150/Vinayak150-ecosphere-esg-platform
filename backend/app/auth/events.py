from app.core.events import event_bus

AUTH_USER_LOGGED_IN = "auth.user.logged_in"
AUTH_USER_LOGGED_OUT = "auth.user.logged_out"


def publish_user_logged_in(payload: dict[str, str]) -> None:
    event_bus.publish(AUTH_USER_LOGGED_IN, payload)


def publish_user_logged_out(payload: dict[str, str]) -> None:
    event_bus.publish(AUTH_USER_LOGGED_OUT, payload)

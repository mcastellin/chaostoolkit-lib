from functools import wraps
from itertools import count
from typing import Any, Callable

from logzero import logger

from chaoslib.types import Journal

counter = None


def initcounter(f: Callable) -> Callable:
    @wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> None:
        global counter
        counter = count()
        f(*args, **kwargs)

    return wrapped


def keepcount(f: Callable) -> Callable:
    @wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> None:
        next(counter)
        f(*args, **kwargs)

    return wrapped


@keepcount
def after_activity_control(**kwargs: Any) -> None:
    logger.info("Activity is called")


@initcounter
def configure_control(**kwargs: Any) -> None:
    logger.info("configure is called")


def after_experiment_control(state: Journal, **kwargs: Any) -> None:
    state["counted_activities"] = next(counter)

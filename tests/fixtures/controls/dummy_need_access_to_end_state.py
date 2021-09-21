from typing import Any

from chaoslib.types import Experiment, Journal


def after_hypothesis_control(
    context: Experiment, state: Journal, **kwargs: Any
) -> None:
    state["after_hypothesis_control"] = True


def after_experiment_control(
    context: Experiment, state: Journal, **kwargs: Any
) -> None:
    state["after_experiment_control"] = True

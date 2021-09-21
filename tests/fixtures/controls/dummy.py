from typing import Any, Dict, List

from chaoslib.types import (
    Activity,
    Configuration,
    Experiment,
    Hypothesis,
    Journal,
    Run,
    Secrets,
    Settings,
)


def configure_control(
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    settings: Settings,
) -> None:
    if configuration:
        experiment["control-value"] = configuration.get("dummy-key", "default")
    elif settings:
        experiment["control-value"] = settings.get("dummy-key", "default")


def cleanup_control() -> None:
    pass


def before_experiment_control(context: Experiment, **kwargs: Any) -> None:
    context["before_experiment_control"] = True


def after_experiment_control(
    context: Experiment, state: Journal, **kwargs: Any
) -> None:
    context["after_experiment_control"] = True
    state["after_experiment_control"] = True


def before_hypothesis_control(context: Hypothesis, **kwargs: Any) -> None:
    context["before_hypothesis_control"] = True


def after_hypothesis_control(
    context: Hypothesis, state: Dict[str, Any], **kwargs: Any
) -> None:
    context["after_hypothesis_control"] = True
    state["after_hypothesis_control"] = True


def before_method_control(context: Experiment, **kwargs: Any) -> None:
    context["before_method_control"] = True


def after_method_control(context: Experiment, state: List[Run], **kwargs: Any) -> None:
    context["after_method_control"] = True
    state.append("after_method_control")


def before_rollback_control(context: Experiment, **kwargs: Any) -> None:
    context["before_rollback_control"] = True


def after_rollback_control(
    context: Experiment, state: List[Run], **kwargs: Any
) -> None:
    context["after_rollback_control"] = True
    state.append("after_rollback_control")


def before_activity_control(context: Activity, **kwargs: Any) -> None:
    context["before_activity_control"] = True


def after_activity_control(context: Activity, state: Run, **kwargs: Any) -> None:
    context["after_activity_control"] = True
    state["after_activity_control"] = True

from fixtures import experiments, run_handlers

from chaoslib.experiment import run_experiment
from chaoslib.run import EventHandlerRegistry, RunEventHandler
from chaoslib.types import Experiment, Journal, Schedule, Strategy


def test_run_ssh_before_method_only() -> None:
    experiment = experiments.SimpleExperiment.copy()
    journal = run_experiment(experiment, strategy=Strategy.BEFORE_METHOD)
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is None


def test_run_ssh_after_method_only() -> None:
    experiment = experiments.SimpleExperiment.copy()
    journal = run_experiment(experiment, strategy=Strategy.AFTER_METHOD)
    assert journal is not None
    assert journal["steady_states"]["before"] is None
    assert journal["steady_states"]["after"] is not None


def test_run_ssh_default_strategy() -> None:
    experiment = experiments.SimpleExperiment.copy()
    journal = run_experiment(experiment, strategy=Strategy.DEFAULT)
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is not None


def test_run_ssh_during_method_only() -> None:
    experiment = experiments.SimpleExperiment.copy()
    journal = run_experiment(experiment, strategy=Strategy.DURING_METHOD)
    assert journal is not None
    assert journal["steady_states"]["before"] is None
    assert journal["steady_states"]["after"] is None
    assert journal["steady_states"]["during"] is not None


def test_run_ssh_continuous() -> None:
    experiment = experiments.SimpleExperiment.copy()
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1),
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is not None
    assert journal["steady_states"]["during"] is not None


def test_exit_continuous_ssh_continuous_when_experiment_is_interrupted() -> None:
    handlers_called = []

    class Handler(RunEventHandler):
        def started(self, experiment: Experiment, journal: Journal) -> None:
            handlers_called.append("started")

        def interrupted(self, experiment: Experiment, journal: Journal) -> None:
            handlers_called.append("interrupted")

    experiment = experiments.SimpleExperimentWithInterruption.copy()
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1),
        event_handlers=[Handler()],
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is None
    assert journal["steady_states"]["during"] is not None
    assert journal["deviated"] is False
    assert journal["status"] == "interrupted"
    assert sorted(handlers_called) == ["interrupted", "started"]


def test_exit_continuous_ssh_continuous_when_experiment_is_exited() -> None:
    handlers_called = []

    class Handler(RunEventHandler):
        def started(self, experiment: Experiment, journal: Journal) -> None:
            handlers_called.append("started")

        def interrupted(self, experiment: Experiment, journal: Journal) -> None:
            handlers_called.append("interrupted")

    experiment = experiments.SimpleExperimentWithExit.copy()
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1),
        event_handlers=[Handler()],
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is None
    assert journal["steady_states"]["during"] is not None
    assert journal["deviated"] is False
    assert journal["status"] == "interrupted"
    assert sorted(handlers_called) == ["started"]


def test_exit_continuous_ssh_continuous_when_activity_raises_unknown_exception() -> None:  # Noqa
    experiment = experiments.SimpleExperimentWithException.copy()
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1),
        settings={"runtime": {"rollbacks": {"strategy": "always"}}},
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is not None
    assert journal["steady_states"]["during"] is not None
    assert journal["deviated"] is False
    assert journal["status"] == "completed"
    assert len(journal["run"]) == 2
    assert journal["run"][-1]["status"] == "failed"
    assert "oops" in journal["run"][-1]["exception"][-1]


def test_exit_immediately_when_continuous_ssh_fails_and_failfast() -> None:
    experiment = experiments.SimpleExperimentWithSSHFailingAtSomePoint.copy()
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1, fail_fast=True),
        settings={"runtime": {"rollbacks": {"strategy": "always"}}},
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is not None
    assert journal["steady_states"]["during"] is not None
    assert journal["status"] == "failed"
    assert journal["deviated"] is True
    assert len(journal["run"]) == 1


def test_do_not_exit_when_continuous_ssh_fails_and_no_failfast() -> None:
    experiment = experiments.SimpleExperimentWithSSHFailingAtSomePoint.copy()
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1, fail_fast=False),
        settings={"runtime": {"rollbacks": {"strategy": "always"}}},
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is not None
    assert journal["steady_states"]["during"] is not None
    assert journal["status"] == "failed"
    assert journal["deviated"] is True
    assert len(journal["run"]) == 2


def test_exit_immediately_when_continuous_ssh_fails_and_failfast_when_background_activity() -> None:  # noqa E501
    experiment = (
        experiments.SimpleExperimentWithSSHFailingAtSomePointWithBackgroundActivity.copy()  # noqa E501
    )
    journal = run_experiment(
        experiment,
        strategy=Strategy.CONTINUOUS,
        schedule=Schedule(continuous_hypothesis_frequency=0.1, fail_fast=True),
        settings={"runtime": {"rollbacks": {"strategy": "always"}}},
    )
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is not None
    assert journal["steady_states"]["during"] is not None
    assert journal["status"] == "failed"
    assert journal["deviated"] is True
    assert len(journal["run"]) == 2


def test_run_handler_is_called_on_each_handler() -> None:
    registry = EventHandlerRegistry()
    h = run_handlers.FullRunEventHandler()
    registry.register(h)

    registry.started({}, {})
    registry.finish({})
    registry.interrupted({}, {})
    registry.signal_exit()
    registry.start_continuous_hypothesis(0)
    registry.continuous_hypothesis_iteration(0, None)
    registry.continuous_hypothesis_completed({}, {})
    registry.start_method({})
    registry.method_completed({}, None)
    registry.start_rollbacks({})
    registry.rollbacks_completed({}, {})
    registry.start_hypothesis_before({})
    registry.hypothesis_before_completed({}, {}, {})
    registry.start_hypothesis_after({})
    registry.hypothesis_after_completed({}, {}, {})
    registry.start_cooldown(0)
    registry.cooldown_completed()

    assert h.calls == [
        "started",
        "finish",
        "interrupted",
        "signal_exit",
        "start_continuous_hypothesis",
        "continuous_hypothesis_iteration",
        "continuous_hypothesis_completed",
        "start_method",
        "method_completed",
        "start_rollbacks",
        "rollbacks_completed",
        "start_hypothesis_before",
        "hypothesis_before_completed",
        "start_hypothesis_after",
        "hypothesis_after_completed",
        "start_cooldown",
        "cooldown_completed",
    ]


def test_exceptions_does_not_stop_handler_registry() -> None:
    registry = EventHandlerRegistry()
    registry.register(run_handlers.FullExceptionRunEventHandler())
    h = run_handlers.FullRunEventHandler()
    registry.register(h)

    registry.started({}, {})
    registry.finish({})
    registry.interrupted({}, {})
    registry.signal_exit()
    registry.start_continuous_hypothesis(0)
    registry.continuous_hypothesis_iteration(0, None)
    registry.continuous_hypothesis_completed({}, {})
    registry.start_method({})
    registry.method_completed({}, None)
    registry.start_rollbacks({})
    registry.rollbacks_completed({}, {})
    registry.start_hypothesis_before({})
    registry.hypothesis_before_completed({}, {}, {})
    registry.start_hypothesis_after({})
    registry.hypothesis_after_completed({}, {}, {})
    registry.start_cooldown(0)
    registry.cooldown_completed()

    assert h.calls == [
        "started",
        "finish",
        "interrupted",
        "signal_exit",
        "start_continuous_hypothesis",
        "continuous_hypothesis_iteration",
        "continuous_hypothesis_completed",
        "start_method",
        "method_completed",
        "start_rollbacks",
        "rollbacks_completed",
        "start_hypothesis_before",
        "hypothesis_before_completed",
        "start_hypothesis_after",
        "hypothesis_after_completed",
        "start_cooldown",
        "cooldown_completed",
    ]


def test_do_not_ruin_method_on_failing_before_ssh() -> None:
    experiment = experiments.SimpleExperimentWithFailingHypothesis.copy()
    journal = run_experiment(experiment, strategy=Strategy.DEFAULT)
    assert journal is not None
    assert journal["steady_states"]["before"] is not None
    assert journal["steady_states"]["after"] is None
    assert journal["steady_states"]["during"] == []
    assert journal["status"] == "failed"
    assert journal["deviated"] is False
    assert len(journal["run"]) == 0

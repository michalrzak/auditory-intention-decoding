from typing import Callable

import sys
import io

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.view.cli_view import CLIView


def __capture_console_output(func: Callable[[], None]) -> str:
    # redirect output from console
    target_output = io.StringIO()
    sys.stdout = target_output
    func()
    sys.stdout = sys.__stdout__

    return target_output.getvalue()


def test_update_new_prompt():
    # initialize object
    cli_view = CLIView()
    new_prompt = "New prompt!"

    outputted = __capture_console_output(lambda: cli_view.update(new_prompt, EModelUpdateIdentifier.NEW_PROMPT))

    assert outputted is not None
    assert len(outputted) != 0
    assert new_prompt in outputted


def test_update_change_experiment_state():
    cli_view = CLIView()
    new_state = EExperimentState.RESTING_STATE

    outputted = __capture_console_output(
        lambda: cli_view.update(new_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED))

    assert outputted is not None
    assert len(outputted) != 0

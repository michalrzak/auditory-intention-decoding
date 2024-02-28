from typing import Callable

import sys
import io
import mockito

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.stimulus import Stimulus
from auditory_stimulation.view.cli_view import CLIView
from tests.auditory_stimulus.stimulus_test_helpers import get_mock_audio_player, get_mock_audio


def __capture_console_output(func: Callable[[], None]) -> str:
    # redirect output from console
    target_output = io.StringIO()
    sys.stdout = target_output
    func()
    sys.stdout = sys.__stdout__

    return target_output.getvalue()


def test_update_new_prompt():
    # initialize object
    cli_view = CLIView(get_mock_audio_player())

    new_prompt = "new prompt"
    new_audio = get_mock_audio(1000, 100)

    new_stimulus = mockito.mock(Stimulus)
    new_stimulus.audio = new_audio
    new_stimulus.prompt = new_prompt

    outputted = __capture_console_output(lambda: cli_view.update(new_stimulus, EModelUpdateIdentifier.NEW_STIMULUS))

    assert outputted is not None
    assert len(outputted) != 0
    assert new_prompt in outputted


def test_update_change_experiment_state():
    cli_view = CLIView(get_mock_audio_player())
    new_state = EExperimentState.RESTING_STATE_EYES_CLOSED

    outputted = __capture_console_output(
        lambda: cli_view.update(new_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED))

    assert outputted is not None
    assert len(outputted) != 0

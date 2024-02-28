import mockito
from mockito import verify, when, ANY

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.stimulus import Stimulus
from auditory_stimulation.view.view import AView
from tests.auditory_stimulus.stimulus_test_helpers import get_mock_audio


def test_new_stimulus():
    model = Model()

    new_prompt = "new prompt"
    new_audio = get_mock_audio(1000, 100)

    new_stimulus = mockito.mock(Stimulus)
    new_stimulus.audio = new_audio
    new_stimulus.prompt = new_prompt

    model.new_stimulus(new_stimulus)
    changed_prompt = model.current_prompt
    changed_audio = model.current_audio

    assert changed_prompt is not None
    assert changed_prompt == new_prompt
    assert changed_audio is not None
    assert changed_audio == new_audio


def test_change_experiment_state():
    model = Model()
    new_experiment_state = EExperimentState.RESTING_STATE_EYES_CLOSED

    previous_value = model.experiment_state
    model.change_experiment_state(new_experiment_state)
    changed_value = model.experiment_state

    assert changed_value is not None
    assert changed_value != previous_value
    assert changed_value == new_experiment_state


def test_register_view_should_not_fail():
    model = Model()
    mock_view = mockito.mock(AView)

    model.register(mock_view)


def test_register_view_and_new_stimulus_should_get_updated():
    model = Model()
    new_prompt = "new prompt"
    new_audio = get_mock_audio(1000, 100)

    new_stimulus = mockito.mock(Stimulus)
    new_stimulus.audio = new_audio
    new_stimulus.prompt = new_prompt

    mock_view = mockito.mock(AView)
    when(mock_view).update(ANY, ANY).thenReturn(None)

    model.register(mock_view)
    model.new_stimulus(new_stimulus)

    verify(mock_view).update(new_stimulus, EModelUpdateIdentifier.NEW_STIMULUS)


def test_register_view_and_change_state_should_get_updated():
    model = Model()
    new_experiment_state = EExperimentState.RESTING_STATE_EYES_CLOSED

    mock_view = mockito.mock(AView)
    when(mock_view).update(ANY, ANY).thenReturn(None)

    model.register(mock_view)

    model.change_experiment_state(new_experiment_state)

    verify(mock_view).update(new_experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)

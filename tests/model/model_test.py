import mockito
import pytest
from mockito import verify, when, ANY

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model, AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus
from auditory_stimulation.view.view import AView
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def create_model() -> Model:
    raw_stimuli = [mockito.mock(CreatedStimulus)]
    return Model(raw_stimuli)


def mock_observer() -> AObserver:
    observer = mockito.mock(AObserver)
    when(observer).update(ANY, ANY).thenReturn(None)
    return observer


def test_new_stimulus():
    model = create_model()

    new_prompt = "new prompt"
    new_audio = get_mock_audio(1000, 100)

    new_stimulus = mockito.mock(CreatedStimulus)
    new_stimulus.audio = new_audio
    new_stimulus.prompt = new_prompt

    model.present_stimulus(new_stimulus)
    changed_prompt = model.current_prompt
    changed_audio = model.current_audio

    assert changed_prompt is not None
    assert changed_prompt == new_prompt
    assert changed_audio is not None
    assert changed_audio == new_audio


def test_change_experiment_state():
    model = create_model()
    new_experiment_state = EExperimentState.RESTING_STATE_EYES_CLOSED

    previous_value = model.experiment_state
    model.change_experiment_state(new_experiment_state)
    changed_value = model.experiment_state

    assert changed_value is not None
    assert changed_value != previous_value
    assert changed_value == new_experiment_state


def test_register_view_should_not_fail():
    model = create_model()
    mock_view = mockito.mock(AView)

    model.register(mock_view)


def test_register_view_and_new_stimulus_should_get_updated():
    model = create_model()
    new_prompt = "new prompt"
    new_audio = get_mock_audio(1000, 100)

    new_stimulus = mockito.mock(CreatedStimulus)
    new_stimulus.array = new_audio
    new_stimulus.prompt = new_prompt

    mock_view = mockito.mock(AView)
    when(mock_view).update(ANY, ANY).thenReturn(None)

    model.register(mock_view)
    model.present_stimulus(new_stimulus)

    verify(mock_view).update(new_stimulus, EModelUpdateIdentifier.NEW_STIMULUS)


@pytest.mark.parametrize("experiment_state", EExperimentState)
def test_register_observer_and_change_state_should_get_updated(experiment_state: EExperimentState):
    model = create_model()

    # make sure the experiment state can actually change (is not what it was before changing it)
    if model.experiment_state == experiment_state:
        assert experiment_state != EExperimentState.EXPERIMENT
        model.change_experiment_state(EExperimentState.EXPERIMENT)

    observer = mock_observer()
    model.register(observer)

    model.change_experiment_state(experiment_state)

    verify(observer).update(experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)


def test_register_observer_new_stimulus_twice_should_get_updated():
    model = create_model()
    stimulus = mockito.mock(CreatedStimulus)

    observer = mock_observer()
    model.register(observer)
    model.present_stimulus(stimulus)

    verify(observer, times=1).update(stimulus, EModelUpdateIdentifier.NEW_STIMULUS)

    model.present_stimulus(stimulus)
    verify(observer, times=2).update(stimulus, EModelUpdateIdentifier.NEW_STIMULUS)


def test_register_observers_with_different_priorities_should_be_called_in_correct_order():
    model = create_model()

    execution_order = []

    observer1 = mock_observer()
    when(observer1).update(ANY, ANY).thenAnswer(lambda _, __: execution_order.append("observer1"))
    observer2 = mock_observer()
    when(observer2).update(ANY, ANY).thenAnswer(lambda _, __: execution_order.append("observer2"))

    model.register(observer1, priority=1)
    model.register(observer2, priority=2)

    experiment_state = EExperimentState.EXPERIMENT_INTRODUCTION
    model.change_experiment_state(experiment_state)

    assert execution_order[0] == "observer1" and execution_order[1] == "observer2"

    verify(observer1, times=1).update(experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)
    verify(observer2, times=1).update(experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)

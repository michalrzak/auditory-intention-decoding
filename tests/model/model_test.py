import mockito
from mockito import verify, when, ANY

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.view.view import AView


def test_new_prompt():
    model = Model()
    new_prompt = "new prompt"

    previous_value = model.current_prompt
    model.new_prompt(new_prompt)
    changed_value = model.current_prompt

    assert changed_value is not None
    assert changed_value != previous_value
    assert changed_value == new_prompt


def test_change_experiment_state():
    model = Model()
    new_experiment_state = EExperimentState.RESTING_STATE

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


def test_register_view_and_new_prompt_should_get_updated():
    model = Model()
    new_prompt = "new prompt"

    mock_view = mockito.mock(AView)
    when(mock_view).update(ANY, ANY).thenReturn(None)

    model.register(mock_view)

    model.new_prompt(new_prompt)

    verify(mock_view).update(new_prompt, EModelUpdateIdentifier.NEW_PROMPT)

def test_register_view_and_change_state_should_get_updated():
    model = Model()
    new_experiment_state = EExperimentState.RESTING_STATE

    mock_view = mockito.mock(AView)
    when(mock_view).update(ANY, ANY).thenReturn(None)

    model.register(mock_view)

    model.change_experiment_state(new_experiment_state)

    verify(mock_view).update(new_experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)

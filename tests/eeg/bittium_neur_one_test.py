import mockito
import pytest
from mockito import when, verify
from mockito.matchers import ANY

from auditory_stimulation.eeg.bittium_neur_one import BittiumTriggerSender, IParallelPort
from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


@pytest.mark.parametrize("update_identifier", [EModelUpdateIdentifier.NEW_STIMULUS, EModelUpdateIdentifier.NEW_PRIMER])
def test_bittium_trigger_sender_update_easy_valid_call(update_identifier: EModelUpdateIdentifier):
    parallel_port = mockito.mock(IParallelPort)
    when(parallel_port).setData(ANY).thenReturn(None)

    trigger_sender = BittiumTriggerSender(parallel_port, trigger_duration_s=0)

    sample_data = "sample_data"
    trigger_sender.update(data=sample_data, identifier=update_identifier)
    verify(parallel_port, times=1).setData(ETrigger.get_trigger(sample_data, update_identifier).value)
    verify(parallel_port, times=1).setData(0)


@pytest.mark.parametrize("experiment_state", EExperimentState)
def test_bittium_trigger_sender_update_experiment_state_changed_valid_call(experiment_state: EExperimentState):
    parallel_port = mockito.mock(IParallelPort)
    when(parallel_port).setData(ANY).thenReturn(None)

    trigger_sender = BittiumTriggerSender(parallel_port, trigger_duration_s=0)

    trigger_sender.update(data=experiment_state, identifier=EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)
    verify(parallel_port, times=1).setData(
        ETrigger.get_trigger(experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED).value)
    verify(parallel_port, times=1).setData(0)

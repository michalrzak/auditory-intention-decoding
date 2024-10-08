import threading
from typing import Any

import mockito
import pytest
from mockito import when, verify
from mockito.matchers import ANY

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.raw_tagger import RawTagger
from auditory_stimulation.eeg.bittium_neur_one import BittiumTriggerSender, IParallelPort
from auditory_stimulation.eeg.common import ETrigger, get_trigger
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import AStimulus

MOCK_AUDIO = mockito.mock(Audio)
MOCK_AUDIO.secs = 0.3
MOCK_STIMULUS = mockito.mock(AStimulus)
MOCK_STIMULUS.time_stamps = [[0.1, 0.2]]
MOCK_STIMULUS.audio = MOCK_AUDIO
MOCK_STIMULUS.used_tagger = mockito.mock(RawTagger)

THREAD_TIMOUT = 0


def wait_for_threads(previous_thread_count: int) -> None:
    # wait for all threads to finish
    while threading.active_count() != previous_thread_count:
        ...


@pytest.mark.parametrize(["update_identifier", "data"],
                         [[EModelUpdateIdentifier.NEW_PRIMER, "sample_data"]])
def test_bittium_trigger_sender_update_easy_valid_call(update_identifier: EModelUpdateIdentifier, data: Any):
    parallel_port = mockito.mock(IParallelPort)
    when(parallel_port).setData(ANY).thenReturn(None)

    trigger_sender = BittiumTriggerSender(THREAD_TIMOUT, parallel_port, trigger_duration_s=0)

    previous_count = threading.active_count()
    with trigger_sender.start() as ts:
        ts.update(data=data, identifier=update_identifier)
    wait_for_threads(previous_count)

    verify(parallel_port, times=1).setData(get_trigger(data, update_identifier))
    verify(parallel_port, times=1).setData(0)


@pytest.mark.parametrize("experiment_state", EExperimentState)
def test_bittium_trigger_sender_update_experiment_state_changed_valid_call(experiment_state: EExperimentState):
    parallel_port = mockito.mock(IParallelPort)
    when(parallel_port).setData(ANY).thenReturn(None)

    previous_count = threading.active_count()

    trigger_sender = BittiumTriggerSender(THREAD_TIMOUT, parallel_port, trigger_duration_s=0)
    with trigger_sender.start() as ts:
        ts.update(data=experiment_state, identifier=EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)
    wait_for_threads(previous_count)

    verify(parallel_port, times=1).setData(
        get_trigger(experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED))
    verify(parallel_port, times=1).setData(0)


def test_bittium_trigger_sender_update_new_stimulus_threads():
    parallel_port = mockito.mock(IParallelPort)
    when(parallel_port).setData(ANY).thenReturn(None)

    trigger_sender = BittiumTriggerSender(THREAD_TIMOUT, parallel_port, trigger_duration_s=0)

    data = MOCK_STIMULUS
    update_identifier = EModelUpdateIdentifier.NEW_STIMULUS

    previous_count = threading.active_count()
    with trigger_sender.start() as ts:
        ts.update(data=data, identifier=update_identifier)
    wait_for_threads(previous_count)

    verify(parallel_port, times=1).setData(get_trigger(data, update_identifier))
    verify(parallel_port, times=1).setData(ETrigger.END_STIMULUS.value)
    verify(parallel_port, times=len(data.time_stamps)).setData(ETrigger.OPTION_START.value)
    verify(parallel_port, times=len(data.time_stamps)).setData(ETrigger.OPTION_END.value)
    verify(parallel_port, times=1 + 1 + 2 * len(data.time_stamps)).setData(0)

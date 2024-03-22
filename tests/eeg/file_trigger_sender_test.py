import csv
import pathlib
from datetime import datetime

import mockito
import pytest

from auditory_stimulation.audio import Audio
from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.eeg.file_trigger_sender import FileTriggerSender
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus

THREAD_TIMOUT = 0

MOCK_AUDIO = mockito.mock(Audio)
MOCK_AUDIO.secs = 3
MOCK_CREATED_STIMULUS = mockito.mock(CreatedStimulus)
MOCK_CREATED_STIMULUS.time_stamps = [[1, 2]]
MOCK_CREATED_STIMULUS.audio = MOCK_AUDIO


def target_file(tmp_path):
    return pathlib.Path(tmp_path) / "trigger_file.csv"


def test_file_trigger_sender_consruct_valid_call(tmp_path):
    trigger_sender = FileTriggerSender(THREAD_TIMOUT, target_file(tmp_path))


@pytest.mark.parametrize("thread_timout", [-1, -10, -0.001])
def test_file_trigger_sender_thread_timout_bellow_0_should_fail(thread_timout, tmp_path):
    with pytest.raises(ValueError):
        trigger_sender = FileTriggerSender(thread_timout, target_file(tmp_path))


@pytest.mark.parametrize("data", EExperimentState)
def test_file_trigger_sender_send_trigger_experiment_state_changed_valid_call(data, tmp_path):
    epsilon = 3

    trigger_sender = FileTriggerSender(THREAD_TIMOUT, target_file(tmp_path))

    data = EExperimentState.INTRODUCTION
    identifier = EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED

    with trigger_sender.start() as ts:
        send_ts = datetime.timestamp(datetime.today()) * 1000
        trigger_sender.update(data, identifier)

    with open(target_file(tmp_path), "r") as f:
        results = list(csv.reader(f, delimiter=','))
        assert len(results) == 1
        assert len(results[0]) == 2
        assert send_ts - epsilon <= float(results[0][0]) <= send_ts + epsilon
        assert results[0][1] == str(ETrigger.get_trigger(data, identifier))


@pytest.mark.parametrize("data", ["test1", "test2", "", "Longer primer testing12345 abc"])
def test_file_trigger_sender_send_trigger_new_primer_valid_call(data, tmp_path):
    epsilon = 3

    trigger_sender = FileTriggerSender(THREAD_TIMOUT, target_file(tmp_path))

    data = EExperimentState.INTRODUCTION
    identifier = EModelUpdateIdentifier.NEW_PRIMER

    with trigger_sender.start() as ts:
        send_ts = datetime.timestamp(datetime.today()) * 1000
        trigger_sender.update(data, identifier)

    with open(target_file(tmp_path), "r") as f:
        results = list(csv.reader(f, delimiter=','))
        assert len(results) == 1
        assert len(results[0]) == 2
        assert send_ts - epsilon <= float(results[0][0]) <= send_ts + epsilon
        assert results[0][1] == str(ETrigger.get_trigger(data, identifier))


def test_file_trigger_sender_send_trigger_new_stimulus_valid_call(tmp_path):
    epsilon = 3

    trigger_sender = FileTriggerSender(THREAD_TIMOUT, target_file(tmp_path))

    data = MOCK_CREATED_STIMULUS
    identifier = EModelUpdateIdentifier.NEW_STIMULUS

    with trigger_sender.start() as ts:
        send_ts = datetime.timestamp(datetime.today()) * 1000
        trigger_sender.update(data, identifier)

    with open(target_file(tmp_path), "r") as f:
        results = list(csv.reader(f, delimiter=','))
    assert len(results) == 1 + len(data.time_stamps) * 2 + 1
    assert all(len(res) == 2 for res in results)

    # first trigger should be new stimulus
    assert send_ts - epsilon <= float(results[0][0]) <= send_ts + epsilon
    assert results[0][1] == str(ETrigger.NEW_STIMULUS)

    # last trigger should be end stimulus
    target_ts = send_ts + data.audio.secs * 1000
    assert target_ts - epsilon <= float(results[-1][0]) <= target_ts + epsilon
    assert results[-1][1] == str(ETrigger.END_STIMULUS)

    for i, ts in enumerate(data.time_stamps):
        target_ts = send_ts + ts[0] * 1000
        assert target_ts - epsilon <= float(results[1 + i * 2][0]) <= target_ts + epsilon
        assert results[1 + i * 2][1] == str(ETrigger.OPTION_START)

        target_ts = send_ts + ts[1] * 1000
        assert target_ts - epsilon <= float(results[1 + i * 2 + 1][0]) <= target_ts + epsilon
        assert results[1 + i * 2 + 1][1] == str(ETrigger.OPTION_END)

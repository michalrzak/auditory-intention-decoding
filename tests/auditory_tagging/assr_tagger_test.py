from typing import Tuple, List, Callable

import numpy as np
import numpy.typing as npt
import pytest

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FMTagger
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def mock_stimulus_generation(length: int, frequency: int, sampling_frequency: int) -> npt.NDArray[np.float32]:
    """Generates a mock stimulus generation function. consisting of only -1. -1 is picked so that the signal is
    modified.
    """
    return -np.ones(length, dtype=np.float32)


def get_am_tagger(audio: Audio, stimuli_intervals: List[Tuple[float, float]], frequency: int) -> AAudioTagger:
    return AMTagger(audio, stimuli_intervals, frequency, mock_stimulus_generation)


def get_fm_tagger(audio: Audio, stimuli_intervals: List[Tuple[float, float]], frequency: int) -> AAudioTagger:
    return FMTagger(audio, stimuli_intervals, frequency)


TAGGER_GETTERS: List[Callable[[Audio, List[Tuple[float, float]], int], AAudioTagger]] = [get_am_tagger, get_fm_tagger]


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_create_validCall_audioShouldBeModified(tagger_getter):
    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 2

    stimulus = tagger_getter(audio,
                             [(0, n_input / sampling_frequency)],
                             stimulus_frequency)
    modified_audio = stimulus.create()

    assert modified_audio is not None
    assert modified_audio.array is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.array != audio.array)


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_create_validCall_audioShouldBeModifiedToHalfPoint(tagger_getter):
    n_input = 100
    sampling_frequency = 2
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 1

    stimulus = tagger_getter(audio,
                             [(0, n_input / sampling_frequency / 2)],
                             stimulus_frequency)
    modified_audio = stimulus.create()

    assert modified_audio is not None
    assert modified_audio.array is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.array[:n_input // 2, :] != audio.array[:n_input // 2, :])
    assert np.all(modified_audio.array[n_input // 2:, :] == audio.array[n_input // 2:, :])


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_invalidFrequency_0_shouldThrow(tagger_getter):
    audio = get_mock_audio(100, 12)
    stimulus_frequency = 0

    with pytest.raises(ValueError):
        stim = tagger_getter(audio,
                             [(0, 1)],
                             stimulus_frequency)


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_invalidFrequency_negative_shouldThrow(tagger_getter):
    audio = get_mock_audio(100, 12)
    stimulus_frequency = -1

    with pytest.raises(ValueError):
        stim = tagger_getter(audio,
                             [(0, 1)],
                             stimulus_frequency)


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_create_validCall(tagger_getter):
    n_input = 1000
    sampling_frequency = 20
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 5

    stim = tagger_getter(audio,
                         [(0, n_input / sampling_frequency)],
                         stimulus_frequency)
    stim.create()

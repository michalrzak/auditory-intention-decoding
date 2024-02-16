from typing import Callable

import mockito

import numpy as np
import pytest

from auditory_stimulation.auditory_stimulus.assr_stimulus import ASSRStimulus
from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio


def get_mocked_audio(n_input: int, sampling_frequency: int, seed: int = 100) -> Audio:
    np.random.seed(seed)

    audio = mockito.mock(Audio)
    audio.audio = np.random.rand(n_input, 2)
    audio.sampling_frequency = sampling_frequency

    return audio


def get_mock_audio_player() -> Callable[[Audio], None]:
    return lambda a: None


def test_ASSRStimulus_create_validCall_audioShouldBeModified():
    n_input = 100
    sampling_frequency = 12
    audio = get_mocked_audio(n_input, sampling_frequency)

    stimulus_frequency = 2

    stimulus = ASSRStimulus(audio,
                            [(0, n_input / sampling_frequency)],
                            get_mock_audio_player(),
                            stimulus_frequency)
    stimulus.create()

    modified_audio = stimulus.modified_audio

    assert modified_audio is not None
    assert modified_audio.audio is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.audio != audio.audio)


def test_ASSRStimulus_create_validCall_audioShouldBeModifiedToHalfPoint():
    n_input = 100
    sampling_frequency = 2
    audio = get_mocked_audio(n_input, sampling_frequency)

    stimulus_frequency = 1

    stimulus = ASSRStimulus(audio,
                            [(0, n_input / sampling_frequency / 2)],
                            get_mock_audio_player(),
                            stimulus_frequency)
    stimulus.create()

    modified_audio = stimulus.modified_audio

    assert modified_audio is not None
    assert modified_audio.audio is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.audio[:n_input // 2, :] != audio.audio[:n_input // 2, :])
    assert np.all(modified_audio.audio[n_input // 2:, :] == audio.audio[n_input // 2:, :])


def test_ASSRStimulus_invalidFrequency_doesNotDivide_shouldThrow():
    n_input = 1000
    sampling_frequency = 17
    audio = get_mocked_audio(n_input, sampling_frequency)

    stimulus_frequency = 5

    with pytest.raises(ValueError):
        stim = ASSRStimulus(audio, [(0, 1)], get_mock_audio_player(), stimulus_frequency)


def test_ASSRStimulus_invalidFrequency_0_shouldThrwo():
    audio = get_mocked_audio(100, 12)
    stimulus_frequency = 0

    with pytest.raises(ValueError):
        stim = ASSRStimulus(audio, [(0, 1)], get_mock_audio_player(), stimulus_frequency)


def test_ASSRStimulus_invalidFrequency_negative_shouldThrwo():
    audio = get_mocked_audio(100, 12)
    stimulus_frequency = -1

    with pytest.raises(ValueError):
        stim = ASSRStimulus(audio, [(0, 1)], get_mock_audio_player(), stimulus_frequency)

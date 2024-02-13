import mockito

import numpy as np

from auditory_stimulation.auditory_stimulus.assr_stimulus import ASSRStimulus
from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio


def get_mocked_audio(n_input: int, sampling_frequency: int) -> Audio:
    audio = mockito.mock(Audio)
    audio.audio = np.zeros((n_input, 2))
    audio.sampling_frequency = sampling_frequency

    return audio


def test_ASSRStimulus_create_validCall_audioShouldBeModified():
    n_input = 100
    sampling_frequency = 2
    audio = get_mocked_audio(n_input, sampling_frequency)

    stimulus_frequency = 40

    stimulus = ASSRStimulus(audio,
                            [(0, n_input / sampling_frequency)],
                            lambda a: None,
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

    stimulus_frequency = 40

    stimulus = ASSRStimulus(audio,
                            [(0, n_input / sampling_frequency / 2)],
                            lambda a: None,
                            stimulus_frequency)
    stimulus.create()

    modified_audio = stimulus.modified_audio

    assert modified_audio is not None
    assert modified_audio.audio is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.audio[:n_input // 2, :] != audio.audio[:n_input // 2, :])
    assert np.all(modified_audio.audio[n_input // 2:, :] == audio.audio[n_input // 2:, :])

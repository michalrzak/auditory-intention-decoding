import mockito

from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio
from auditory_stimulation.auditory_stimulus.noise_tagging_stimulus import NoiseTaggingStimulus
from tests.auditory_stimulus.stimulus_test_helpers import get_mock_audio, get_mock_audio_player

import numpy as np

SEED = 123


def test_create_validCall_channelsShouldBeTheSame():
    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus = NoiseTaggingStimulus(audio,
                                    [(0, n_input / sampling_frequency)],
                                    get_mock_audio_player(),
                                    10,
                                    20,
                                    SEED)
    stimulus.create()

    code = stimulus.code

    assert np.all(code[:, 0] == code[:, 1])


def test_create_validCall_codeHasCorrectResolution():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_audio(n_input, sampling_frequency)

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = 5
    length = bits_per_second * 2
    stimulus = NoiseTaggingStimulus(audio,
                                    [labeled_interval],
                                    get_mock_audio_player(),
                                    bits_per_second,
                                    length,
                                    SEED)

    stimulus.create()
    code = stimulus.code

    bit_width = sampling_frequency / bits_per_second

    assert code.shape[0] == bit_width * length


def test_create_validCall_codeRepeatsCorrectly():
    n_input = 100
    sampling_frequency = 10
    audio = mockito.mock(Audio)
    audio.audio = np.ones((n_input, 2))
    audio.sampling_frequency = sampling_frequency

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = 5
    length = bits_per_second  # code of length 1 second

    stimulus = NoiseTaggingStimulus(audio,
                                    [labeled_interval],
                                    get_mock_audio_player(),
                                    bits_per_second,
                                    length,
                                    SEED)
    stimulus.create()

    # since the code is 1 second and the interval is 2 seconds, the code should repeat twice
    code = stimulus.code
    modified_audio = stimulus.modified_audio

    assert np.all(
        modified_audio.audio[labeled_interval[0] * sampling_frequency:labeled_interval[1] * sampling_frequency // 2, :]
        == code)
    assert np.all(
        modified_audio.audio[labeled_interval[1] * sampling_frequency // 2:labeled_interval[1] * sampling_frequency, :]
        == code)

# TODO probably need to check how stuff behaves if bitwidth does not divide the sampling frequency

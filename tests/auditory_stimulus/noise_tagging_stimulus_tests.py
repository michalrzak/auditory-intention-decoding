from auditory_stimulation.auditory_stimulus.noise_tagging_stimulus import NoiseTaggingStimulus
from tests.auditory_stimulus.stimulus_test_helpers import get_mock_audio, get_mock_audio_player

import numpy as np

SEED = 123


def test_create_generatedCode_validCall_channelsShouldBeTheSame():
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


def test_create_generatedCode_validCall_codeHasCorrectResolution():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_audio(n_input, sampling_frequency)

    labeled_interval = (0, sampling_frequency * 2)  # 2 seconds labeled
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

# TODO probably need to check how stuff behaves if bitwidth does not divide the sampling frequency
# TODO check that np.repeat actually works like I expect

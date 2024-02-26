import numpy as np
import pytest
import numpy.typing as npt

from auditory_stimulation.auditory_stimulus.assr_stimulus import ASSRStimulus, clicking_signal
from tests.auditory_stimulus.stimulus_test_helpers import get_mock_audio, get_mock_audio_player, get_mock_ones_audio


def mock_stimulus_generation(length: int, frequency: int, sampling_frequency: int) -> npt.NDArray[np.float32]:
    """Generates a mock stimulus generation function. consisting of only -1. -1 is picked so that the signal is
    modified.
    """
    return -np.ones(length, dtype=np.float32)


def test_ASSRStimulus_create_validCall_audioShouldBeModified():
    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 2

    stimulus = ASSRStimulus(audio,
                            [(0, n_input / sampling_frequency)],
                            get_mock_audio_player(),
                            stimulus_frequency,
                            mock_stimulus_generation)
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
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 1

    stimulus = ASSRStimulus(audio,
                            [(0, n_input / sampling_frequency / 2)],
                            get_mock_audio_player(),
                            stimulus_frequency,
                            mock_stimulus_generation)
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
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 5

    with pytest.raises(ValueError):
        stim = ASSRStimulus(audio,
                            [(0, 1)],
                            get_mock_audio_player(),
                            stimulus_frequency,
                            mock_stimulus_generation)


def test_ASSRStimulus_invalidFrequency_0_shouldThrow():
    audio = get_mock_audio(100, 12)
    stimulus_frequency = 0

    with pytest.raises(ValueError):
        stim = ASSRStimulus(audio,
                            [(0, 1)],
                            get_mock_audio_player(),
                            stimulus_frequency,
                            mock_stimulus_generation)


def test_ASSRStimulus_invalidFrequency_negative_shouldThrow():
    audio = get_mock_audio(100, 12)
    stimulus_frequency = -1

    with pytest.raises(ValueError):
        stim = ASSRStimulus(audio,
                            [(0, 1)],
                            get_mock_audio_player(),
                            stimulus_frequency,
                            mock_stimulus_generation)


def test_ASSRStimulus_create_validCall():
    n_input = 1000
    sampling_frequency = 20
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 5

    stim = ASSRStimulus(audio,
                        [(0, n_input / sampling_frequency)],
                        get_mock_audio_player(),
                        stimulus_frequency,
                        mock_stimulus_generation)
    stim.create()

def test_clickingStimulus_validCall_shouldHaveCorrectFrequency():
    epsilon = 0.1

    sampling_frequencies = [12, 20, 24, 60]
    stimulus_frequencies = [3, 5, 4, 15]

    length = 1000

    for sampling_frequency, stimulus_frequency in zip(sampling_frequencies, stimulus_frequencies):
        modulating_stimulus = clicking_signal(length, stimulus_frequency, sampling_frequency)

        modulating_stimulus_spectrum = np.abs(np.real(np.fft.fftshift(np.fft.fft(modulating_stimulus))))
        # cut of the irrelevant half of the spectrum
        modulating_stimulus_spectrum = modulating_stimulus_spectrum[modulating_stimulus_spectrum.shape[0] // 2:]

        peak = np.argmax(modulating_stimulus_spectrum)
        peak_frequency = peak * sampling_frequency / length

        assert peak_frequency - epsilon <= stimulus_frequency <= peak_frequency + epsilon

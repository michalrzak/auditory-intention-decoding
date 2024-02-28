import numpy as np
import pytest

from auditory_stimulation.auditory_stimulus.stimulus_generators import clicking_signal, sine_signal

STIMULUS_GENERATORS = [clicking_signal, sine_signal]


@pytest.mark.parametrize("stimulus_generation", STIMULUS_GENERATORS)
def test_stimulusGeneration_validCall_shouldHaveCorrectFrequency(stimulus_generation):
    epsilon = 0.1

    sampling_frequencies = [12, 20, 24, 60]
    stimulus_frequencies = [3, 5, 4, 15]

    length = 1000

    for sampling_frequency, stimulus_frequency in zip(sampling_frequencies, stimulus_frequencies):
        modulating_stimulus = stimulus_generation(length, stimulus_frequency, sampling_frequency)

        modulating_stimulus_spectrum = np.abs(np.real(np.fft.fftshift(np.fft.fft(modulating_stimulus))))
        # cut of the irrelevant half of the spectrum
        modulating_stimulus_spectrum = modulating_stimulus_spectrum[modulating_stimulus_spectrum.shape[0] // 2:]

        peak = np.argmax(modulating_stimulus_spectrum)
        peak_frequency = peak * sampling_frequency / length

        assert peak_frequency - epsilon <= stimulus_frequency <= peak_frequency + epsilon


@pytest.mark.parametrize("stimulus_generation", STIMULUS_GENERATORS)
def test_stimulusGeneration_invalidFrequency_negative_shouldThrow(stimulus_generation):
    length = 1000
    sampling_frequency = 20

    frequency = -5

    with pytest.raises(ValueError):
        stimulus_generation(length, frequency, sampling_frequency)


@pytest.mark.parametrize("stimulus_generation", STIMULUS_GENERATORS)
def test_stimulusGeneration_invalidFrequency_0_shouldThrow(stimulus_generation):
    length = 1000
    sampling_frequency = 20

    frequency = 0

    with pytest.raises(ValueError):
        stimulus_generation(length, frequency, sampling_frequency)


@pytest.mark.parametrize("stimulus_generation", STIMULUS_GENERATORS)
def test_stimulusGeneration_invalidSamplingFrequency_negative_shouldThrow(stimulus_generation):
    length = 1000
    sampling_frequency = -20

    frequency = 5

    with pytest.raises(ValueError):
        stimulus_generation(length, frequency, sampling_frequency)


@pytest.mark.parametrize("stimulus_generation", STIMULUS_GENERATORS)
def test_stimulusGeneration_invalidSamplingFrequency_0_shouldThrow(stimulus_generation):
    length = 1000
    sampling_frequency = 0

    frequency = 5

    with pytest.raises(ValueError):
        stimulus_generation(length, frequency, sampling_frequency)


@pytest.mark.parametrize("stimulus_generation", STIMULUS_GENERATORS)
def test_stimulusGeneration_invalidSamplingFrequency_and_invalidFrequency_bellowZero_shouldThrow(stimulus_generation):
    length = 1000
    sampling_frequency = -20

    frequency = -5

    with pytest.raises(ValueError):
        stimulus_generation(length, frequency, sampling_frequency)


def test_clickingStimulus_invalidFrequency_doesNotDivide_shouldThrow():
    length = 1000
    sampling_frequency = 17

    frequency = 5

    with pytest.raises(ValueError):
        clicking_signal(length, frequency, sampling_frequency)

from numbers import Number, Complex, Real
from typing import List, Tuple, Callable

import numpy as np
import numpy.typing as npt
from scipy.signal import hilbert

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, AAudioTaggerFactory, _duplicate_signal, \
    _scale_down_signal
from auditory_stimulation.auditory_tagging.tag_generators import TagGenerator


def amplitude_modulation(signal: npt.NDArray[np.float32],
                         modulation_code: npt.NDArray[Number]) -> npt.NDArray[np.float32]:
    """Applies amplitude modulation to signal and modulation code and returns the resulting signal. The modulation code
    has to be of the same length as the signal.

    :param signal: The base signal. Needs to be of the shape Nx2
    :param modulation_code: The modulation code. Needs to be of the shape N
    :return: the resulting, modulated signal
    """

    if len(signal.shape) != 2 or signal.shape[1] != 2:
        raise ValueError("Signal must have dimensions Nx2!")

    if len(modulation_code.shape) != 1:
        raise ValueError("Modulation code must have dimensions Nx1!")

    if signal.shape[0] != modulation_code.shape[0]:
        raise ValueError("Signal and modulation_code must match in their first dimension!")

    duplicate_code = _duplicate_signal(modulation_code)

    output = signal * duplicate_code
    assert output.shape == signal.shape

    output_scaled = _scale_down_signal(output)
    return output_scaled


def frequency_modulation(signal: npt.NDArray[np.float32],
                         f_sampling: int,
                         f_carrier: int,
                         modulation_factor: float = 1) -> npt.NDArray[np.float32]:
    """Applies frequency modulation to the provided signal. Done by FM the a sine wave with f = carrier_frequency with
    the signal. (Cannot be done other way around, or with an arbitrary carrier signal, as FM requires an underlying
    periodic signal)

    :param signal: The encoded signal.
    :param f_sampling: The sampling frequency of the signal.
    :param f_carrier: Frequency of the carrier signal.
    :param modulation_factor: Optional parameter, determining how strongly the signal is modulated in the carrier.
    :return: The FM modulated signal.
    """
    if len(signal.shape) != 2 or signal.shape[1] != 2:
        raise ValueError("Signal must have dimensions Nx2!")

    samples = _duplicate_signal(f_carrier / f_sampling * np.arange(signal.shape[0]))

    combined_signal = np.sin(2 * np.pi * (samples + signal * modulation_factor), dtype=np.float32)
    assert combined_signal.shape == signal.shape

    return combined_signal


class AMTagger(AAudioTagger):
    """Creates an AM modulated ASSR stimulus.
    """
    __frequency: int
    __tag_generator: TagGenerator

    def __init__(self,
                 audio: Audio,
                 stimuli_intervals: List[Tuple[float, float]],
                 frequency: int,
                 tag_generator: TagGenerator) -> None:
        """Constructs the AMTagger object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param frequency: The frequency of the AM tag
        :param tag_generator: A function, which given the length, stimulus frequency and sampling frequency
         generates the tagging signal.
        """

        super().__init__(audio, stimuli_intervals)

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")

        self.__frequency = frequency
        self.__tag_generator = tag_generator

    def create(self) -> Audio:
        """This method is implemented from the abstract super class. When called, it generates the AM tagged audio.

        :return: The AM tagged audio.
        """

        audio_copy = np.copy(self._audio.array)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            # generate sine of the appropriate frequency
            signal_length = sample_range[1] - sample_range[0]
            added_signal = self.__tag_generator(signal_length, self.__frequency, self._audio.sampling_frequency)

            modulated_chunk = amplitude_modulation(audio_copy[sample_range[0]:sample_range[1]], added_signal)
            audio_copy[sample_range[0]:sample_range[1]] = modulated_chunk

        return Audio(audio_copy, self._audio.sampling_frequency)


class FMTagger(AAudioTagger):
    __frequency: int

    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]], frequency: int):
        """Constructs the FlippedFMTagger object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param frequency: The modulating frequency.
        """

        super().__init__(audio, stimuli_intervals)

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")
        self.__frequency = frequency

    @staticmethod
    def __extract_amplitudes_phases(numbers: npt.NDArray[Complex]) -> Tuple[npt.NDArray[Real], npt.NDArray[Real]]:
        """Extracts the amplitude and the phase from the (complex) numbers provided.

        :param numbers: A collection of complex numbers.
        :return: (collection of amplitudes, collection  of phases)
        """
        amplitude = np.abs(numbers)
        phase = np.unwrap(np.angle(numbers))

        assert amplitude.shape == numbers.shape
        assert phase.shape == numbers.shape

        return amplitude, phase

    @staticmethod
    def __get_complex_number(amplitudes: npt.NDArray[Real], phases: npt.NDArray[Real]) -> npt.NDArray[Complex]:
        """Given a list of amplitudes and a list of phases, combines them to represent one complex number."""

        output = np.array([amplitude * np.e ** (1j * phase) for amplitude, phase in zip(amplitudes, phases)])
        assert output.shape == amplitudes.shape
        assert output.shape == phases.shape

        return output

    def __phases_to_instantaneous_frequencies(self, phases: npt.NDArray[Real]) -> npt.NDArray[Real]:
        inst_freq = np.diff(phases, axis=0) / (2 * np.pi) * self._audio.sampling_frequency
        assert inst_freq.shape[0] == phases.shape[0] - 1, f"Was {inst_freq.shape} vs {phases.shape} - 1"
        assert inst_freq.shape[1] == phases.shape[1] == 2

        return inst_freq

    def __instantaneous_frequencies_to_phases(self,
                                              instantaneous_frequencies: npt.NDArray[Real],
                                              first_phase: npt.NDArray[Real]) -> npt.NDArray[Real]:
        first_phase_reshaped = np.reshape(first_phase, (1, 2))
        assert first_phase_reshaped.shape[0] == 1
        assert first_phase_reshaped.shape[1] == 2

        corrected_inst_freq = instantaneous_frequencies * (2 * np.pi) / self._audio.sampling_frequency
        phases = np.append(first_phase_reshaped, corrected_inst_freq, axis=0).cumsum(axis=0)

        assert phases.shape[0] == instantaneous_frequencies.shape[0] + 1
        assert phases.shape[1] == instantaneous_frequencies.shape[1] == 2

        return phases

    def __modulate(self, signal: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
        assert signal.shape[1] == 2

        analytic = hilbert(signal, axis=0)
        amplitude, phase = self.__extract_amplitudes_phases(analytic)

        inst_freq = self.__phases_to_instantaneous_frequencies(phase)

        added_freq = np.ones_like(inst_freq) * self.__frequency
        shifted_inst_freq = inst_freq + added_freq

        phase_shifted = self.__instantaneous_frequencies_to_phases(shifted_inst_freq, phase[0, :])

        reconstructed_shifted = self.__get_complex_number(amplitude, phase_shifted)
        assert reconstructed_shifted.shape == signal.shape

        return np.real(reconstructed_shifted)

    def create(self) -> Audio:
        audio_copy = np.copy(self._audio.array)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            modulated_chunk = self.__modulate(audio_copy[sample_range[0]:sample_range[1]])
            audio_copy[sample_range[0]:sample_range[1]] = modulated_chunk

        return Audio(audio_copy, self._audio.sampling_frequency)


class FlippedFMTagger(AAudioTagger):
    """This tagger tags the given audio signal with the tagging frequency, by interpreting the tagging frequency as the
    carrier frequency of FM and the audio signal as the modulating signal. This hence flips the interpretation of the
    FM, as the taggers attempt to tag the audio (carrier) with a frequency (modulator)."""
    __frequency: int

    def __init__(self,
                 audio: Audio,
                 stimuli_intervals: List[Tuple[float, float]],
                 frequency: int) -> None:
        """Constructs the FlippedFMTagger object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param frequency: The FM carrier frequency, modulated by the audio
        """

        super().__init__(audio, stimuli_intervals)

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")

        self.__frequency = frequency

    def create(self) -> Audio:
        """This method is implemented from the abstract super class. When called, it generates the FM tagged audio.

        :return: The FM tagged audio.
        """

        audio_copy = np.copy(self._audio.array)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            modulated_chunk = frequency_modulation(audio_copy[sample_range[0]:sample_range[1]],
                                                   self._audio.sampling_frequency,
                                                   self.__frequency)
            audio_copy[sample_range[0]:sample_range[1]] = modulated_chunk

        return Audio(audio_copy, self._audio.sampling_frequency)


class AMTaggerFactory(AAudioTaggerFactory):
    _frequency: int
    _tag_generator: Callable[[int, int, int], npt.NDArray[np.float32]]

    def __init__(self,
                 frequency: int,
                 tag_generator: Callable[[int, int, int], npt.NDArray[np.float32]],
                 ) -> None:
        self._frequency = frequency
        self._stimulus_generator = tag_generator

    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return AMTagger(audio,
                        stimuli_intervals,
                        self._frequency,
                        self._stimulus_generator)


class FMTaggerFactory(AAudioTaggerFactory):
    _frequency: int

    def __init__(self, frequency: int) -> None:
        self._frequency = frequency

    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return FMTagger(audio,
                        stimuli_intervals,
                        self._frequency)


class FlippedFMTaggerFactory(AAudioTaggerFactory):
    _frequency: int

    def __init__(self, frequency: int) -> None:
        self._frequency = frequency

    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return FlippedFMTagger(audio,
                               stimuli_intervals,
                               self._frequency)

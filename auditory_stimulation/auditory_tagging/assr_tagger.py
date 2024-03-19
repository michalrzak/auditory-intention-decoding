from numbers import Number, Complex, Real
from typing import Tuple

import numpy as np
import numpy.typing as npt
from scipy.signal import hilbert

from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, _duplicate_signal, \
    _scale_down_signal
from auditory_stimulation.auditory_tagging.tag_generators import TagGenerator, sine_signal


def _shape_signal(signal: npt.NDArray[np.float32], signal_interval: Tuple[float, float]) -> npt.NDArray[np.float32]:
    """Expects a signal in the range -1 to 1"""
    if signal_interval[0] == -1 and signal_interval[1] == 1:
        return signal

    # the following is just an assert statement as checking it could potentially take a very long time
    assert all(-1 <= signal) and all(signal <= 1)

    shaped_signal = abs(signal_interval[1] - signal_interval[0]) / 2 * (signal + 1) + signal_interval[0]
    assert shaped_signal.shape[0] == signal.shape[0]
    assert len(shaped_signal.shape) == 1

    return shaped_signal


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
    __signal_interval: Tuple[float, float]

    def __init__(self,
                 frequency: int,
                 tag_generator: TagGenerator,
                 signal_interval: Tuple[float, float] = (-1, 1)) -> None:
        """Constructs the AMTagger object

        :param frequency: The frequency of the AM tag
        :param tag_generator: A function, which given the length, stimulus frequency and sampling frequency
         generates the tagging signal.
        :param signal_interval: Default = (-1, 1). The interval of the generated signal. The first value specifies the
         lower boundary, the second value of the upper boundary.
        """

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")

        if signal_interval[0] > signal_interval[1]:
            raise ValueError(
                "The first value of the signal interval needs to be the lower boundary, while the second value"
                " is the upper boundary, which does not seem to be the case!")

        if signal_interval[0] == signal_interval[1]:
            raise ValueError("The interval cannot have length 0!")

        self.__frequency = frequency
        self.__tag_generator = tag_generator
        self.__signal_interval = signal_interval

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        # generate tag of the appropriate frequency
        signal_length = audio_array_chunk.shape[0]
        added_signal_raw = self.__tag_generator(signal_length, self.__frequency, fs)

        # change the interval of the tag to the set range
        added_signal = _shape_signal(added_signal_raw, self.__signal_interval)

        modulated_chunk = amplitude_modulation(audio_array_chunk, added_signal)

        return modulated_chunk

    def __repr__(self) -> str:
        return self._get_repr("AMTagger", frequency=str(self.__frequency), tag_generator=self.__tag_generator.__name__,
                              signal_interval=str(self.__signal_interval))


class FMTagger(AAudioTagger):
    """Uses the audio signal as the carrier and modulates it by specified frequency. The frequency of the audio signal
     is computed via the hilbert transform (instantaneous frequency). In essence, this only shifts the entire audio
     spectrum up by the specified frequency (imagine a simple sine wave to see why)."""
    __frequency: int
    __modulation_factor: float

    def __init__(self,
                 frequency: int,
                 modulation_factor: float) -> None:
        """Constructs the FMTagger object

        :param frequency: The modulating frequency.
        :param modulation_factor: The factor by which the added modulating signal is scaled.
        """

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")
        self.__frequency = frequency
        self.__modulation_factor = modulation_factor

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

    def __phases_to_instantaneous_frequencies(self, phases: npt.NDArray[Real], fs: int) -> npt.NDArray[Real]:
        inst_freq = np.diff(phases, axis=0) / (2 * np.pi) * fs
        assert inst_freq.shape[0] == phases.shape[0] - 1, f"Was {inst_freq.shape} vs {phases.shape} - 1"
        assert inst_freq.shape[1] == phases.shape[1] == 2

        return inst_freq

    def __instantaneous_frequencies_to_phases(self,
                                              instantaneous_frequencies: npt.NDArray[Real],
                                              first_phase: npt.NDArray[Real],
                                              fs: int) -> npt.NDArray[Real]:
        first_phase_reshaped = np.reshape(first_phase, (1, 2))
        assert first_phase_reshaped.shape[0] == 1
        assert first_phase_reshaped.shape[1] == 2

        corrected_inst_freq = instantaneous_frequencies * (2 * np.pi) / fs
        phases = np.append(first_phase_reshaped, corrected_inst_freq, axis=0).cumsum(axis=0)

        assert phases.shape[0] == instantaneous_frequencies.shape[0] + 1
        assert phases.shape[1] == instantaneous_frequencies.shape[1] == 2

        return phases

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        assert audio_array_chunk.shape[1] == 2

        analytic = hilbert(audio_array_chunk, axis=0)
        amplitude, phase = self.__extract_amplitudes_phases(analytic)

        inst_freq = self.__phases_to_instantaneous_frequencies(phase, fs)

        # generate a sine wave of the appropriate frequency and of the appropriate shape
        modulating_sine = sine_signal(inst_freq.shape[0], self.__frequency, fs)
        modulating_sine_doubled = _duplicate_signal(modulating_sine)

        # modulate the signal frequency with the generated sine wave
        shifted_inst_freq = inst_freq + self.__modulation_factor * modulating_sine_doubled

        phase_shifted = self.__instantaneous_frequencies_to_phases(shifted_inst_freq, phase[0, :], fs)

        reconstructed_shifted = self.__get_complex_number(amplitude, phase_shifted)
        assert reconstructed_shifted.shape == audio_array_chunk.shape

        return _scale_down_signal(np.real(reconstructed_shifted))

    def __repr__(self) -> str:
        return self._get_repr("FMTagger", frequency=str(self.__frequency),
                              modulation_factor=str(self.__modulation_factor))


class FlippedFMTagger(AAudioTagger):
    """This tagger tags the given audio signal with the tagging frequency, by interpreting the tagging frequency as the
    carrier frequency of FM and the audio signal as the modulating signal. This hence flips the interpretation of the
    FM, as the taggers attempt to tag the audio (carrier) with a frequency (modulator)."""
    __frequency: int

    def __init__(self,
                 frequency: int) -> None:
        """Constructs the FlippedFMTagger object

        :param frequency: The FM carrier frequency, modulated by the audio
        """

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")

        self.__frequency = frequency

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        modulated_chunk = frequency_modulation(audio_array_chunk, fs, self.__frequency)
        return modulated_chunk

    def __repr__(self) -> str:
        return self._get_repr("FlippedFMTagger", frequency=str(self.__frequency))

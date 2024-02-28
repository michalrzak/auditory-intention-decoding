from typing import List, Tuple, Callable, Optional

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio, AAuditoryStimulusFactory
import numpy as np
import numpy.typing as npt

Code = npt.NDArray[np.int16]


class NoiseTaggingStimulus(AAuditoryStimulus):
    """Creates a noise tagging stimulus. This stimulus is generated by first creating a random code and then modulating
    the signal with this code."""
    __seed: Optional[int]
    __bit_width: int
    __length_bit: int
    __code: Optional[Code]  # can only contain 1 and -1

    def __init__(self,
                 audio: Audio,
                 stimuli_intervals: List[Tuple[float, float]],
                 audio_player: Callable[[Audio], None],
                 bits_per_second: int,
                 length_bit: int,
                 seed: Optional[int] = None) -> None:
        """Constructs the NoiseTaggingStimulus object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param audio_player: A function, which if given an audio plays it
        :param bits_per_second: The resolution of the noise tagging stimulus.
        :param length_bit: The length of the tag in bits.
        :param seed: An Optional seed for the tag generation.
        """
        super().__init__(audio, stimuli_intervals, audio_player)

        if bits_per_second <= 0:
            raise ValueError("bits_per_second has to be a positive number")

        if self._audio.sampling_frequency // bits_per_second != self._audio.sampling_frequency / bits_per_second:
            raise ValueError("bits_per_second must fully divide the sampling frequency of the audio, otherwise the code"
                             " cannot be fully created")

        if length_bit <= 0:
            raise ValueError("length_bit has to be a positive number")

        self.__seed = seed

        # save only the bit_width and not the bits_per_seconds, as the latter is not used anywhere later in the code
        self.__bit_width = self._audio.sampling_frequency // bits_per_second
        self.__length_bit = length_bit

        self.__code = None

    def __generate_code(self) -> None:
        """If the code is not already set, generates a new code and sets it.
        technically, as we are only using one code, we can generate an arbitrary random sequence

        TODO: change this to a a more deliberate solution if multiple codes are used
        """

        if self.__code is not None:
            return

        if self.__seed is not None:
            np.random.seed(self.__seed)

        random_floats = np.random.rand(self.__length_bit)  # Nx1 as I want the same code for both audio channels
        random_zero_one = np.array(random_floats > 0.5, dtype=np.int16)
        code = random_zero_one * 2 - 1

        code_normalized = np.repeat(code, self.__bit_width)
        self.__code = np.array([code_normalized, code_normalized]).T  # duplicate code to both audio channels
        assert self.__code.shape[1] == 2

    def __get_code(self, length: int) -> Code:
        """Need to run __generate_code() first. This function returns an appropriately cut code to the given length.

        :param length: The length of the to be generated code.
        :return: The appropriately cut noise tagging code.
        """
        if self.__code is None:
            raise ValueError("You must run __generate_code() first before you can run this method")

        repeat = length // self.__code.shape[0]
        long_code = np.tile(self.__code.T, repeat).T
        assert long_code.shape[0] == self.__code.shape[0] * repeat

        if long_code.shape[0] == length:
            assert long_code.shape[1] == 2
            return long_code

        assert length - long_code.shape[0] > 0
        out = np.append(long_code, self.__code[:length - long_code.shape[0], :], axis=0)

        assert out.shape[0] == length, f"out.shape[0]: {out.shape[0]}; length: {length}"
        assert out.shape[1] == 2
        return out

    def _create_modified_audio(self) -> Audio:
        """This method is implemented from the abstract super class. When called, it generates the noise tagging
         stimulus modified audio.

        :return: The noise tagging stimulus modified audio.
        """
        self.__generate_code()

        audio_copy = np.copy(self._audio.audio)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            audio_copy[sample_range[0]:sample_range[1]] *= self.__get_code(sample_range[1] - sample_range[0])

        return Audio(audio_copy, self._audio.sampling_frequency)

    @property
    def code(self) -> Optional[Code]:
        if self.__code is None:
            return None

        return np.copy(self.__code)


class NoiseTaggingStimulusFactory(AAuditoryStimulusFactory):
    _bits_per_second: int
    _length_bit: int
    _seed: Optional[int]

    def __init__(self,
                 audio_player: Callable[[Audio], None],
                 bits_per_second: int,
                 length_bit: int,
                 seed: Optional[int] = None) -> None:
        super().__init__(audio_player)
        self._bits_per_second = bits_per_second
        self._length_bit = length_bit
        self._seed = seed

    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAuditoryStimulus:
        return NoiseTaggingStimulus(audio,
                                    stimuli_intervals,
                                    self._audio_player,
                                    self._bits_per_second,
                                    self._length_bit,
                                    self._seed)

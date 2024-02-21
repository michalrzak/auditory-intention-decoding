from typing import List, Tuple, Callable, Optional

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio
import numpy as np
import numpy.typing as npt

Code = npt.NDArray[np.int16]


class NoiseTaggingStimulus(AAuditoryStimulus):
    __seed: Optional[int]
    __bits_per_second: int
    __length_bit: int
    __code: Optional[Code]  # can only contain 1 and -1

    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]],
                 audio_player: Callable[[Audio], None], bits_per_second: int, length_bit: int,
                 seed: Optional[int]) -> None:
        super().__init__(audio, stimuli_intervals, audio_player)

        if seed is not None:
            if seed <= 0:
                ...
                # TODO: check. does the seed need to be a positive integer?

        self.__seed = seed

        if bits_per_second <= 0:
            raise ValueError("bits_per_second has to be a positive number")

        if length_bit <= 0:
            raise ValueError("length_bit has to be a positive number")

        self.__bits_per_second = bits_per_second
        self.__length_bit = length_bit

        self.__code = None

    def __generate_code(self) -> None:
        # technically, as we are only using one code, we can generate an arbitrary random sequence
        # TODO: change this to a a more deliberate solution if multiple codes are used

        if self.__code is not None:
            return

        if self.__seed is not None:
            np.random.seed(self.__seed)

        bit_width = self._audio.sampling_frequency // self.__bits_per_second
        assert bit_width == self._audio.sampling_frequency / self.__bits_per_second

        random_floats = np.random.rand(self.__length_bit)  # Nx1 as I want the same code for both audio channels
        random_zero_one = np.array(random_floats > 0.5, dtype=np.int16)
        code = random_zero_one * 2 - 1

        code_normalized = np.repeat(code, bit_width)
        self.__code = np.array([code_normalized, code_normalized]).T  # duplicate code to both audio channels
        assert self.__code.shape[1] == 2

    def __get_code(self, length: int) -> Code:
        if self.__code is None:
            raise ValueError("You must run __generate_code() first before you can run this method")

        repeat = length // self.__code.shape[0]
        long_code = np.tile(self.__code.T, repeat).T
        assert long_code.shape[0] == self.__code.shape[0] * repeat

        if long_code.shape[0] == length:
            assert long_code.shape[1] == 2
            return long_code

        assert length - long_code.shape[0] > 0
        out = np.append(long_code, self.__code[:length - long_code.shape[0], :], axis=2)

        assert out.shape[0] == length, f"out.shape[0]: {out.shape[0]}; length: {length}"
        assert out.shape[1] == 2
        return out

    def _create_modified_audio(self) -> Audio:
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

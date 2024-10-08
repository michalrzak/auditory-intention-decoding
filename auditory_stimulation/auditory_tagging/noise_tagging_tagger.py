from typing import Optional

import numpy as np
import numpy.typing as npt

from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger

Code = npt.NDArray[np.int16]


class NoiseTaggingTagger(AAudioTagger):
    """Creates a noise tagging stimulus. This stimulus is generated by first creating a random code and then modulating
    the signal with this code."""
    __rng: np.random.Generator
    __specified_fs: int
    __bit_width: int
    __length_bit: int
    __code: Optional[Code]  # can only contain 1 and -1

    def __init__(self,
                 fs: int,
                 bits_per_second: int,
                 length_bit: int,
                 rng: np.random.Generator) -> None:
        """Constructs the NoiseTaggingTagger object


        :param bits_per_second: The resolution of the noise tagging stimulus.
        :param length_bit: The length of the tag in bits.
        :param rng: A numpy random numer generator.
        """
        if fs <= 0:
            raise ValueError("Sampling frequency must be a non-negative integer.")

        if bits_per_second <= 0:
            raise ValueError("bits_per_second has to be a positive number")

        if fs // bits_per_second != fs / bits_per_second:
            raise ValueError("bits_per_second must fully divide the sampling frequency of the audio, otherwise the code"
                             " cannot be fully created")

        if length_bit <= 0:
            raise ValueError("length_bit has to be a positive number")

        self.__rng = rng

        # save only the bit_width and not the bits_per_seconds, as the latter is not used anywhere later in the code
        self.__bit_width = fs // bits_per_second
        self.__length_bit = length_bit
        self.__specified_fs = fs

        self.__code = None

    def __generate_code(self) -> None:
        """If the code is not already set, generates a new code and sets it.
        technically, as we are only using one code, we can generate an arbitrary random sequence

        TODO: change this to a a more deliberate solution if multiple codes are used
        """

        if self.__code is not None:
            return

        random_floats = self.__rng.random(self.__length_bit)  # Nx1 as I want the same code for both audio channels
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

    @property
    def code(self) -> Optional[Code]:
        if self.__code is None:
            return None

        return np.copy(self.__code)

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        if fs != self.__specified_fs:
            raise ValueError("The specified sampling frequency did not match the sampling frequency of the audio chunk")

        self.__generate_code()
        return audio_array_chunk * self.__get_code(audio_array_chunk.shape[0])

    def __repr__(self) -> str:
        code_print = "["
        for c in self.code[:, 0][::self.__bit_width]:
            if len(code_print) != 1:
                code_print += ", "
            code_print += str(c)
        code_print += "]"

        return self._get_repr("NoiseTaggingTagger", bit_width=str(self.__bit_width), length_bit=str(self.__length_bit),
                              code=code_print)

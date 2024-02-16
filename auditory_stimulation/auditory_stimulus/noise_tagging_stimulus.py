from typing import List, Tuple, Callable, Optional

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio


class NoiseTaggingStimulus(AAuditoryStimulus):
    __seed: Optional[int]
    __bits_per_second: int
    __length_bit: int

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

    def _create_modified_audio(self) -> Audio:
        ...
    
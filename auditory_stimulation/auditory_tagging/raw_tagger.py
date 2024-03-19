import numpy as np
import numpy.typing as npt

from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger


class RawTagger(AAudioTagger):
    """Simple, debug stimulus, which does not change the signal at all."""

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        return audio_array_chunk

    def __repr__(self) -> str:
        return self._get_repr("RawTagger")

from typing import List, Tuple

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, AAudioTaggerFactory


class RawTagger(AAudioTagger):
    """Simple, debug stimulus, which does not change the signal at all."""

    def create(self) -> Audio:
        return self._audio

    def __repr__(self) -> str:
        return f"RawTagger({super().__repr__()})"


class RawTaggerFactory(AAudioTaggerFactory):
    def create_auditory_tagger(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return RawTagger(audio, stimuli_intervals)

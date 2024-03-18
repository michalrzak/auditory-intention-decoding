from typing import List, Tuple

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, AAudioTaggerFactory


class RawTagger(AAudioTagger):
    """Simple, debug stimulus, which does not change the signal at all."""

    def create(self) -> Audio:
        return self._audio

    def __repr__(self) -> str:
        return self._get_repr("RawTagger")


class RawTaggerFactory(AAudioTaggerFactory):
    def create_audio_tagger(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return RawTagger(audio, stimuli_intervals)

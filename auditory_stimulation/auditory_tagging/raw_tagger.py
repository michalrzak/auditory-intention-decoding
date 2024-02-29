from typing import List, Tuple

from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, Audio, AAudioTaggerFactory


class RawTagger(AAudioTagger):
    """Simple, debug stimulus, which does not change the signal at all."""

    def create(self) -> Audio:
        return self._audio


class RawTaggerFactory(AAudioTaggerFactory):
    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return RawTagger(audio, stimuli_intervals)

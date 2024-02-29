from typing import List, Tuple

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio, AAuditoryStimulusFactory


class RawStimulus(AAuditoryStimulus):
    """Simple, debug stimulus, which does not change the signal at all."""

    def _create_modified_audio(self) -> Audio:
        return self._audio


class RawStimulusFactory(AAuditoryStimulusFactory):
    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAuditoryStimulus:
        return RawStimulus(audio, stimuli_intervals)

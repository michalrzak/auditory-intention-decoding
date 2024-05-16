from enum import Enum
from typing import Any, List, Type

from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FMTagger, FlippedFMTagger
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTagger
from auditory_stimulation.auditory_tagging.raw_tagger import RawTagger
from auditory_stimulation.auditory_tagging.shift_tagger import SpectrumShiftTagger, ShiftSumTagger, BinauralTagger
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier

"""This entire module is a bit more hacky than I would have liked. Ideally this would get refactored at some point,
but should be good enough for now.
"""


class ETrigger(Enum):
    NEW_PROMPT = 100
    NEW_STIMULUS = 101
    END_STIMULUS = 102
    ATTENTION_CHECK_ACTION = 120

    OPTION_START = 50
    OPTION_END = 69

    TARGET_START = 70
    TARGET_END = 89

    RESTING_STATE_EYES_OPEN_INTRODUCTION = 20
    RESTING_STATE_EYES_OPEN = 21
    RESTING_STATE_EYES_CLOSED_INTRODUCTION = 22
    RESTING_STATE_EYES_CLOSED = 23

    INTRODUCTION = 1
    EXPERIMENT_INTRODUCTION = 2
    EXPERIMENT = 3
    BREAK_START = 4
    OUTRO = 5
    EXAMPLE = 6
    EXAMPLE_INTRODUCTION = 7
    ATTENTION_CHECK = 8

    INACTIVE = 200


def get_trigger(data: Any, identifier: EModelUpdateIdentifier) -> int:
    if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
        return ETrigger.NEW_STIMULUS.value
    elif identifier == EModelUpdateIdentifier.NEW_PRIMER:
        return ETrigger.NEW_PROMPT.value
    elif identifier == EModelUpdateIdentifier.ATTENTION_CHECK:
        return ETrigger.ATTENTION_CHECK_ACTION.value
    elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
        assert isinstance(data, EExperimentState)
        if data == EExperimentState.INTRODUCTION:
            return ETrigger.INTRODUCTION.value
        elif data == EExperimentState.EXPERIMENT_INTRODUCTION:
            return ETrigger.EXPERIMENT_INTRODUCTION.value
        elif data == EExperimentState.RESTING_STATE_EYES_OPEN:
            return ETrigger.RESTING_STATE_EYES_OPEN.value
        elif data == EExperimentState.RESTING_STATE_EYES_CLOSED:
            return ETrigger.RESTING_STATE_EYES_CLOSED.value
        elif data == EExperimentState.EXPERIMENT:
            return ETrigger.EXPERIMENT.value
        elif data == EExperimentState.INACTIVE:
            return ETrigger.INACTIVE.value
        elif data == EExperimentState.BREAK:
            return ETrigger.BREAK_START.value
        elif data == EExperimentState.RESTING_STATE_EYES_OPEN_INTRODUCTION:
            return ETrigger.RESTING_STATE_EYES_OPEN_INTRODUCTION.value
        elif data == EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION:
            return ETrigger.RESTING_STATE_EYES_CLOSED_INTRODUCTION.value
        elif data == EExperimentState.OUTRO:
            return ETrigger.OUTRO.value
        elif data == EExperimentState.EXAMPLE:
            return ETrigger.EXAMPLE.value
        elif data == EExperimentState.EXAMPLE_INTRODUCTION:
            return ETrigger.EXAMPLE_INTRODUCTION.value
        elif data == EExperimentState.ATTENTION_CHECK:
            return ETrigger.ATTENTION_CHECK.value

    raise NotImplementedError(f"Could not resolve trigger for data: {data} and identifier: {identifier}")


_TAGGER_LIST = [
    RawTagger,
    AMTagger,
    FMTagger,
    FlippedFMTagger,
    SpectrumShiftTagger,
    ShiftSumTagger,
    BinauralTagger,
    NoiseTaggingTagger
]


def _find_is_instance_index(type_list: List[Type], tagger: AAudioTagger):
    for i, ele in enumerate(type_list):
        if isinstance(tagger, ele):
            return i
    raise NotImplementedError("The provided tagger was not recognized!")


def get_target_trigger(tagger: AAudioTagger) -> int:
    offset = _find_is_instance_index(_TAGGER_LIST, tagger)
    return ETrigger.TARGET_START.value + offset


def get_option_trigger(tagger: AAudioTagger) -> int:
    offset = _find_is_instance_index(_TAGGER_LIST, tagger)
    return ETrigger.OPTION_START.value + offset

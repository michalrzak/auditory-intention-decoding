from enum import Enum
from typing import Any, Optional

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class ETrigger(Enum):
    NEW_PROMPT = 100
    NEW_STIMULUS = 101
    END_STIMULUS = 102
    OPTION_START = 111
    OPTION_END = 112
    TARGET_START = 113
    TARGET_END = 114
    ATTENTION_CHECK = 120

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

    INACTIVE = 200

    @staticmethod
    def get_trigger(data: Any, identifier: EModelUpdateIdentifier) -> Optional["ETrigger"]:
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            return ETrigger.NEW_STIMULUS
        elif identifier == EModelUpdateIdentifier.NEW_PRIMER:
            return ETrigger.NEW_PROMPT
        elif identifier == EModelUpdateIdentifier.ATTENTION_CHECK:
            return ETrigger.ATTENTION_CHECK
        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            assert isinstance(data, EExperimentState)
            if data == EExperimentState.INTRODUCTION:
                return ETrigger.INTRODUCTION
            elif data == EExperimentState.EXPERIMENT_INTRODUCTION:
                return ETrigger.EXPERIMENT_INTRODUCTION
            elif data == EExperimentState.RESTING_STATE_EYES_OPEN:
                return ETrigger.RESTING_STATE_EYES_OPEN
            elif data == EExperimentState.RESTING_STATE_EYES_CLOSED:
                return ETrigger.RESTING_STATE_EYES_CLOSED
            elif data == EExperimentState.EXPERIMENT:
                return ETrigger.EXPERIMENT
            elif data == EExperimentState.INACTIVE:
                return ETrigger.INACTIVE
            elif data == EExperimentState.BREAK:
                return ETrigger.BREAK_START
            elif data == EExperimentState.RESTING_STATE_EYES_OPEN_INTRODUCTION:
                return ETrigger.RESTING_STATE_EYES_OPEN_INTRODUCTION
            elif data == EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION:
                return ETrigger.RESTING_STATE_EYES_CLOSED_INTRODUCTION
            elif data == EExperimentState.OUTRO:
                return ETrigger.OUTRO
            elif data == EExperimentState.EXAMPLE:
                return ETrigger.EXAMPLE
            elif data == EExperimentState.EXAMPLE_INTRODUCTION:
                return ETrigger.EXAMPLE_INTRODUCTION
            elif data == EExperimentState.ATTENTION_CHECK:
                return None

        raise NotImplementedError(f"Could not resolve trigger for data: {data} and identifier: {identifier}")

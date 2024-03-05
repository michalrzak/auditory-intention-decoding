from enum import Enum
from typing import Any

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class ETrigger(Enum):
    NEW_STIMULUS = 100
    NEW_PROMPT = 101
    INTRODUCTION = 1
    EXPERIMENT_INTRODUCTION = 2
    RESTING_STATE_EYES_OPEN = 3
    RESTING_STATE_EYES_CLOSED = 4
    EXPERIMENT = 5
    INACTIVE = 200

    @staticmethod
    def get_trigger(data: Any, identifier: EModelUpdateIdentifier) -> "ETrigger":
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            return ETrigger.NEW_STIMULUS
        elif identifier == EModelUpdateIdentifier.NEW_PRIMER:
            return ETrigger.NEW_PROMPT
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

        raise NotImplementedError(f"Could not resolve trigger for data: {data} and identifier: {identifier}")

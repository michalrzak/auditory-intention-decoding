from enum import Enum, auto


class ModelUpdateIdentifier(Enum):
    NEW_PROMPT = auto()
    EXPERIMENT_STATE_CHANGED = auto()
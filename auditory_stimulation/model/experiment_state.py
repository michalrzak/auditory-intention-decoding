from enum import Enum
from os import PathLike
from typing import Any, Dict, Optional

import yaml


class EExperimentState(Enum):
    INACTIVE = "inactive"
    INTRODUCTION = "introduction"
    RESTING_STATE_EYES_OPEN_INTRODUCTION = "resting-state-eyes-open-introduction"
    RESTING_STATE_EYES_OPEN = "resting-state-eyes-open"
    RESTING_STATE_EYES_CLOSED_INTRODUCTION = "resting-state-eyes-closed-introduction"
    RESTING_STATE_EYES_CLOSED = "resting-state-eyes-closed"
    EXPERIMENT_INTRODUCTION = "experiment-introduction"
    EXPERIMENT = "experiment"
    BREAK = "break"


def __experiment_text_validate(experiment_texts_raw: Dict[str, Any]) -> None:
    valid_values = [e.value for e in EExperimentState]
    for value in valid_values:
        if value not in experiment_texts_raw:
            raise KeyError(f"The field {value} needs to be specified.")

    for key in experiment_texts_raw:
        if key not in valid_values:
            raise KeyError(f"The field {key} was not recognized.")

        if not (experiment_texts_raw[key] is None or isinstance(key, str)):
            raise ValueError(f"The specified fields must either be None or a string.")


def __to_enum_dictionary(experiment_texts: Dict[str, Optional[str]]) -> Dict[EExperimentState, Optional[str]]:
    mapping = {e.value: e for e in EExperimentState}
    return {mapping[key]: experiment_texts[key] for key in experiment_texts}


def load_experiment_texts(path_to_yaml: PathLike) -> Dict[EExperimentState, Optional[str]]:
    """Loads the experiments texts specified int the yaml and returns them as a dictionary.
    TODO: document structure of yaml somewhere

    :param path_to_yaml: A path to the to be loaded yaml.
    :return: A dictionary containing the contents of the yaml.
    """
    with open(path_to_yaml, 'r') as file:
        experiment_texts_raw = yaml.safe_load(file)

    __experiment_text_validate(experiment_texts_raw)
    return __to_enum_dictionary(experiment_texts_raw)

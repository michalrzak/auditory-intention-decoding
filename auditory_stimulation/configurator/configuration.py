import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    """Defines the settings used in the project. All parameters, apart from the subjectID, provide default options.
    These can be used by omitting the specific kw_arg."""

    subject_ID: int
    repetitions: int = 2
    resting_state_secs: float = 5
    primer_secs: float = 5
    break_secs: float = 5
    experiment_texts_file_path: pathlib.Path = pathlib.Path("auditory_stimulation/experiment_texts.yaml")
    logging_directory_path: pathlib.Path = pathlib.Path("logs/")
    trigger_directory_path: pathlib.Path = pathlib.Path("triggers/")

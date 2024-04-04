import pathlib
from dataclasses import dataclass
from os import PathLike


@dataclass(frozen=True, kw_only=True)
class Settings:
    """Defines the settings used in the project. All parameters, apart from the subjectID, provide default options.
    These can be used by omitting the specific kw_arg."""

    subject_ID: int
    repetitions: int = 2
    resting_state_secs: int = 5
    primer_secs: int = 5
    break_secs: int = 5
    experiment_texts_file_path: PathLike = pathlib.Path("auditory_stimulation/experiment_texts.yaml")
    logging_directory_path: PathLike = pathlib.Path("logs/")
    trigger_directory_path: PathLike = pathlib.Path("triggers/")

import pathlib
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Configuration:
    """Defines the settings used in the project. See the DEFAULTS constant for default values for all fields."""

    # general parameters
    subject_ID: int
    logging_directory_path: pathlib.Path
    trigger_directory_path: pathlib.Path

    # stimulus generation parameters
    n_stimuli: int
    pause_secs: float
    stimuli_numbers_interval: Tuple[int, int]
    intros_transcription_path: pathlib.Path
    voices_folders: List[pathlib.Path]

    # experiment flow parameters
    repetitions: int
    resting_state_secs: float
    primer_secs: float
    break_secs: float
    experiment_texts_file_path: pathlib.Path

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
    intro_transcription_path: pathlib.Path
    voices_folders: List[pathlib.Path]

    # experiment flow parameters
    repetitions: int
    resting_state_secs: float
    primer_secs: float
    break_secs: float
    experiment_texts_file_path: pathlib.Path


DEFAULTS = Configuration(subject_ID=-1,
                         logging_directory_path=pathlib.Path("logs/"),
                         trigger_directory_path=pathlib.Path("triggers/"),

                         n_stimuli=3,
                         pause_secs=0.5,
                         stimuli_numbers_interval=(100, 1000),
                         intro_transcription_path=pathlib.Path("stimuli_sounds/intro-transcriptions.yaml"),
                         voices_folders=[pathlib.Path(f"stimuli_sounds/eric"), pathlib.Path(f"stimuli_sounds/natasha")],

                         repetitions=2,
                         resting_state_secs=5,
                         primer_secs=5,
                         break_secs=5,
                         experiment_texts_file_path=pathlib.Path("auditory_stimulation/experiment_texts.yaml"))

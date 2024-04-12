import pathlib
from dataclasses import dataclass
from os import PathLike
from typing import List, Tuple

import yaml


@dataclass(frozen=True)
class Configuration:
    """Defines the settings used in the project."""

    # general parameters
    subject_id: int
    logging_directory_path: pathlib.Path
    trigger_directory_path: pathlib.Path

    # stimulus generation parameters
    n_stimuli: int
    pause_secs: float
    intro_indices: List[int]
    stimuli_numbers_interval: Tuple[int, int]
    intros_transcription_path: pathlib.Path
    voices_folders: List[pathlib.Path]

    # experiment flow parameters
    repetitions: int
    resting_state_secs: float
    primer_secs: float
    break_secs: float
    attention_check_secs: float
    experiment_texts_file_path: pathlib.Path


class FailedToGetConfigurationException(Exception):
    pass


def get_configuration_psychopy(defaults: Configuration,
                               window_title: str = "Experiment configuration") -> Configuration:
    """Creates a psychopy dialogue box, which allows to set the configuration by the user.

    :param defaults: Default configuration, which will be autofilled into the fields.
    :param window_title: The title which will be shown on top of the dialogue box.
    :return: A generated configuration from the provided settings.
    """
    # only import this if the function is run; I don't want the entire module to depend on psychopy
    import psychopy.gui

    default_intros = ",".join([str(ele) for ele in defaults.intro_indices])

    separator = "_________________"

    dlg = psychopy.gui.Dlg(title=window_title)

    dlg.addText("<b>Overall parameters</b>")
    dlg.addField(label="Subject ID*", required=True)
    dlg.addField(label="Logging directory path", initial=str(defaults.logging_directory_path))
    dlg.addField(label="Trigger directory path", initial=str(defaults.trigger_directory_path))

    dlg.addText(separator)

    dlg.addText("<b>Stimulus generation parameters</b>")
    dlg.addField(label="n_stimuli", initial=defaults.n_stimuli)
    dlg.addField(label="Pause secs", initial=defaults.pause_secs)
    dlg.addField(label="Valid indices (comma seperated)", initial=default_intros)
    dlg.addField(label="Stimuli numbers interval lower", initial=defaults.stimuli_numbers_interval[0])
    dlg.addField(label="Stimuli numbers interval upper", initial=defaults.stimuli_numbers_interval[1])
    dlg.addField(label="Intro transcription file path", initial=str(defaults.intros_transcription_path))
    dlg.addText("Voices")
    dlg.addField(label="  - eric", initial=False)
    dlg.addField(label="  - natasha", initial=True)

    dlg.addText(separator)

    dlg.addText("<b>Experiment flow parameters</b>")
    dlg.addField(label="Repetitions", initial=defaults.repetitions)
    dlg.addField(label="Resting state secs", initial=defaults.resting_state_secs)
    dlg.addField(label="Primer secs", initial=defaults.primer_secs)
    dlg.addField(label="Break secs", initial=defaults.break_secs)
    dlg.addField(label="Attention check secs", initial=defaults.attention_check_secs)
    dlg.addField(label="Experiment texts file path", initial=str(defaults.experiment_texts_file_path))

    results = dlg.show()

    if results is None:
        raise FailedToGetConfigurationException("The user has aborted the dialogue!")

    intro_indices = [int(ele) for ele in results[5].split(",")]

    voices_choices = [pathlib.Path("stimuli_sounds/eric"), pathlib.Path("stimuli_sounds/natasha")]
    voices = [voice for voice, choice in zip(voices_choices, [results[9], results[10]]) if choice]

    assert len(results) == 17
    config = Configuration(subject_id=int(results[0]),
                           logging_directory_path=pathlib.Path(results[1]),
                           trigger_directory_path=pathlib.Path(results[2]),
                           n_stimuli=int(results[3]),
                           pause_secs=float(results[4]),
                           intro_indices=intro_indices,
                           stimuli_numbers_interval=(int(results[6]), int(results[7])),
                           intros_transcription_path=pathlib.Path(results[8]),
                           voices_folders=voices,
                           repetitions=int(results[11]),
                           resting_state_secs=float(results[12]),
                           primer_secs=float(results[13]),
                           break_secs=float(results[14]),
                           attention_check_secs=float(results[15]),
                           experiment_texts_file_path=pathlib.Path(results[16]))

    return config


def get_configuration_yaml(configuration_path: PathLike) -> Configuration:
    """Given a path to a YAML, loads the configuration defined in it.

    :param configuration_path: Path to YAML.
    :return: The loaded configuration object.
    """
    with open(configuration_path, 'r') as file:
        configuration_raw = yaml.safe_load(file)

    stimuli_number_interval = tuple(configuration_raw["stimuli_numbers_interval"])
    if len(stimuli_number_interval) != 2:
        raise FailedToGetConfigurationException(
            "The stimuli_numbers_interval is incorrect. It must consist of two numbers!")

    voices_folders = [pathlib.Path(ele) for ele in configuration_raw["voices_folders"]]

    configuration = Configuration(
        subject_id=int(configuration_raw["subject_id"]),
        logging_directory_path=pathlib.Path(configuration_raw["logging_directory_path"]),
        trigger_directory_path=pathlib.Path(configuration_raw["trigger_directory_path"]),

        n_stimuli=int(configuration_raw["n_stimuli"]),
        pause_secs=float(configuration_raw["pause_secs"]),
        intro_indices=configuration_raw["intro_indices"],
        stimuli_numbers_interval=(configuration_raw["stimuli_numbers_interval"]),
        intros_transcription_path=pathlib.Path(configuration_raw["intros_transcription_path"]),
        voices_folders=voices_folders,

        repetitions=int(configuration_raw["repetitions"]),
        resting_state_secs=float(configuration_raw["resting_state_secs"]),
        primer_secs=float(configuration_raw["primer_secs"]),
        break_secs=float(configuration_raw["break_secs"]),
        attention_check_secs=float(configuration_raw["attention_check_secs"]),
        experiment_texts_file_path=pathlib.Path(configuration_raw["experiment_texts_file_path"]))

    return configuration


def get_configuration_cli() -> Configuration:
    raise NotImplementedError()

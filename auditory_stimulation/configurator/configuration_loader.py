import pathlib

import psychopy.gui

from auditory_stimulation.configurator.configuration import Configuration

WINDOW_TITLE = "Experiment configuration"


class FailedToGetConfigurationException(Exception):
    pass


def get_configuration_psychopy() -> Configuration:
    dlg = psychopy.gui.Dlg(title=WINDOW_TITLE)

    dlg.addField(label="Subject ID", required=True)
    dlg.addField(label="Repetitions", initial=Configuration.repetitions)
    dlg.addField(label="Resting state secs", initial=Configuration.resting_state_secs)
    dlg.addField(label="Primer secs", initial=Configuration.primer_secs)
    dlg.addField(label="Break secs", initial=Configuration.break_secs)
    dlg.addField(label="Experiment texts file path", initial=str(Configuration.experiment_texts_file_path))
    dlg.addField(label="Logging directory path", initial=str(Configuration.logging_directory_path))
    dlg.addField(label="Trigger directory path", initial=str(Configuration.trigger_directory_path))

    results = dlg.show()

    if results is None:
        raise FailedToGetConfigurationException("The user has aborted the dialogue!")

    assert len(results) == 8
    config = Configuration(subject_ID=int(results[0]),
                           repetitions=int(results[1]),
                           resting_state_secs=int(results[2]),
                           primer_secs=int(results[3]),
                           break_secs=int(results[4]),
                           experiment_texts_file_path=pathlib.Path(results[5]),
                           logging_directory_path=pathlib.Path(results[6]),
                           trigger_directory_path=pathlib.Path(results[7]))

    return config


def get_configuration_yaml() -> Configuration:
    raise NotImplementedError()


def get_configuration_cli() -> Configuration:
    raise NotImplementedError()

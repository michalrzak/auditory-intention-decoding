import pathlib

import psychopy.gui

from auditory_stimulation.configurator import configuration

WINDOW_TITLE = "Experiment configuration"


class FailedToGetConfigurationException(Exception):
    pass


def get_configuration_psychopy() -> configuration.Configuration:
    separator = "_________________"

    dlg = psychopy.gui.Dlg(title=WINDOW_TITLE)

    dlg.addText("<b>Overall parameters</b>")
    dlg.addField(label="Subject ID*", required=True)
    dlg.addField(label="Logging directory path", initial=str(configuration.DEFAULTS.logging_directory_path))
    dlg.addField(label="Trigger directory path", initial=str(configuration.DEFAULTS.trigger_directory_path))

    dlg.addText(separator)

    dlg.addText("<b>Stimulus generation parameters</b>")
    dlg.addField(label="n_stimuli", initial=configuration.DEFAULTS.n_stimuli)
    dlg.addField(label="Pause secs", initial=configuration.DEFAULTS.pause_secs)
    dlg.addField(label="Stimuli numbers interval lower", initial=configuration.DEFAULTS.stimuli_numbers_interval[0])
    dlg.addField(label="Stimuli numbers interval upper", initial=configuration.DEFAULTS.stimuli_numbers_interval[1])
    dlg.addField(label="Intro transcription file path", initial=str(configuration.DEFAULTS.intro_transcription_path))
    dlg.addText("Voices")
    dlg.addField(label="  - eric", initial=True)
    dlg.addField(label="  - natasha", initial=True)

    dlg.addText(separator)

    dlg.addText("<b>Experiment flow parameters</b>")
    dlg.addField(label="Repetitions", initial=configuration.DEFAULTS.repetitions)
    dlg.addField(label="Resting state secs", initial=configuration.DEFAULTS.resting_state_secs)
    dlg.addField(label="Primer secs", initial=configuration.DEFAULTS.primer_secs)
    dlg.addField(label="Break secs", initial=configuration.DEFAULTS.break_secs)
    dlg.addField(label="Experiment texts file path", initial=str(configuration.DEFAULTS.experiment_texts_file_path))

    results = dlg.show()

    if results is None:
        raise FailedToGetConfigurationException("The user has aborted the dialogue!")

    voices = [voice for voice, choice in zip(configuration.DEFAULTS.voices_folders, [results[8], results[9]]) if choice]

    assert len(results) == 15
    config = configuration.Configuration(subject_ID=int(results[0]),
                                         logging_directory_path=pathlib.Path(results[1]),
                                         trigger_directory_path=pathlib.Path(results[2]),
                                         n_stimuli=int(results[3]),
                                         pause_secs=float(results[4]),
                                         stimuli_numbers_interval=(int(results[5]), int(results[6])),
                                         intro_transcription_path=pathlib.Path(results[7]),
                                         voices_folders=voices,
                                         repetitions=int(results[10]),
                                         resting_state_secs=float(results[11]),
                                         primer_secs=float(results[12]),
                                         break_secs=float(results[13]),
                                         experiment_texts_file_path=pathlib.Path(results[14]))

    return config


def get_configuration_yaml() -> configuration.Configuration:
    raise NotImplementedError()


def get_configuration_cli() -> configuration.Configuration:
    raise NotImplementedError()

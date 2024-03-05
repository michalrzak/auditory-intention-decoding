import pathlib

import psychopy.visual

from auditory_stimulation.auditory_tagging.assr_tagger import AMTaggerFactory, FMTaggerFactory
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTaggerFactory
from auditory_stimulation.auditory_tagging.tag_generators import clicking_signal
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.logging import Logger
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import load_stimuli
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player

LOGGING_DIRECTORY = pathlib.Path("logs/")


def main() -> None:
    model = Model()

    logger = Logger(LOGGING_DIRECTORY)
    model.register(logger)

    experiment_texts = load_experiment_texts(pathlib.Path("auditory_stimulation/experiment_texts.yaml"))
    window = psychopy.visual.Window(fullscr=True)
    view = PsychopyView(psychopy_player, experiment_texts, window)

    model.register(view)

    stimuli = load_stimuli(pathlib.Path("auditory_stimulation/stimuli.yaml"))

    experiment = Experiment(model, view, stimuli, [AMTaggerFactory(42, clicking_signal),
                                                   FMTaggerFactory(40),
                                                   NoiseTaggingTaggerFactory(126, 256)])
    experiment.create_stimuli()
    experiment.run()


if __name__ == "__main__":
    main()

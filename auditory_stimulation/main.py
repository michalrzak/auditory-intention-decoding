import psychopy.visual

from auditory_stimulation.auditory_tagging.assr_tagger import ASSRTaggerFactory
from auditory_stimulation.auditory_tagging.modulation_strategies import amplitude_modulation
from auditory_stimulation.auditory_tagging.tag_generators import clicking_signal
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.model import Model
from auditory_stimulation.stimulus import load_stimuli
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player


def main():
    model = Model()

    experiment_texts = load_experiment_texts("auditory_stimulation/experiment_texts.yaml")
    window = psychopy.visual.Window(fullscr=True)
    view = PsychopyView(psychopy_player, experiment_texts, window)

    model.register(view)

    stimuli = load_stimuli("auditory_stimulation/stimuli.yaml")

    experiment = Experiment(model, view, stimuli, [ASSRTaggerFactory(42, clicking_signal, amplitude_modulation)])
    experiment.create_stimuli()
    experiment.run()


if __name__ == "__main__":
    main()

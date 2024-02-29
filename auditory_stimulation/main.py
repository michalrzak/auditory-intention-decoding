import psychopy.visual

from auditory_stimulation.auditory_tagging.assr_tagger import ASSRTaggerFactory
from auditory_stimulation.auditory_tagging.modulation_strategies import amplitude_modulation
from auditory_stimulation.auditory_tagging.tag_generators import clicking_signal
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.model import Model
from auditory_stimulation.stimulus import load_stimuli
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player


def main():
    model = Model()

    window = psychopy.visual.Window()
    view = PsychopyView(psychopy_player, window)

    model.register(view)

    stimuli = load_stimuli("auditory_stimulation/stimuli.yaml")

    experiment = Experiment(model, view, stimuli, [ASSRTaggerFactory(42, clicking_signal, amplitude_modulation)])
    experiment.create_stimuli()
    experiment.run()


if __name__ == "__main__":
    main()

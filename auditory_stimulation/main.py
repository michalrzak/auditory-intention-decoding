import psychopy.visual

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

    experiment = Experiment(model, view, stimuli)
    experiment.run()


if __name__ == "__main__":
    main()

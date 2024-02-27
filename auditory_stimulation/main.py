import psychopy.visual

from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.cli_view import CLIView
from auditory_stimulation.view.psychopy_view import PsychopyView


def main():
    model = Model()
    window = psychopy.visual.Window()
    view = PsychopyView(window)
    model.register(view)
    experiment = Experiment(model, view)
    experiment.run()


if __name__ == "__main__":
    main()

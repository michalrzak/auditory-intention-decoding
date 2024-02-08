from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.cli_view import CLIView


def main():
    model = Model()
    view = CLIView()
    model.register(view)
    experiment = Experiment(model, view)
    experiment.run()


if __name__ == "__main__":
    main()

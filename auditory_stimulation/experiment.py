from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import AView

STIMULUS_REPEAT = 5

RESTING_STATE_SECS = 5
PRIMER_SECS = 5
BREAK_SECS = 5


class Experiment:
    """A controller class of the MVC pattern, responsible for handling the experiment logic, updating the model and
    calling blocking operations (wait for keypress, wait) on the view.
    """
    __model: Model
    __view: AView

    def __init__(self, model: Model, view: AView) -> None:
        """Constructs an Experiment instance.

        :param model: The underlying model of the experiment, saving all relevant experiment data.
        :param view: The used view of the experiment, showing the current state of the model and interacting with users

        """
        self.__model = model
        self.__view = view

        assert self.__model.experiment_state == EExperimentState.INACTIVE

    def run(self) -> None:
        """Runs the experiment.
        """
        self.__model.create_stimuli()

        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        for stimulus in self.__model.created_stimuli:
            self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
            self.__model.present_primer(stimulus.primer)
            self.__view.wait(PRIMER_SECS)

            for i in range(STIMULUS_REPEAT):
                self.__model.present_stimulus(stimulus)

            self.__model.change_experiment_state(EExperimentState.BREAK)
            self.__view.wait(BREAK_SECS)
            self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

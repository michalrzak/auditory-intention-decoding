from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import AView


class Experiment:
    """A controller class of the MVC pattern, responsible for handling the experiment logic, updating the model and
    calling blocking operations (wait for keypress, wait) on the view.
    """
    __model: Model
    __view: AView
    __stimulus_repeat: int
    __resting_state_secs: float
    __primer_secs: float
    __break_secs: float

    def __init__(self,
                 model: Model,
                 view: AView,
                 stimulus_repeat: int,
                 resting_state_secs: float,
                 primer_secs: float,
                 break_secs: float) -> None:
        """Constructs an Experiment instance.

        :param model: The underlying model of the experiment, saving all relevant experiment data.
        :param view: The used view of the experiment, showing the current state of the model and interacting with users
        :param stimulus_repeat: How often each stimulus is repeated
        :param resting_state_secs: How long to measure the resting state
        :param primer_secs: How long the primer is shown
        :param break_secs: How long the break is

        """
        self.__model = model
        self.__view = view

        self.__stimulus_repeat = stimulus_repeat
        self.__resting_state_secs = resting_state_secs
        self.__primer_secs = primer_secs
        self.__break_secs = break_secs

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
        self.__view.wait(self.__resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(self.__resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        for stimulus in self.__model.created_stimuli:
            self.__model.change_experiment_state(EExperimentState.EXPERIMENT)

            for i in range(self.__stimulus_repeat):
                self.__model.present_primer(stimulus.primer)
                self.__view.wait(self.__primer_secs)

                self.__model.present_stimulus(stimulus)

            self.__model.change_experiment_state(EExperimentState.BREAK)
            self.__view.wait(self.__break_secs)
            self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(self.__resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(self.__resting_state_secs)

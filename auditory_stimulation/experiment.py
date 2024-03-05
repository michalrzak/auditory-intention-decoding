from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import AView

STIMULUS_REPEAT = 5

RESTING_STATE_SECS = 5
PRIMER_SECS = 5


class Experiment:
    """A controller class of the MVC pattern, responsible for handling the experiment logic, updating the model and
    calling blocking operations (wait for keypress, wait) on the view.

    Note: This class is not ideal. I think the stimuli should be saved and also possibly created in the model class.
    Then the only thing needed would be calling something like "next stimulus" and this would do all the necessery
    updates in the model by itself. Unfortunately, my rule, where I want to have all experiment logic in this class,
    as it would require to delegate the decision to, for example, how long to wait after a primer to the view. I
    specifically wanted to avoid that, as I feel that this fits better into the Experiment class.
    Should this ever get implemented, the code would be a lot better decoupled as this would no longer depend on
    stimulus.
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
        """Runs the experiment. Before running the experiment `create_stimuli()` has to be executed first
        """
        self.__model.create_stimuli()

        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
        for stimulus in self.__model.created_stimuli:
            self.__model.present_primer(stimulus.primer)
            self.__view.wait(PRIMER_SECS)

            for i in range(STIMULUS_REPEAT):
                self.__model.present_stimulus(stimulus)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

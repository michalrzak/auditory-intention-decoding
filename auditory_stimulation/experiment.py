from auditory_stimulation.auditory_stimulus.helper.load_wav_as_numpy_array import load_wav_as_numpy_array
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.stimulus import FullStimulus
from auditory_stimulation.view.view import AView

# TODO: this needs to be a lot more complex, linking a primer the audio, the stimuli timestamps
audio = load_wav_as_numpy_array("../test_sounds/test.wav")
STIMULI = [FullStimulus(audio,
                        "Hello this is Pizzeria Romano, would you like to take an order, see the menu, or do a reservation?",
                        "You want to reserve a table at a Pizzeria.",
                        ["take an order", "see the menu", "do a reservation"])]

STIMULUS_REPEAT = 5

RESTING_STATE_SECS = 5
PRIMER_SECS = 5


class Experiment:
    __model: Model
    __view: AView

    def __init__(self, model: Model, view: AView) -> None:
        self.__model = model
        self.__view = view

        assert self.__model.experiment_state == EExperimentState.INACTIVE

    def run(self) -> None:
        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
        for stimulus in STIMULI:
            self.__model.new_primer(stimulus.primer)
            self.__view.wait(PRIMER_SECS)

            for i in range(STIMULUS_REPEAT):
                self.__model.new_stimulus(stimulus)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

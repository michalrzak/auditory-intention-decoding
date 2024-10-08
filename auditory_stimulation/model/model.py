from abc import ABC, abstractmethod
from bisect import bisect_right
from typing import List, Any, Optional, Collection, Tuple

from auditory_stimulation.audio import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import AStimulus


class AObserver(ABC):
    @abstractmethod
    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        ...


class Model:
    """Class, containing all  relevant data for the experiment. Is an observable of the observer pattern
    """
    __created_stimuli: Collection[AStimulus]
    __example_stimuli: Collection[AStimulus]

    __stimulus_history: List[AStimulus]
    __primer_history: List[str]
    __attention_check_indices: List[int]
    __experiment_state: EExperimentState

    __observers: List[Tuple[AObserver, int]]

    def __init__(self, stimuli: Collection[AStimulus], example_stimuli: Collection[AStimulus]) -> None:
        """Creates a model object.

        :param stimuli: A list of stimuli which will be used throughout the experiment.
        """
        self.__stimulus_history = []
        self.__primer_history = []
        self.__attention_check_indices = []
        self.__experiment_state = EExperimentState.INACTIVE
        self.__observers = []

        self.__created_stimuli = stimuli
        self.__example_stimuli = example_stimuli

    def __notify(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        for observer, _ in self.__observers:
            observer.update(data, identifier)

    def register(self, observer: AObserver, priority: int = 99) -> None:
        """Observable. Register a view, which will get notified about changes in the model.

        :param observer: The to be registered observer.
        :param priority: Positive integer in the range [1; 99]. The smaller the number the higher priority an observer
         has. Observers are executed in the order of their priority. This parameter is to be used if some
         observers are time sensitive (set a high priority, i.e. close to 1) or if some observers are blocking,
         and should be executed last (set a low priority, i.e. close to 2). Can be also used to define the order in
         which the observers get updated
        """

        if not (1 <= priority <= 99):
            raise ValueError("Priority needs to be in the range 1 to 99")

        # insert the new observer into the observer list, while keeping the list sorted by the priority
        keys = [x[1] for x in self.__observers]
        # finds the insertion to the right of the last key; where key <= priority
        insertion_point = bisect_right(keys, priority)
        # insert the observer and priority based on the computed key
        self.__observers.insert(insertion_point, (observer, priority))

    def present_stimulus(self, stimulus: AStimulus) -> None:
        """Mark the given stimulus as presented.

        :param stimulus: The to be added stimulus.
        :return: None
        """
        self.__stimulus_history.append(stimulus)
        self.__notify(stimulus, EModelUpdateIdentifier.NEW_STIMULUS)

    def present_primer(self, primer: str) -> None:
        """Adds a primer statement to the model.

        :param primer: The to be added primer statement.
        :return: None
        """
        self.__primer_history.append(primer)
        self.__notify(primer, EModelUpdateIdentifier.NEW_PRIMER)

    def change_experiment_state(self, new_state: EExperimentState) -> None:
        """Change the current experiment state

        :param new_state: The to be changed to experiment state.
        :return: None
        """
        assert new_state != self.__experiment_state
        self.__experiment_state = new_state
        self.__notify(self.__experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)

    def add_attention_check(self, stimulus_index: int) -> None:
        """Save that an attention check was conducted on the stimulus with the given index.

        :param stimulus_index: The stimulus on which the attention check was conducted.
        :return:
        """
        if not (0 <= stimulus_index < len(self.__created_stimuli)):
            raise ValueError("Must provide a valid index!")

        self.__attention_check_indices.append(stimulus_index)
        self.__notify(stimulus_index, EModelUpdateIdentifier.ATTENTION_CHECK)

    @property
    def current_prompt(self) -> Optional[str]:
        if len(self.__stimulus_history) == 0:
            return None
        return self.__stimulus_history[-1].prompt

    @property
    def current_audio(self) -> Optional[Audio]:
        if len(self.__stimulus_history) == 0:
            return None
        return self.__stimulus_history[-1].audio

    @property
    def current_primer(self) -> Optional[str]:
        if len(self.__primer_history) == 0:
            return None
        return self.__primer_history[-1]

    @property
    def experiment_state(self) -> EExperimentState:
        return self.__experiment_state

    @property
    def created_stimuli(self) -> Collection[AStimulus]:
        return self.__created_stimuli

    @property
    def example_stimuli(self) -> Collection[AStimulus]:
        return self.__example_stimuli

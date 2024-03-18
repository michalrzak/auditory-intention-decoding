import copy
import random
from abc import ABC, abstractmethod
from bisect import bisect_right
from typing import List, Any, Optional, Collection, Tuple

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTaggerFactory
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus, Stimulus


class AObserver(ABC):
    @abstractmethod
    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        ...


class Model:
    """Class, containing all  relevant data for the experiment. Is an observable of the observer pattern
    """
    __raw_stimuli: Collection[Stimulus]
    __auditory_stimulus_factories: Collection[AAudioTaggerFactory]
    __created_stimuli: Optional[Collection[CreatedStimulus]]

    __stimulus_history: List[CreatedStimulus]
    __primer_history: List[str]
    __experiment_state: EExperimentState

    __observers: List[Tuple[AObserver, int]]

    def __init__(self,
                 raw_stimuli: Collection[Stimulus],
                 auditory_tagger_factories: Collection[AAudioTaggerFactory]) -> None:
        """Creates a model object.

        :param raw_stimuli: A list of stimuli which will be used throughout the experiment.
        :param auditory_tagger_factories: The to be used auditory_stimuli. Note that the number of
         auditory_stimulus_factories must divide the number of stimuli, to ensure that each auditory_tagging can be
         shown the same number of times
        """
        self.__stimulus_history = []
        self.__primer_history = []
        self.__experiment_state = EExperimentState.INACTIVE
        self.__observers = []

        self.__raw_stimuli = raw_stimuli

        if len(auditory_tagger_factories) == 0:
            raise ValueError("At least one auditory stimulus factory needs to be supplied!")
        if len(raw_stimuli) % len(auditory_tagger_factories) != 0:
            # this can potentially be changed if I e.g. change it to replay the stimuli for each stimulus
            raise ValueError("The amount of factories must fully divide the amount of stimuli,"
                             " to avoid having one stimulus type less!")
        self.__auditory_stimulus_factories = copy.copy(auditory_tagger_factories)

        self.__created_stimuli = None

    def create_stimuli(self) -> None:
        """Has to be run before using created_stimuli. Creates the auditory modulated stimuli from the passed stimuli.
        Depending on the used auditory stimuli and the amount of stimuli, this could take a while to execute.
        """
        if self.__created_stimuli is not None:
            raise RuntimeError("You can only call create_stimuli() once!")

        assert len(self.__raw_stimuli) % len(self.__auditory_stimulus_factories) == 0

        repeats = len(self.__raw_stimuli) // len(self.__auditory_stimulus_factories)

        applied_factories = []
        for factory in self.__auditory_stimulus_factories:
            applied_factories += [factory] * repeats

        random.shuffle(applied_factories)

        created_stimuli = []
        for factory, stimulus in zip(applied_factories, self.__raw_stimuli):
            auditory_tagger = factory.create_audio_tagger(stimulus.audio, stimulus.time_stamps)
            modified_audio = auditory_tagger.create()
            created_stimuli.append(CreatedStimulus(stimulus, modified_audio, auditory_tagger))

        self.__created_stimuli = created_stimuli

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

    def present_stimulus(self, stimulus: CreatedStimulus) -> None:
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
    def created_stimuli(self) -> Optional[Collection[CreatedStimulus]]:
        return self.__created_stimuli

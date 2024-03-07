import threading
import time
from abc import abstractmethod
from typing import Any

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus


class ATriggerSender(AObserver):

    @abstractmethod
    def _send_trigger(self, trigger: ETrigger) -> None:
        """To be implemented by the subclasses. Responsible for properly sending the trigger to the used trigger stream.

        :param trigger: The to be sent trigger.
        :return: None
        """
        ...

    def __queue_trigger(self, trigger: ETrigger, secs: float) -> None:
        def wait_and_send():
            time.sleep(secs)
            self._send_trigger(trigger)

        thread = threading.Thread(target=wait_and_send)
        thread.start()

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        # send the trigger instantly, but on another thread
        self.__queue_trigger(ETrigger.get_trigger(data, identifier), 0)

        # in case a new stimulus is received, also queue sending trigger after it finishes playing and at the beginning
        #  of each option
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            assert isinstance(data, CreatedStimulus)
            for time_stamp in data.time_stamps:
                self.__queue_trigger(ETrigger.OPTION_START, time_stamp[0])
                self.__queue_trigger(ETrigger.OPTION_END, time_stamp[1])

            self.__queue_trigger(ETrigger.END_STIMULUS, data.audio.secs)

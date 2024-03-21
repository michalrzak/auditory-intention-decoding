import queue
import threading
import time
from abc import abstractmethod
from typing import Any

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus


class ThreadDiedException(Exception):
    ...


class ATriggerSender(AObserver):
    __trigger_queue: queue.Queue

    __thread_timout: int
    __thread: threading.Thread
    __exit_flag: bool

    def __init__(self, thread_timout: int) -> None:
        self.__thread_timeout = thread_timout

        self.__thread = threading.Thread(target=self.__trigger_worker)
        self.__trigger_queue = queue.Queue()
        self.__exit_flag = False

    def __trigger_worker(self):
        while not self.__exit_flag:
            try:
                item = self.__trigger_queue.get(timeout=self.__thread_timout)
            except queue.Empty:
                continue
            self._send_trigger(item)
            self.__trigger_queue.task_done()

    def __queue_trigger(self, trigger: ETrigger, offset: float = 0) -> None:
        if offset == 0:
            self.__trigger_queue.put(trigger)
            return

        def wait_and_put():
            time.sleep(offset)
            self.__trigger_queue.put(trigger)

        thread = threading.Thread(target=wait_and_put)
        thread.start()

    @abstractmethod
    def _send_trigger(self, trigger: ETrigger) -> None:
        """To be implemented by the subclasses. Responsible for properly sending the trigger to the used trigger stream.

        :param trigger: The to be sent trigger.
        :return: None
        """
        ...

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        self.__trigger_queue.put(ETrigger.get_trigger(data, identifier))
        self.__queue_trigger(ETrigger.get_trigger(data, identifier))

        # in case a new stimulus is received, also queue sending trigger after it finishes playing and at the beginning
        #  of each option
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            assert isinstance(data, CreatedStimulus)
            for time_stamp in data.time_stamps:
                self.__queue_trigger(ETrigger.OPTION_START, time_stamp[0])
                self.__queue_trigger(ETrigger.OPTION_END, time_stamp[1])

            self.__queue_trigger(ETrigger.END_STIMULUS, data.audio.secs)

    def __enter__(self):
        self.__thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        if not self.__thread.is_alive():
            raise ThreadDiedException("The thread died unexpectedly!")

        self.__trigger_queue.join()
        self.__exit_flag = True
        self.__thread.join()
        assert not self.__thread.is_alive()

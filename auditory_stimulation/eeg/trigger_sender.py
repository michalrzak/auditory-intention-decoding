import queue
import threading
import time
from abc import abstractmethod
from typing import Any, List

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus


class ThreadDiedException(Exception):
    ...


class ATriggerSender(AObserver):
    __trigger_queue: queue.Queue

    __thread_timeout: float
    __thread: threading.Thread
    __exit_flag: bool

    __offset_trigger_threads: List[threading.Thread]

    def __init__(self, thread_timeout: float) -> None:
        self.__thread_timeout = thread_timeout

        self.__thread = threading.Thread(target=self.__trigger_worker)
        self.__trigger_queue = queue.Queue()
        self.__exit_flag = False

        self.__offset_trigger_threads = []

    def __trigger_worker(self):
        while not self.__exit_flag:
            try:
                item = self.__trigger_queue.get(timeout=self.__thread_timeout)
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
        self.__offset_trigger_threads.append(thread)

    @abstractmethod
    def _send_trigger(self, trigger: ETrigger) -> None:
        """To be implemented by the subclasses. Responsible for properly sending the trigger to the used trigger stream.

        :param trigger: The to be sent trigger.
        :return: None
        """
        ...

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if not self.__thread.is_alive():
            raise ThreadDiedException("The trigger sending thread died. Did you use the `with` syntax to start the "
                                      "thread?")

        self.__queue_trigger(ETrigger.get_trigger(data, identifier))

        # in case a new stimulus is received, also queue sending trigger after it finishes playing and at the beginning
        #  of each option
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            assert isinstance(data, CreatedStimulus)
            for time_stamp in data.time_stamps:
                self.__queue_trigger(ETrigger.OPTION_START, time_stamp[0])
                self.__queue_trigger(ETrigger.OPTION_END, time_stamp[1])

            self.__queue_trigger(ETrigger.END_STIMULUS, data.audio.secs)

    def __enter__(self) -> "ATriggerSender":
        self.__thread.start()
        return self

    def __exit__(self, *args) -> None:
        self.__del__()

    def __del__(self) -> None:
        if not self.__thread.is_alive():
            return

        for thread in self.__offset_trigger_threads:
            thread.join()

        self.__trigger_queue.join()
        self.__exit_flag = True
        self.__thread.join()
        assert not self.__thread.is_alive()

import queue
import threading
from abc import abstractmethod
from contextlib import contextmanager
from datetime import datetime
from threading import Timer
from typing import Any, List

from auditory_stimulation.eeg.common import ETrigger, get_trigger, get_target_trigger, get_option_trigger
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import AStimulus, Stimulus


class ThreadDiedException(Exception):
    ...


class ATriggerSender(AObserver):
    """An abstract trigger sender object, where subclasses can define specific trigger sending mechanisms. It acts as an
    observer on the model and gets notified about changes in it. This class then processes the changes and sends the
    appropriate triggers. Since trigger sending is always blocking and the context of the project requires me to
    schedule triggers, the triggers are always sent from a separate thread, to ensure consistency. This makes the class
    relatively complicated, requiring pythons (thread safe) queue to operate.

    Since the class has to start and stop a thread, during the time when triggers can be sent, please use the `with`
    syntax with this class:
    ```python
    trigger_sender: ATriggerSender = ConcreteTriggerSender(thread_timout, ...)
    with trigger_sender.start() as ts:
        # register ts as an observer
        # use ts
        # ...
    ```

    The with syntax automatically starts the thread and stops the thread. When cleaning up, it blocks main program
    execution before all trigger sending has been completed, ensuring no triggers are lost.

    As this class uses multithreading to operate, the trigger sending may not be 100% accurate. This is not a big deal
    in the context of the project, however it is something to keep in mind if you want to adapt this class. If the
    trigger for `audio ended` and the different option within the audio is not needed, this class can be easily reworked
    within multithreading.

    I am not too happy with this class and I think ideally this should be solvable with no threads, or potentially just
    one single thread. This class is context dependant.
    """
    __trigger_queue: queue.Queue

    __thread_timeout_secs: float
    __thread: threading.Thread = None  # this is None in order to catch __del__ call after failed __init__ call
    __exit_flag: bool

    __trigger_enqueue_threads: List[threading.Thread]

    def __init__(self, thread_timeout_secs: float) -> None:
        """
        :param thread_timeout_secs: Specifies how long the thread tries to send something, before it attempts to quit.
        """
        if thread_timeout_secs < 0:
            raise ValueError("thread_timout_secs has to be a non-negative number!")

        self.__thread_timeout_secs = thread_timeout_secs

        self.__thread = threading.Thread(target=self.__trigger_worker)
        self.__trigger_queue = queue.Queue()
        self.__exit_flag = False

        self.__trigger_enqueue_threads = []

    def __trigger_worker(self) -> None:
        """The method which runs on the trigger sender thread. To quit the thread, set self.__exit_flag to True.

        :return: None
        """
        while not self.__exit_flag:
            try:
                item, ts = self.__trigger_queue.get(timeout=self.__thread_timeout_secs)
            except queue.Empty:
                continue
            self._send_trigger(item, ts)
            self.__trigger_queue.task_done()

    def __queue_trigger(self, trigger: int, offset_secs: float = 0) -> None:
        """Enqueues the given trigger, to be sent after the specified amount.

        :param trigger: The to be sent trigger.
        :param offset_secs: How long, in seconds, to wait before sending the trigger.
        :return: None
        """
        current_timestamp_ms = datetime.timestamp(datetime.today()) * 1000

        if offset_secs == 0:
            self.__trigger_queue.put((trigger, current_timestamp_ms))
            return

        item = (trigger, current_timestamp_ms + offset_secs * 1000)

        t = Timer(offset_secs, lambda tr, ts: self.__trigger_queue.put((tr, ts)), args=item)
        t.start()
        self.__trigger_enqueue_threads.append(t)

    @abstractmethod
    def _send_trigger(self, trigger: ETrigger, timestamp: float) -> None:
        """To be implemented by the subclasses. Responsible for properly sending the trigger to the used trigger
        mechanism.

        :param trigger: The to be sent trigger.
        :param timestamp: Timestamp of the trigger.
        :return: None
        """
        pass

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        """The method, called by the observer."""
        if not self.__thread.is_alive():
            raise ThreadDiedException("The trigger sending thread died. Did you use the `with` syntax to start the "
                                      "thread?")
        self.__queue_trigger(get_trigger(data, identifier))

        # in case a new stimulus is received, also queue sending trigger after it finishes playing and at the beginning
        #  of each option
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            assert isinstance(data, AStimulus)
            for i, time_stamp in enumerate(data.time_stamps):

                # this could probably be done a bit better, but as the AttentionCheckStimulus is a bit of an
                # afterthought, this `if` is not very clean.
                if isinstance(data, Stimulus) and i == data.target_index:
                    self.__queue_trigger(get_target_trigger(data.used_tagger), time_stamp[0])
                    self.__queue_trigger(ETrigger.TARGET_END.value, time_stamp[1])
                    continue

                self.__queue_trigger(get_option_trigger(data.used_tagger), time_stamp[0])
                self.__queue_trigger(ETrigger.OPTION_END.value, time_stamp[1])

            self.__queue_trigger(ETrigger.END_STIMULUS.value, data.audio.secs)

    @contextmanager
    def start(self) -> "ATriggerSender":
        """Method responsible for the `with` syntax functionality."""
        try:
            self.__thread.start()
            yield self
        finally:
            self.__del__()

    def __del__(self) -> None:
        if self.__thread is None or not self.__thread.is_alive():
            return

        for t in self.__trigger_enqueue_threads:
            t.join()

        self.__trigger_queue.join()
        self.__exit_flag = True
        self.__thread.join()
        assert not self.__thread.is_alive()

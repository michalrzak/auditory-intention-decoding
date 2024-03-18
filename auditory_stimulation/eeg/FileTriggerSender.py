import threading
from datetime import datetime
from os import PathLike
from queue import Queue
from typing import IO

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.eeg.trigger_sender import ATriggerSender


class FileTriggerSender(ATriggerSender):
    """Constructs a FileTriggerSender object, which writes all acquired triggers to a file.

    The structure of this object is relatively complicated, as to make it non-blocking, the file operations are executed
    on separate threads. This requires locking/unlocking the written file.

    The class works by enqueuing timestamps + triggers and opening write_file workers, where each pops an item from the
    queue and writes it to the file. This should ensure that the triggers are always in correct order in the file.
    """
    __target_file: PathLike
    __file: IO
    __file_lock: threading.Lock

    __file_write_thread: threading.Thread
    __trigger_queue: Queue

    def __init__(self, target_file: PathLike):
        """Constructs a FileTriggerSender object.

        :param target_file: The target file, where the triggers will be written.
        """
        self.__target_file = target_file
        self.__file = open(self.__target_file, "w")
        self.__file_lock = threading.Lock()

        self.__trigger_queue = Queue()

    def __write_file_worker(self) -> None:
        time, trigger = self.__trigger_queue.get(block=False)

        with self.__file_lock:
            self.__file.write(f"{datetime.timestamp(time) * 1000}: {str(trigger)}\n")

        self.__trigger_queue.task_done()

    def __del__(self):
        self.__trigger_queue.join()
        self.__file.close()

    def _send_trigger(self, trigger: ETrigger) -> None:
        self.__trigger_queue.put((datetime.today(), trigger))
        threading.Thread(target=self.__write_file_worker).start()

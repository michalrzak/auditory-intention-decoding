import logging
from datetime import datetime
from os import PathLike
from typing import Any

from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class Logger(AObserver):
    """ Observer class, used to log the Observed object.

    INSTANTIATING MULTIPLE INSTANCES OF THIS CLASS WILL BREAK THE PREVIOUS LOGGING!
    FIXME: THIS SHOULD NOT HAPPEN
    """

    def __init__(self, logging_directory: PathLike):
        logging.basicConfig(filename=f"{str(logging_directory)}/{datetime.today().strftime('%Y-%m-%d-%H-%M-%S')}.log",
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if identifier == EModelUpdateIdentifier.NEW_PRIMER:
            logging.info(f"Added new primer {data}")

        elif identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            logging.info(f"Added new stimulus {data}")


        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            logging.info(f"Changing experiment state to {data}")

        else:
            assert False, f"Unexpected identifier: {identifier}"

from typing import Any

from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.view.view import AView


class CLIView(AView):

    # TODO: change type
    def __update_new_prompt(self, data: Any) -> None:
        print(f"Prompt: {data}")

    # TODO: change type
    def __update_experiment_state_changed(self, data: Any) -> None:
        print(f"New State: {data}")

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if identifier == EModelUpdateIdentifier.NEW_PROMPT:
            # TODO: assert type is correct
            self.__update_new_prompt(data)
        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            # TODO: assert type is correct
            self.__update_experiment_state_changed(data)
        else:
            # this should never happen
            assert False

    def get_confirmation(self) -> bool:
        input("Please press the enter key")
        return True

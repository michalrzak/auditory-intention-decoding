from typing import Callable, Protocol, Dict, Optional

import psychopy
import psychopy.visual
from psychopy.hardware import keyboard

from auditory_stimulation.auditory_tagging.auditory_tagger import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.stimulus import CreatedStimulus
from auditory_stimulation.view.view import AView

LETTER_SIZE = 0.05
TEXT_BOX_POSITION = (0, 0)
TEXT_BOX_SIZE = (0.5, 0.5),
TEXT_BOX_COLOR = 1.
TEXT_BOX_COLOR_SPACE = 'rgb'
TEXT_BOX_FONT = 'Caladea'


class Drawable(Protocol):
    def draw(self) -> None:
        ...


class PsychopyView(AView):
    """A view, implementing the psychopy frontend.
    """

    def __init__(self,
                 sound_player: Callable[[Audio], None],
                 experiment_texts: Dict[EExperimentState, Optional[str]],
                 window: psychopy.visual.Window) -> None:
        """Constructs a PsychopyView object

        :param sound_player: The sound player to be used by the view.
        :param experiment_texts: Dictionary, containing the displayed experiment texts.
        :param window: The psychopy window to be used to display the elements.
        """
        super().__init__(sound_player, experiment_texts)
        self.__window = window
        self.__keyboard = keyboard.Keyboard()

    def __try_to_quit(self):
        if len(self.__keyboard.getKeys(["escape"])) != 0:
            self.close_view()

    def _update_new_stimulus(self, stimulus: CreatedStimulus) -> None:
        self.__try_to_quit()

        prompt = self.__create_text_box(stimulus.prompt)

        prompt.draw()
        self.__window.flip()

        self._sound_player(stimulus.modified_audio)

    def _update_new_primer(self, primer: str) -> None:
        self.__try_to_quit()

        prompt = self.__create_text_box(primer)

        prompt.draw()
        self.__window.flip()

    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        self.__try_to_quit()

        text = self.__create_text_box(self._experiment_texts[data])

        text.draw()
        self.__window.flip()

    def get_confirmation(self) -> bool:
        self.__try_to_quit()

        self.__keyboard.clearEvents()  # clear keys in case the key was already pressed before
        while len(self.__keyboard.getKeys(["space"])) == 0:
            ...

        return True

    def wait(self, secs: int) -> None:
        self.__try_to_quit()

        psychopy.core.wait(secs)

    def __create_text_box(self, text: str) -> Drawable:
        return psychopy.visual.TextBox2(win=self.__window,
                                        text=text,
                                        letterHeight=LETTER_SIZE,
                                        pos=TEXT_BOX_POSITION,
                                        size=TEXT_BOX_SIZE,
                                        color=1.,
                                        colorSpace=TEXT_BOX_COLOR_SPACE,
                                        font=TEXT_BOX_FONT)

    def close_view(self):
        """Closes the view properly."""
        self.__window.close()
        # psychopy.core.quit()

    def __del__(self):
        self.close_view()

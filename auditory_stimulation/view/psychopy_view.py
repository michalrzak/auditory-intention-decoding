from typing import Callable
from typing import Protocol

import psychopy
import psychopy.visual
from psychopy.hardware import keyboard

from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.stimulus import Stimulus
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

    def __init__(self, sound_player: Callable[[Audio], None], window: psychopy.visual.Window) -> None:
        super().__init__(sound_player)
        self.window = window

    def _update_new_stimulus(self, stimulus: Stimulus) -> None:
        prompt = self.__create_text_box(stimulus.prompt)

        prompt.draw()
        self.window.flip()

        self._sound_player(stimulus.audio)
        self.wait(10)  # TODO: this should not be here

    def _update_new_primer(self, primer: str) -> None:
        prompt = self.__create_text_box(primer)

        prompt.draw()
        self.window.flip()

    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        text = self.__create_text_box(str(data))

        text.draw()
        self.window.flip()

    def get_confirmation(self) -> bool:
        kb = keyboard.Keyboard()

        while len(kb.getKeys(["space"])) == 0:
            ...

        return True

    def wait(self, secs: int) -> None:
        psychopy.core.wait(secs)

    def __create_text_box(self, text: str) -> Drawable:
        return psychopy.visual.TextBox2(win=self.window,
                                        text=text,
                                        letterHeight=LETTER_SIZE,
                                        pos=TEXT_BOX_POSITION,
                                        size=TEXT_BOX_SIZE,
                                        color=1.,
                                        colorSpace=TEXT_BOX_COLOR_SPACE,
                                        font=TEXT_BOX_FONT)

    def close_view(self):
        self.window.close()
        # psychopy.core.quit()

    def __del__(self):
        self.close_view()

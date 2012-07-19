"""Input handling."""
from __future__ import absolute_import, division

import cocos
import pyglet

import flora.util.direction

# XXX not really sure about this design, or how it'll work with
# stuff like dialogue
class InputLayer(cocos.layer.Layer):
    """I accept input and direct it around.  I'm only concerned with
    controlling the *game world*; I don't much care about menus or much else.

    You might consider me the C in MVC.  Maybe.
    """
    is_event_handler = True

    _key_direction_map = {
        pyglet.window.key.UP: flora.util.direction.UP,
        pyglet.window.key.DOWN: flora.util.direction.DOWN,
        pyglet.window.key.LEFT: flora.util.direction.LEFT,
        pyglet.window.key.RIGHT: flora.util.direction.RIGHT,
    }

    def __init__(self, state):
        super(InputLayer, self).__init__()

        self._state = state

    def on_enter(self):
        super(InputLayer, self).on_enter()

        self._direction_stack = []

    # TODO this should care less about the actions of the keys, i suspect, and
    # just translate to a common internal meaning
    # TODO in which case, who owns the direction stack and other
    # semantics?
    def on_key_press(self, key, mod):
        if key in self._key_direction_map:
            direction = self._key_direction_map[key]
            self._state.start_walking(direction)
            self._direction_stack.append(direction)

    def on_key_release(self, key, mod):
        if key in self._key_direction_map:
            direction = self._key_direction_map[key]
            if direction in self._direction_stack:
                self._direction_stack.remove(direction)
                if self._direction_stack:
                    self._state.start_walking(self._direction_stack[-1])
                else:
                    self._state.stop_walking()

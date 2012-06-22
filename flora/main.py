# encoding: utf8
from __future__ import division

import sys

import cocos
import pyglet

from flora.model.spritesheet import Spritesheet, UP, DOWN, LEFT, RIGHT
from flora.model import Flora
from flora.view.world import WorldLayer
import flora.view.plane

class WorldController(cocos.layer.Layer):
    """I accept input and direct it around.  I'm only concerned with
    controlling the *game world*; I don't much care about menus or much else.

    You might consider me the C in MVC.  Maybe.
    """
    is_event_handler = True

    _key_direction_map = {
        pyglet.window.key.UP: flora.view.plane.UP,
        pyglet.window.key.DOWN: flora.view.plane.DOWN,
        pyglet.window.key.LEFT: flora.view.plane.LEFT,
        pyglet.window.key.RIGHT: flora.view.plane.RIGHT,
    }

    def __init__(self, model):
        super(WorldController, self).__init__()

        self._direction_stack = []

        self.model = model

        self.add(WorldLayer(model))

    def on_key_press(self, key, mod):
        if key in self._key_direction_map:
            direction = self._key_direction_map[key]
            self.model.player_walk(direction)
            self._direction_stack.append(direction)

    def on_key_release(self, key, mod):
        if key in self._key_direction_map:
            direction = self._key_direction_map[key]
            if direction in self._direction_stack:
                self._direction_stack.remove(direction)
                if self._direction_stack:
                    self.model.player_walk(self._direction_stack[-1])
                else:
                    self.model.player_stop()

def main():
    # Set up Pyglet resource stuff
    pyglet.resource.path.append('data')
    pyglet.resource.reindex()

    # Initialize the window
    # NOTE: 16:10 is good for monitors, but 16:9 is good for TVs.  hm.
    dx = cocos.director.director
    dx.init(width=1280, height=800, caption=u'❀  flora  ✿', vsync=False)

    model = Flora()
    model.load_map('field')
    # TODO put player object ????
    scene = cocos.scene.Scene(WorldController(model))

    dx.run(scene)

if __name__ == '__main__':
    main()

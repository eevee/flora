# encoding: utf8
from __future__ import division

import cocos
import pyglet

from flora.engine.input import InputLayer
from flora.engine.map import MapLayer
from flora.load.map import Loader

class GameState(pyglet.event.EventDispatcher):
    """I keep track of high-level, game-global state: the player's progress,
    roughly what's going on at the moment, etc.  I also act as an event hub for
    player input.

    Don't tell anyone, but I'm like the M in MVC.
    """

    _map = None

    def __init__(self):
        self.loader = Loader(['maps/field.yaml'], ['entities/entities.yaml'])

    def change_map(self, map_name):
        mapdata = self.loader.load_map(map_name)
        # TODO blah blah another circular ref.
        self._map = MapLayer(self, mapdata)
        return self._map


    def start_walking(self, direction):
        self.dispatch_event('on_start_walking', direction)

    def stop_walking(self):
        self.dispatch_event('on_stop_walking')

GameState.register_event_type('on_start_walking')
GameState.register_event_type('on_stop_walking')


class Flora(object):
    """Hello!  I'm the entire game.  What's up.

    I'm the main entry point: I do very basic setup and teardown.
    """

    def __init__(self):
        # Set up Pyglet resource stuff
        pyglet.resource.path.append('data')
        pyglet.resource.reindex()

    def run(self):
        # Initialize the window
        # NOTE: 16:10 is good for monitors, but 16:9 is good for TVs.  hm.
        dx = cocos.director.director
        dx.init(width=1280, height=800, caption=u'❀  flora  ✿', vsync=False)

        # Create the game proper and fire it off
        # TODO this will need some stuff to handle a main menu scene later
        state = GameState()

        controller = InputLayer(state)
        game = state.change_map('field')

        scene = cocos.scene.Scene(controller, game)
        dx.run(scene)


if __name__ == '__main__':
    Flora().run()

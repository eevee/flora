# encoding: utf8
from __future__ import absolute_import
from __future__ import division

import cocos
import pyglet

from flora.engine.map import WorldLayer
from flora.model.load import Loader

class GameState(pyglet.event.EventDispatcher):
    """I keep track of high-level, game-global state: the player's progress,
    roughly what's going on at the moment, etc.  I also act as an event hub for
    player input.

    Don't tell anyone, but I'm like the M in MVC.
    """

    _world = None

    def __init__(self):
        self.loader = Loader(['maps/field.yaml'], ['entities/entities.yaml'])

        self.inventory = []

    def change_map(self, map_name):
        mapdata = self.loader.load_map(map_name)
        # TODO blah blah another circular ref.
        self._world = WorldLayer(self, mapdata)
        return self._world


class Flora(object):
    """Hello!  I'm the entire game.  What's up.

    I'm the main entry point: I do very basic setup and teardown.
    """

    def __init__(self):
        # Set up Pyglet resource stuff
        pyglet.resource.path.append('data')
        pyglet.resource.reindex()

        # Load some global stuff
        # TODO gonna need a real pre-loading step, and also loading per map
        pyglet.resource.add_font('fonts/short-stack.ttf')

    def run(self):
        # Initialize the window
        # NOTE: 16:10 is good for monitors, but 16:9 is good for TVs.  hm.
        dx = cocos.director.director
        dx.init(width=1280, height=800, caption=u'❀  flora  ✿', vsync=False)

        # Create the game proper and fire it off
        # TODO this will need some stuff to handle a main menu scene later
        state = GameState()

        game = state.change_map('field')

        scene = cocos.scene.Scene(game)
        dx.run(scene)

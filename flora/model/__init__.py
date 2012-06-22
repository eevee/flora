from __future__ import absolute_import, division

import pyglet

from flora.model.map import MapLayout

class Flora(pyglet.event.EventDispatcher):
    """I'm the entire game.

    I know the player's status, the current map, etc.  I don't do a lot by
    myself; other objects should prod me and see what happens.
    """

    current_map = None

    def __init__(self):
        pass

    def load_map(self, map_name):
        self.current_map = MapLayout.load(map_name)

    def player_walk(self, direction):
        self.dispatch_event('on_start_walking', direction)

    def player_stop(self):
        self.dispatch_event('on_stop_walking')

Flora.register_event_type('on_start_walking')
Flora.register_event_type('on_stop_walking')

from __future__ import absolute_import

import os.path

import cocos
import pyglet.image
import pyglet.resource
import yaml

import flora
from flora.view.plane import Direction, UP, DOWN, LEFT, RIGHT


class MapLayout(object):
    """I know what things are on a map.

    Flora maps use a hybrid grid system: the terrain itself is a fixed grid of
    cells, but decorations and other objects can exist at any arbitrary
    coordinates.
    """
    # XXX am i just the pristine copy, or what?  what happens with changes,
    # dudes walking around, etc?

    @classmethod
    def load(cls, map_name):
        self = cls()

        map_defs = yaml.load(pyglet.resource.file('maps/field.yaml'))
        map_data = map_defs[map_name]

        self.name = map_name
        # TODO wish i were a namedtuple
        self.size = tuple(map_data['size'])

        # "Layers":
        # 1. Background texture.  Default terrain that shows through as an
        # ultimate fallback.
        self.base_terrain = map_data['base_terrain']

        # 1b. "Horizon" texture.  Forms a border around the map proper and
        # extends off into infinity.
        self.horizon_terrain = map_data['horizon_terrain']

        # Entity definitions.
        self.entities = []
        for entity_data in map_data['entities']:
            self.entities.append(MapEntity(entity_data))

        #from flora.engine.debug import DebugLayer
        #self.add(DebugLayer(self.model), z=9999)

        return self

    def visible_cells(self, x0, y0, x1, y1):
        """Iterates over all terrain cells in the given region."""
        # TODO is there an actual "rectangular region" class somewhere?  rather
        # use that
        # TODO gonna need a more interesting interface when there are more
        # entities/decorations
        # XXX cell size really needs to be set somewhere
        for x in xrange(x0, x1, 64):
            for y in xrange(y0, y1, 64):
                if x < 0 or y < 0 or x > self.size[0] or y > self.size[1]:
                    tex = self.horizon_terrain
                else:
                    tex = self.base_terrain

                # TODO: yield MapCell(tex)
                yield x, y, tex

class MapEntity(object):
    """I represent the original core functionality of an entity on the map --
    i.e. I should never change!
    """

    def __init__(self, entity_data):
        self.spritesheet_name = entity_data['sprite']
        self.initial_position = tuple(entity_data['position'])

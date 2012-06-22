from __future__ import absolute_import

import os.path

import cocos
from cocos.euclid import Point2
from cocos.rect import Rect
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
        self.size = Point2(*map_data['size'])
        self.rect = Rect(0, 0, *self.size)

        # "Layers":
        # 1. Background texture.  Default terrain that shows through as an
        # ultimate fallback.
        self.base_terrain = MapTerrain(map_data['base_terrain'])

        # 1b. "Horizon" texture.  Forms a border around the map proper and
        # extends off into infinity.
        self.horizon_terrain = MapTerrain(map_data['horizon_terrain'])

        # Entity definitions.
        self.entities = []
        for entity_data in map_data['entities']:
            self.entities.append(MapEntity(entity_data))

        #from flora.engine.debug import DebugLayer
        #self.add(DebugLayer(self.model), z=9999)

        return self

    def visible_cells(self, rect):
        """Iterates over all terrain cells in the given region."""
        # TODO is there an actual "rectangular region" class somewhere?  rather
        # use that
        # TODO gonna need a more interesting interface when there are more
        # entities/decorations
        # XXX cell size really needs to be set somewhere
        GRID_SIZE = 64
        for x in xrange(rect.left - rect.left % GRID_SIZE, rect.right, GRID_SIZE):
            for y in xrange(rect.bottom - rect.bottom % GRID_SIZE, rect.top, GRID_SIZE):
                yield MapCell(self, Point2(x, y))


class MapCell(object):
    """I'm just generated as a transient object for representing a cell,
    really.
    """

    def __init__(self, map, point):
        self.map = map
        self.point = point

    @property
    def terrain(self):
        # Note that because these points are the bottom-left of the cell, and
        # sprites extend upwards and rightwards, a point on the LEFT edge is
        # INSIDE the map but a point on the RIGHT edge is OUTSIDE the map.
        rect = self.map.rect
        if not (rect.left <= self.point.x < rect.right and
                rect.bottom <= self.point.y < rect.top):
            return self.map.horizon_terrain

        return self.map.base_terrain

    @property
    def terrain_texture(self):
        terrain = self.terrain
        texture = terrain.texture

        # Surprise!  These are (row, column) which is (y, x).
        return texture[
            self.point.y / 64 % texture.rows,
            self.point.x / 64 % texture.columns,
        ]


### Three (?) main kinds of things that can exist on a map:

class MapTerrain(object):
    """I am some kinda base flooring."""

    def __init__(self, name):
        self.name = name

    @property
    def texture(self):
        img = pyglet.resource.image(os.path.join('sprites/terrain', self.name, 'texture.png'))
        image_grid = pyglet.image.ImageGrid(img, rows=img.height / 64, columns=img.width / 64)
        tex_grid = image_grid.get_texture_sequence()

        return tex_grid


class MapEntity(object):
    """I represent the original core functionality of an entity on the map --
    i.e. I should never change!
    """

    def __init__(self, entity_data):
        self.spritesheet_name = entity_data['sprite']
        self.initial_position = tuple(entity_data['position'])

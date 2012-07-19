from __future__ import absolute_import

import os.path

from cocos.euclid import Point2
from cocos.rect import Rect
import pyglet.image
import pyglet.resource
import yaml

from flora.engine.entity import Entity
from flora.model.spritesheet import Spritesheet
from flora.util.data import reify

class MapData(object):
    """Lazy object that represents data for a map.

    Consider the properties here as a rough guide to the map file format.
    """

    # XXX actually this is a property of the whole world.  should it live here...?
    GRID_SIZE = 64

    def __init__(self, loader, name, data):
        self.name = name
        self._loader = loader
        self._data = data

    @reify
    def size(self):
        return Point2(*self._data['size'])

    @reify
    def rect(self):
        return Rect(0, 0, *self._data['size'])

    def _load_texture_grid(self, name):
        img = pyglet.resource.image(os.path.join('sprites/terrain', name, 'texture.png'))
        image_grid = pyglet.image.ImageGrid(
            img,
            rows=img.height / self.GRID_SIZE,
            columns=img.width / self.GRID_SIZE,
        )
        return image_grid.get_texture_sequence()

    @reify
    def base_terrain(self):
        return self._load_texture_grid(self._data['base_terrain'])

    @reify
    def horizon_terrain(self):
        return self._load_texture_grid(self._data['horizon_terrain'])

    # Entity definitions.
    # TODO need a real way to specify the player start point
    @property
    def entities(self):
        for entity_data in self._data['entities']:
            scale2 = entity_data.get('scale', 1)
            spritesheet = Spritesheet.load(entity_data['sprite'])
            yield Entity(
                initial_position=Point2(*entity_data['position']),
                spritesheet=spritesheet,
                scale=spritesheet.scale * scale2,
                radius=spritesheet.radius * scale2,
            )


class MapLoader(object):
    """Loads a map.  Returns a `MapLayer`.

    Flora maps use a hybrid grid system: the terrain (i.e., background) itself
    is a fixed grid of cells, but decorations and other objects can exist at
    any arbitrary coordinates.
    """
    # XXX am i just the pristine copy, or what?  what happens with changes,
    # dudes walking around, etc?

    def __init__(self, map_sources, sprite_sources):
        self.map_sources = [yaml.load(pyglet.resource.file(fn)) for fn in map_sources]

    def load(self, map_name):
        # TODO caching?  ??  ???????
        return MapData(self, map_name, self.map_sources[0][map_name])

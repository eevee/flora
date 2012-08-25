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

# TODO reify is great, but has the minor downside in here that it duplicates
# everything: both the data and the cached properties exist.  of course, the
# data stays loaded forever anyway, so maybe this is just part of that same
# problem
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
            yield Entity(
                entity_type=self._loader.load_entity_type(entity_data['type']),
                initial_position=Point2(*entity_data['position']),
                scale=entity_data.get('scale', 1),
            )


class EntityTypeData(object):
    def __init__(self, loader, name, data):
        self.name = name
        self._loader = loader
        self._data = data

    @reify
    def base_path(self):
        return self._data['base_path']

    @reify
    def scale(self):
        return self._data['scale']

    @reify
    def shape(self):
        return self._data['shape']

    @reify
    def spritesheet(self):
        return Spritesheet.load(self.name, self._data)




class Loader(object):
    # XXX am i just the pristine copy, or what?  what happens with changes,
    # dudes walking around, etc?

    def __init__(self, map_sources, entity_sources):
        self.map_sources = [yaml.load(pyglet.resource.file(fn)) for fn in map_sources]
        self.entity_sources = [yaml.load(pyglet.resource.file(fn)) for fn in entity_sources]

    def load_map(self, map_name):
        """Loads a map.  Returns a `MapData`.

        Flora maps use a hybrid grid system: the terrain (i.e., background)
        itself is a fixed grid of cells, but decorations and other objects can
        exist at any arbitrary coordinates.
        """
        # TODO caching?  ??  ???????
        return MapData(self, map_name, self.map_sources[0][map_name])

    def load_entity_type(self, type_name):
        """Loads an entity type.  Returns an `EntityTypeData`."""
        return EntityTypeData(self, type_name, self.entity_sources[0][type_name])

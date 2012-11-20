from __future__ import absolute_import

import os.path

from cocos.euclid import Point2
from cocos.rect import Rect
import pyglet.image
import pyglet.resource

from flora.engine.entity import Entity
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
        img = pyglet.resource.image("sprites/terrain/{0}/texture.png".format(name))
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
                behaviors=entity_data.get('behaviors', {}),
            )

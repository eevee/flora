from __future__ import absolute_import

import pyglet.image
import pyglet.resource
import yaml

from flora.model.entity import EntityTypeData
from flora.model.map import MapData


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

from __future__ import absolute_import, division

import cocos
from cocos.euclid import Point2
from cocos.rect import Rect
import pyglet.image
import pyglet.sprite

from flora.engine.debugger import DebugLayer

# TODO people are kinda violatin demeter in me
# TODO maybe this should actually copy the stuff out of mapdata, not save it
class MapLayer(cocos.layer.scrolling.ScrollingManager):
    """I'm the map, I'm the map, I'm the map.

    I know what things are on a map, construct various layers to make sure it
    renders correctly, update when necessary, and hang on to game data.

    If you like MVC, I'm the V, but I also act as an interface to the M.
    """

    def __init__(self, state, mapdata):
        super(MapLayer, self).__init__()

        self._state = state
        self._mapdata = mapdata

        # Terrain: the background
        self.add(TerrainLayer(), z=0, name='terrain')

        # Entities: the interesting stuff
        entity_layer = EntityLayer()
        self.add(entity_layer, z=1, name='entities')

        self._player_entity = None
        for entity in mapdata.entities:
            # TODO hey, gross.  looks like i want an EntityData too?  figure
            # this out once entity types are first-class
            # TODO this is a circular ref of course
            entity._world = self

            if self._player_entity is None:
                self._player_entity = entity
            entity_layer.add(entity)

        # Debugging
        self.add(DebugLayer(state), z=999)

    def on_enter(self):
        super(MapLayer, self).on_enter()

        # TODO this feels a little hamfisted, but not sure how it should really
        # be handled until the "player object" is more well-defined.  perhaps
        # the player object should register itself directly?
        self._state.push_handlers(self._player_entity)

        self.schedule(lambda dt: self.set_focus(*self._player_entity.position))

    def visible_cells(self, rect):
        """Iterates over all terrain cells in the given region."""
        x0 = int(rect.left - rect.left % self._mapdata.GRID_SIZE)
        x1 = int(rect.right)
        y0 = int(rect.bottom - rect.bottom % self._mapdata.GRID_SIZE)
        y1 = int(rect.top)

        rect = self._mapdata.rect

        for x in xrange(x0, x1, self._mapdata.GRID_SIZE):
            for y in xrange(y0, y1, self._mapdata.GRID_SIZE):
                point = Point2(x, y)

                # Note that because these points are the bottom-left of the cell, and
                # sprites extend upwards and rightwards, a point on the LEFT edge is
                # INSIDE the map but a point on the RIGHT edge is OUTSIDE the map.
                if (rect.left <= point.x < rect.right and
                        rect.bottom <= point.y < rect.top):
                    terrain = self._mapdata.base_terrain
                else:
                    terrain = self._mapdata.horizon_terrain

                texture = terrain.texture

                # Surprise!  These are (row, column) which is (y, x).
                yield point, texture[
                    int(point.y / self._mapdata.GRID_SIZE) % texture.rows,
                    int(point.x / self._mapdata.GRID_SIZE) % texture.columns,
                ]


class TerrainLayer(cocos.layer.ScrollableLayer):
    """I draw the main map grid, which is primarily just terrain."""

    def __init__(self):
        super(TerrainLayer, self).__init__()

        self._sprite_cache = {}

    def set_view(self, *a, **kw):
        super(TerrainLayer, self).set_view(*a, **kw)

        self._update_sprites()

    def _update_sprites(self):
        """Make sure all the visible tiles are showing.

        With some inspiration from cocos.tiles.
        """
        seen = set()

        # Create sprites for the terrain
        for point, texture in self.parent.visible_cells(Rect(self.view_x, self.view_y, self.view_w, self.view_h)):
            # NOTE: Point2 objects hash by IDENTITY, NOT VALUE.  Upshot: DO NOT
            # USE THEM AS DICT KEYS OR SET VALUES
            key = tuple(point)
            seen.add(key)
            if key in self._sprite_cache:
                continue

            self._sprite_cache[key] = pyglet.sprite.Sprite(
                texture,
                x=point.x, y=point.y,
                batch=self.batch)

        # Drop any sprites no longer visible on-screen
        unseen = set(self._sprite_cache) - seen
        for key in unseen:
            self._sprite_cache[key].delete()
            self._sprite_cache.pop(key)


class EntityLayer(cocos.layer.ScrollableLayer):
    """I'm kind of a dumb container for entities so far."""

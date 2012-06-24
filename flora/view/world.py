from __future__ import absolute_import, division

import os.path

import cocos
from cocos.rect import Rect
import pyglet.image
import pyglet.sprite
import yaml

import flora
from flora.view.debug import DebugLayer
from flora.view.entity import Entity
from flora.view.plane import Direction, UP, DOWN, LEFT, RIGHT
from flora.model.spritesheet import Spritesheet


class WorldLayer(cocos.layer.scrolling.ScrollingManager):
    """I know what things are on a map, construct various layers to make sure
    it renders correctly, and update when necessary.

    I guess I'm the V in MVC.
    """

    def __init__(self, model):
        super(WorldLayer, self).__init__()

        self.model = model

        # Main child: the layer containing all the stuff in the world
        self.add(WorldMapLayer(model.current_map), name='map')

        # Debugging layer is separate so as to be toggleable
        self.add(DebugLayer(self.model), z=9999)

        self.set_focus(0, 0)


class WorldMapLayer(cocos.layer.ScrollableLayer):
    """I display the actual stuff in the world."""

    def __init__(self, current_map):
        super(WorldMapLayer, self).__init__()

        self.current_map = current_map

        self._sprite_cache = {}

    def on_enter(self):
        super(WorldMapLayer, self).on_enter()

        # Create sprites for actors
        # XXX this is here because we need the player, but honestly it might be
        # a good idea to always have all the entities around

        player_entity = None
        for map_entity in self.current_map.entities:
            spritesheet = Spritesheet.load(map_entity.spritesheet_name)
            entity = Entity(spritesheet, position=map_entity.initial_position, scale=0.25)
            self.add(entity, z=1)

            map_entity._FIXME_view_entity = entity

            if player_entity is None:
                player_entity = entity

        # TODO it doesn't seem like this should be down here.  definitely not in set_view, probably not in sprite-updater code at all.
        # i am still not a fan of the input handling really.  seems like the world view should worry about movement keypresses?
        self.parent.model.push_handlers(player_entity)
        self.player_entity = player_entity

        self.schedule(lambda dt: self.parent.set_focus(*self.player_entity.position))

    def set_view(self, *a, **kw):
        super(WorldMapLayer, self).set_view(*a, **kw)

        self._update_sprites()

    def _update_sprites(self):
        """Make sure all the visible tiles are showing.

        With some inspiration from cocos.tiles.
        """
        cmap = self.current_map
        seen = set()

        # Create sprites for the terrain
        for cell in cmap.visible_cells(Rect(self.view_x, self.view_y, self.view_w, self.view_h)):
            # NOTE: Point2 objects hash by IDENTITY, NOT VALUE.  Upshot: DO NOT
            # USE THEM AS DICT KEYS OR SET VALUES
            key = tuple(cell.point)
            seen.add(key)
            if key in self._sprite_cache:
                continue

            self._sprite_cache[key] = pyglet.sprite.Sprite(
                cell.terrain_texture,
                x=cell.point.x, y=cell.point.y,
                batch=self.batch)

        # Drop any sprites no longer visible on-screen
        unseen = set(self._sprite_cache) - seen
        for key in unseen:
            self._sprite_cache[key].delete()
            self._sprite_cache.pop(key)

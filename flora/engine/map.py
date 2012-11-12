from __future__ import absolute_import, division

import cocos
from cocos.euclid import Point2
from cocos.rect import Rect
import pyglet.image
import pyglet.sprite

from flora.engine.debugger import DebugLayer
from flora.engine.dialogue import DialogueLayer
from flora.engine.menu import MenuLayer
import flora.util.direction

SEARCH_DISTANCE = 64

class WorldLayer(cocos.layer.Layer):
    """I'm the root layer class for the game world.  I contain the map, dialog,
    pause screen, etc., and do some light mediation between all of those
    screens.
    """

    is_event_handler = True

    Z_MAP = 0
    Z_DIALOGUE = 90
    Z_MENU = 100

    def __init__(self, state, mapdata):
        super(WorldLayer, self).__init__()

        self._state = state

        self.add(MapLayer(state, mapdata), z=self.Z_MAP)

    def on_key_press(self, key, mod):
        if key == pyglet.window.key.TAB:
            self.add(MenuLayer(self._state), name='menu', z=self.Z_MENU)

        else:
            return False

        return True


    def initiate_dialogue(self, dialogue_tree):
        self.add(DialogueLayer(dialogue_tree), name='dialogue', z=self.Z_DIALOGUE)

    def pick_up_item(self, entity):
        # TODO probably needs an animation or something, much much later
        entity.kill()

        self._state.inventory.append(entity.entity_type)

        # TODO i guess a pickup sound goes here
        # TODO wow you are retarded what is any of this garbage
        self.children[0][1].children_names['fyi'].inform('got a thing!!', entity.position)


# TODO people are kinda violatin demeter in me
# TODO maybe this should actually copy the stuff out of mapdata, not save it
class MapLayer(cocos.layer.scrolling.ScrollingManager):
    """I'm the map, I'm the map, I'm the map.

    I know what things are on a map, construct various layers to make sure it
    renders correctly, update when necessary, and hang on to game data.

    If you like MVC, I'm the V, but I also act as an interface to the M.
    """

    is_event_handler = True

    Z_TERRAIN = 10
    Z_ENTITIES = 20
    Z_FYI = 80
    Z_DEBUG = 9999

    def __init__(self, state, mapdata):
        super(MapLayer, self).__init__()

        self._state = state
        self._mapdata = mapdata

        # Terrain: the background
        self.add(TerrainLayer(), z=self.Z_TERRAIN, name='terrain')

        # Entities: the interesting stuff
        entity_layer = EntityLayer()
        self.add(entity_layer, z=self.Z_ENTITIES, name='entities')

        # This layer is for transient UI text, like pick-up notices.
        self.add(FYILayer(), name='fyi', z=self.Z_FYI)

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
        self.add(DebugLayer(), z=self.Z_DEBUG, name='debug')

    def on_enter(self):
        super(MapLayer, self).on_enter()

        self.focus_player()

        # TODO remove this somehow
        self._direction_stack = []

    def on_exit(self):
        self.unschedule(self.focus_player)

        super(MapLayer, self).on_exit()

    def focus_player(self, dt=0.0):
        self.set_focus(*self._player_entity.position)


    ### Input handling for the map

    _key_direction_map = {
        pyglet.window.key.UP: flora.util.direction.UP,
        pyglet.window.key.DOWN: flora.util.direction.DOWN,
        pyglet.window.key.LEFT: flora.util.direction.LEFT,
        pyglet.window.key.RIGHT: flora.util.direction.RIGHT,
    }

    def on_key_press(self, key, mod):
        if key in self._key_direction_map:
            direction = self._key_direction_map[key]
            self.unschedule(self.focus_player)
            self.schedule(self.focus_player)
            self._player_entity.start_walking(direction)
            self._direction_stack.append(direction)

        elif key == pyglet.window.key.SPACE:
            # TODO what the fuck is this?  needs some kind of event handling
            # jackass
            target = self.find_facing(self._player_entity, with_behavior='on_interact')
            if target:
                interaction = target.behaviors['on_interact']
                if interaction['action'] == 'converse':
                    self.parent.initiate_dialogue(interaction['conversation'])
                elif interaction['action'] == 'pickup':
                    self.parent.pick_up_item(target)
                else:
                    raise TypeError("unknown interaction type {0}".format(interaction['action']))

        elif key == pyglet.window.key.F4:
            self.toggle_debugging()

        else:
            return False

        # Keypress handled
        return True

    def on_key_release(self, key, mod):
        if key in self._key_direction_map:
            direction = self._key_direction_map[key]
            if direction in self._direction_stack:
                self._direction_stack.remove(direction)
                if self._direction_stack:
                    self._player_entity.start_walking(self._direction_stack[-1])
                else:
                    self._player_entity.stop_walking()
                    self.unschedule(self.focus_player)


    def toggle_debugging(self):
        debug_layer = self.children_names['debug']
        debug_layer.visible = not debug_layer.visible

    ### Map inspection utilities

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

    def find_facing(self, entity, with_behavior=None):
        # Find nearby things that respond to use
        # TODO really need to figure out where this kind of code goes.  surely
        # in the entity layer.
        # TODO also, goddamn, Rect blows.
        # XXX the idea here is that the "activation" rectangle is a fixed size
        # in front of the searching entity, extended inwards to touch the
        # entity's center.  this could probably be improved or better-commented
        # or something.
        # TODO this makes poor use of the concept of "shape".  luckily that
        # isn't implemented yet.
        # TODO seems the search area should be round, and yet, it is not.  eh?
        target = Rect(
            0, 0,
            SEARCH_DISTANCE + abs(entity._angle.vector[0]) * entity.entity_type.shape,
            SEARCH_DISTANCE + abs(entity._angle.vector[1]) * entity.entity_type.shape,
        )
        if entity._angle is flora.util.direction.UP:
            target.midbottom = entity.position
        elif entity._angle is flora.util.direction.DOWN:
            target.midtop = entity.position
        elif entity._angle is flora.util.direction.LEFT:
            target.midright = entity.position
        elif entity._angle is flora.util.direction.RIGHT:
            target.midleft = entity.position

        for z, other in self.children_names['entities'].children:
            if other is entity:
                continue

            if with_behavior is not None and with_behavior not in other.behaviors:
                continue

            # TODO again, Rect sucks
            if target.contains(*other.position):
                # OK, within range
                # TODO need to, like, pick more cleverly than just the first
                return other


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

        # TODO this is causing a fuckton of work even when the view on screen
        # doesn't actually change.  optimize the hell out of me please

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

    def reorder_child(self, child, z):
        """Changes the z-index of a given child."""
        # XXX this would be nice to have in core tbh
        # XXX actually i don't know how to do this efficiently...

        self.children = [item for item in self.children if item[1] is not child]
        import bisect
        bisect.insort(self.children, (z, child))

    # XXX might work better to skip the cocosnode stuff entirely, use pyglet
    # sprites directly, and override draw() here.


class FYILayer(cocos.layer.ScrollableLayer):
    """I exist solely to show little informational messages."""

    def inform(self, message, position):
        label = cocos.text.Label(message, position=position, font_name='Short Stack', font_size=10, anchor_x='center', anchor_y='bottom')
        label.opacity = 0.
        self.add(label)

        label.do(
            (cocos.actions.FadeIn(0.3) | cocos.actions.MoveBy((0, 8), 0.3))
            + cocos.actions.Delay(1)
            + (cocos.actions.FadeOut(0.3) | cocos.actions.MoveBy((0, 8), 0.3))
            + cocos.actions.CallFuncS(lambda self: self.kill())
        )

from __future__ import absolute_import, division

import cocos
from cocos.euclid import Point2
import pyglet.gl as gl
import pyglet.graphics


class OutlinedPolygonsGroup(pyglet.graphics.Group):
    """Draw polygons as outlines, not filled."""

    def set_state(self):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

    def unset_state(self):
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)


class DebugLayer(cocos.layer.scrolling.ScrollableLayer):
    """I show the map grid and the positions and sizes of entities."""

    def __init__(self, state):
        super(DebugLayer, self).__init__()

        self._state = state
        self.grid_batch = pyglet.graphics.Batch()
        self.outlines_group = OutlinedPolygonsGroup()

    def on_enter(self):
        super(DebugLayer, self).on_enter()

        TEXT_OFFSET = 4
        GRID_SIZE = 64

        w, h = self._state._map._mapdata.size

        for x in range(0, w + 1, GRID_SIZE):
            self.grid_batch.add(2, gl.GL_LINES, None,
                ('v2i', (x, 0, x, h)),
                ('c4f', (1.0, 1.0, 1.0, 0.5) * 2))

            label = cocos.text.Label(str(x), position=(x + TEXT_OFFSET, 0 + TEXT_OFFSET), font_size=8)
            self.add(label)

        for y in range(0, h + 1, GRID_SIZE):
            self.grid_batch.add(2, gl.GL_LINES, None,
                ('v2i', (0, y, w, y)),
                ('c4f', (1.0, 1.0, 1.0, 0.5) * 2))

            label = cocos.text.Label(str(y), position=(0 + TEXT_OFFSET, y + TEXT_OFFSET), font_size=8)
            self.add(label)

    def draw(self):
        # Update list of entities
        # TODO this should actually update instead of recomputing all day, but, whatever
        entity_batch = pyglet.graphics.Batch()
        for _, entity in self._state._map.children_names['entities'].children:
            x, y = entity.position
            w, h = entity.size
            x0 = entity.position[0] - entity.image_anchor[0] * entity.scale
            y0 = entity.position[1] - entity.image_anchor[1] * entity.scale
            x1, y1 = x0 + w, y0 + h
            entity_batch.add(4, gl.GL_QUADS, self.outlines_group,
                ('v2f', (x0, y0, x0, y1, x1, y1, x1, y0)),
                ('c4f', (1.0, 1.0, 0.0, 0.5) * 4))

            # This is a diamond but at scale it looks enough like a dot
            D = 3
            entity_batch.add(4, gl.GL_QUADS, None,
                ('v2f', (x + D, y, x, y - D, x - D, y, x, y + D)),
                ('c4f', (1.0, 1.0, 0.0, 1.0) * 4))

            # Collision footprint...  kinda
            R = entity.radius
            entity_batch.add(4, gl.GL_QUADS, None,
                ('v2f', (x - R, y - R, x + R, y - R, x + R, y + R, x - R, y + R)),
                ('c4f', (1.0, 1.0, 0.0, 0.2) * 4))


        # TODO wtf is GL_CURRENT_BIT
        gl.glPushMatrix()
        self.transform()
        self.grid_batch.draw()
        entity_batch.draw()
        gl.glPopMatrix()

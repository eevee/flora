from __future__ import absolute_import, division

import cocos
import pyglet.gl as gl
import pyglet.graphics


class DebugLayer(cocos.layer.scrolling.ScrollableLayer):
    def __init__(self, model):
        super(DebugLayer, self).__init__()

        self._model = model
        self.grid_batch = pyglet.graphics.Batch()

        TEXT_OFFSET = 4
        GRID_SIZE = 64

        w, h = self._model.current_map.size

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
        for entity in self._model.current_map.entities:
            x, y = entity.position
            w, h = entity.size
            x0, y0 = entity.position - entity.anchor
            x1, y1 = x0 + w, y0 + h
            entity_batch.add(4, gl.GL_LINE_LOOP, None,
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

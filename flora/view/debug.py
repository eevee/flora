from __future__ import absolute_import, division

import cocos
import pyglet.gl as gl
import pyglet.graphics


class DebugLayer(cocos.layer.scrolling.ScrollableLayer):
    def __init__(self, model):
        super(DebugLayer, self).__init__()

        self._model = model
        self._batch = pyglet.graphics.Batch()

        TEXT_OFFSET = 4
        GRID_SIZE = 64

        w, h = self._model.current_map.size

        for x in range(0, w + 1, GRID_SIZE):
            self._batch.add(2, gl.GL_LINES, None,
                ('v2i', (x, 0, x, h)),
                ('c4f', (1.0, 1.0, 1.0, 0.5) * 2))

            label = cocos.text.Label(str(x), position=(x + TEXT_OFFSET, 0 + TEXT_OFFSET), font_size=8)
            self.add(label)

        for y in range(0, h + 1, GRID_SIZE):
            self._batch.add(2, gl.GL_LINES, None,
                ('v2i', (0, y, w, y)),
                ('c4f', (1.0, 1.0, 1.0, 0.5) * 2))

            label = cocos.text.Label(str(y), position=(0 + TEXT_OFFSET, y + TEXT_OFFSET), font_size=8)
            self.add(label)

    def draw(self):
        super(DebugLayer, self).draw()

        # TODO wtf is GL_CURRENT_BIT
        gl.glPushMatrix()
        self.transform()
        self._batch.draw()
        gl.glPopMatrix()

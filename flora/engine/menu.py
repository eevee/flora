"""In-game "pause" menu."""

from __future__ import absolute_import

import cocos
import pyglet

class MenuLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(MenuLayer, self).__init__()

        self.add(cocos.layer.ColorLayer(255, 255, 255, 192))

        self.add(cocos.text.Label(u'PAUSE', font_name='Short Stack', font_size=48, color=(0, 0, 0, 255), anchor_x='center', anchor_y='top', position=(640, 784)), z=1)

    def on_key_press(self, key, mod):
        if key in (pyglet.window.key.ESCAPE, pyglet.window.key.TAB):
            # TODO self.kill() doesn't work with named layers  :|
            #self.kill()
            self.parent.remove('menu')

        # Always consider the keypress handled
        return True

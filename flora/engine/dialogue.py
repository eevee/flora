from __future__ import absolute_import

import cocos
import pyglet

class DialogueLayer(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self, dialogue_tree):
        super(DialogueLayer, self).__init__()

        self.add( cocos.layer.ColorLayer(0, 0, 0, 64), z=0.1 )

        # Create the frame
        border = cocos.layer.ColorLayer(32, 32, 32, 255, width=1280 - 16*2, height=320 - 16*2)
        border.position = 16, 16
        self.add(border, z=1)

        shadow = cocos.layer.ColorLayer(160, 160, 160, 255, width=1280 - 32*2, height=320 - 32*2)
        shadow.position = 32, 32
        self.add(shadow, z=1.9)

        bg = cocos.layer.ColorLayer(208, 208, 208, 255, width=1280 - 32*2 - 4, height=320 - 32*2 - 4)
        bg.position = 36, 32
        self.add(bg, z=2)

        self.add(cocos.text.Label(dialogue_tree, font_name='Short Stack', font_size=24, color=(0, 0, 0, 255), height=320 - 64*2, width=1280 - 64*2, anchor_y='top', position=(64, 320 - 64)), z=3)

        # Top of the dialog box is at 304
        self.add(cocos.sprite.Sprite(pyglet.resource.image('sprites/characters/maya/portrait-normal.png'), position=(64, 64), anchor=(0, 0)), z=0.5)

    def on_key_press(self, key, mod):
        # TODO self.kill() doesn't work with named layers  :|
        #self.kill()
        self.parent.remove('dialogue')
        return True

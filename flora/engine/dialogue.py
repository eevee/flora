from __future__ import absolute_import

import cocos

class DialogueLayer(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self, dialogue_tree):
        super(DialogueLayer, self).__init__()

        # Create the frame
        border = cocos.layer.ColorLayer(64, 64, 64, 255, width=1152, height=272)
        border.position = 64, 64
        self.add(border, z=1)

        bg = cocos.layer.ColorLayer(0, 0, 96, 255, width=1120, height=240)
        bg.position = 80, 80
        self.add(bg, z=2)

        self.add(cocos.text.Label(dialogue_tree, font_name='Short Stack', font_size=40, height=80, width=960, anchor_y='top', position=(96, 304)), z=3)

    def on_key_press(self, key, mod):
        # TODO self.kill() doesn't work with named layers  :|
        #self.kill()
        self.parent.remove('dialogue')
        return True

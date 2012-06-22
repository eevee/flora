from __future__ import absolute_import

import cocos


class Entity(cocos.sprite.Sprite):
    def __init__(self, spritesheet, **kw):
        spritesheet.pose = 'standing'
        super(Entity, self).__init__(spritesheet._pick_image(), anchor=spritesheet._pick_anchor(), **kw)

        self.spritesheet = spritesheet

    # TODO uhoh this stuff needs to be componentized
    _walking_action = None

    def on_start_walking(self, direction):
        self.spritesheet.angle = direction
        self.spritesheet.pose = 'walking'
        self.image = self.spritesheet._pick_image()
        self.image_anchor = self.spritesheet._pick_anchor()

        if self._walking_action:
            self.remove_action(self._walking_action)

        # TODO where does this live
        step_size = 192
        action = cocos.actions.MoveBy(direction.vector * step_size, 1)
        action = cocos.actions.Repeat(action)
        self._walking_action = self.do(action)


    def on_stop_walking(self):
        self.spritesheet.pose = 'standing'
        self.image = self.spritesheet._pick_image()

        if self._walking_action:
            self.remove_action(self._walking_action)
            self._walking_action = None
            # set sprite state

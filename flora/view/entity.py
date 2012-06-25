from __future__ import absolute_import, division

import cocos
from cocos.euclid import Point2
from cocos.rect import Rect

from flora.view.plane import DOWN


def rect_contain_rect(r1, r2):
    return (
        r1.left < r2.left and r2.right < r1.right and
        r1.bottom < r2.bottom and r2.top < r1.top
    )

def rect_overlap(r1, r2):
    return r1.intersects(r2) and not (rect_contain_rect(r1, r2) or rect_contain_rect(r2, r1))
    return ((
        r1.left < r2.left < r1.right < r2.right or
        r2.left < r1.left < r2.right < r1.right
    ) and (
        r1.bottom < r2.bottom < r1.top < r2.top or
        r2.bottom < r1.bottom < r2.top < r1.top
    ))

class Walk(cocos.actions.Action):
    def init(self, velocity):
        self.velocity = velocity

    def step(self, dt):
        #self.target.position = self.start_position + self.delta * dt
        new_position = self.target.position + self.velocity * dt

        r = self.target.radius
        collision_box = Rect(
            new_position.x - r,
            new_position.y - r,
            r * 2,
            r * 2,
        )

        # XXX YEAH NOPE
        if rect_overlap(collision_box, Rect(0, 0, 320, 320)):
            # Collision!  Can't move there.
            return

        self.target.position = new_position


class Entity(cocos.sprite.Sprite):
    def __init__(self, entity_model, **kw):

        # TODO what if the model's spritesheet changes
        self.spritesheet = entity_model.sprite

        # TODO this is bad.  need a better way to update view from model.
        self.radius = entity_model.radius

        # TODO: self._pose = self.spritesheet.default_pose
        self._pose = 'standing'
        self._angle = DOWN

        super(Entity, self).__init__(
            self.spritesheet.pick_image(self._pose, self._angle),
            anchor=self.spritesheet.pick_anchor(self._pose, self._angle),
            position=entity_model.initial_position,
            scale=entity_model.scale,
            **kw)

        entity_model.register_view(self)

    def update_spritesheet(self, pose=None, angle=None):
        if pose is not None:
            self._pose = pose
        if angle is not None:
            self._angle = angle

        self.image = self.spritesheet.pick_image(self._pose, self._angle)
        self.image_anchor = self.spritesheet.pick_anchor(self._pose, self._angle)

    # TODO uhoh this stuff needs to be componentized
    _walking_action = None

    def on_start_walking(self, direction):
        self.update_spritesheet(pose='walking', angle=direction)

        if self._walking_action:
            self.remove_action(self._walking_action)

        # TODO where does this live
        step_size = 192
        action = Walk(direction.vector * step_size)
        action = cocos.actions.Repeat(action)
        self._walking_action = self.do(action)


    def on_stop_walking(self):
        self.update_spritesheet(pose='standing')

        if self._walking_action:
            self.remove_action(self._walking_action)
            self._walking_action = None

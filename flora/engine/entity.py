from __future__ import absolute_import, division

import cocos
from cocos.euclid import Point2
from cocos.rect import Rect

from flora.util.direction import DOWN


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

        r = self.target.entity_type.shape  # XXX this should ask the entity for a collision shape
        collision_box = Rect(
            new_position.x - r,
            new_position.y - r,
            r * 2,
            r * 2,
        )

        if self.target.would_collide(collision_box):
            # Collision!  Can't move there.
            return

        self.target.position = new_position


# TODO: componentize me; make the sprite a child node and everything JW
class Entity(cocos.sprite.Sprite):
    """I represent an active, concrete object in the world.

    I straddle model and view: my position is canonical both as
    display coordinates and physics coordinates.
    """

    def __init__(self, entity_type, initial_position, scale):
        self.entity_type = entity_type

        # TODO: self._pose = self.spritesheet.default_pose
        self._pose = 'default'
        self._angle = DOWN

        # TODO kind of not liking the state of the spritesheet class.
        # dismantle it into EntityType?  make it a template that spawns state
        # objects for Walk to use?  what about terrain sounds?
        self.spritesheet = self.entity_type.spritesheet

        super(Entity, self).__init__(
            self.spritesheet.pick_image(self._pose, self._angle),
            anchor=self.spritesheet.pick_anchor(self._pose, self._angle),
            position=initial_position,
            scale=scale * entity_type.scale,
        )

    # TODO i wish this was standard, and that position+anchor were also Point2s
    @property
    def size(self):
        return Point2(self.width, self.height)

    @property
    def collision_rect(self):
        r = self.entity_type.shape  # XXX well...
        return Rect(
            self.position[0] - r,
            self.position[1] - r,
            r * 2,
            r * 2,
        )


    # TODO overriding properties is awkward.
    def _set_position(self, value):
        super(Entity, self)._set_position(value)
        if self.parent:
            x, y = value
            self.parent.reorder_child(self, -y)
    position = property(cocos.sprite.Sprite._get_position, _set_position)

    def on_enter(self):
        super(Entity, self).on_enter()

        self.parent.reorder_child(self, - self.position[1])



    def would_collide(self, collision_box):
        # TODO clearly this interface is suboptimal  :)
        # TODO who should own this stuff?  the world object?  or me, in a
        # component?

        # Check the map boundaries
        if rect_overlap(collision_box, self._world._mapdata.rect):
            return True

        # Check against other entities
        # XXX THIS SUCKS IN SO MANY WAYS
        for z, entity in self.parent.children:
            if entity is self:
                continue

            if rect_overlap(collision_box, entity.collision_rect):
                return True

        return False

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
        self.update_spritesheet(pose='default')

        if self._walking_action:
            self.remove_action(self._walking_action)
            self._walking_action = None

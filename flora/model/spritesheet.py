from __future__ import absolute_import

import os.path

import pyglet.image
import pyglet.resource
import yaml

from flora.util.direction import Direction, LEFT, RIGHT


class Spritesheet(object):
    """I contain sprites for an arbitrary number of poses at multiple angles
    for a single graphical entity.  For example, an actor may have both running
    and walking animations.  "Running" and "walking" are two different poses,
    and both are depicted differently depending on the angle the actor is
    facing.
    """

    _loaded = {}

    # Defaults
    scale = 1

    @classmethod
    def load(cls, name):
        if name in cls._loaded:
            return cls._loaded[name]

        # TODO put this in __init__
        # TODO require a default pose
        # TODO default angle to DOWN
        # TODO simpler way to support a single sprite, like a flower
        character_defs = yaml.load(pyglet.resource.file('spritesheets/characters.yaml'))
        sprite_def = character_defs[name]

        self = cls()
        sprite_path = os.path.join('sprites', sprite_def['filepath'])
        for pose_name, pose_data in sprite_def['poses'].iteritems():
            for angle_name, angle_data in pose_data.iteritems():
                pose = self._views.setdefault(pose_name, {})
                if angle_name in pose:
                    raise ValueError

                frame_textures = []
                for frame_path in angle_data['frames']:
                    frame_textures.append(pyglet.resource.texture(
                        os.path.join(sprite_path, frame_path)))

                animation = pyglet.image.Animation.from_image_sequence(
                    sequence=frame_textures,
                    period=0.1,
                )

                if 'anchor' in angle_data:
                    anchor = angle_data['anchor']
                else:
                    anchor = animation.get_max_width() / 2, animation.get_max_height() / 2

                angle = Direction._instances[angle_name]
                pose[angle] = animation, anchor

            if 'LEFT' in pose_data and 'RIGHT' not in pose_data:
                self.flip_pose(pose_name, LEFT, RIGHT)
            elif 'RIGHT' in pose_data and 'LEFT' not in pose_data:
                self.flip_pose(pose_name, RIGHT, LEFT)

        if 'scale' in sprite_def:
            self.scale = sprite_def['scale']

        # TODO is this part of an entity?  seems like it...  should be?  should
        # entity types be another middle layer?  (yes)
        self.radius = sprite_def['radius']

        cls._loaded[name] = self
        return self


    def __init__(self, *args, **kwargs):
        self._views = {}

    def flip_pose(self, view_name, angle_from, angle_to):
        # copies with a horizontal flip
        view = self._views[view_name]
        if angle_to in view:
            raise ValueError

        animation, anchor = view[angle_from]
        new_animation = animation.get_transform(flip_x=True)
        new_anchor = new_animation.get_max_width() - anchor[0], anchor[1]
        view[angle_to] = new_animation, new_anchor


    def pick_image(self, pose, angle):
        return self._views[pose][angle][0]

    def pick_anchor(self, pose, angle):
        return self._views[pose][angle][1]

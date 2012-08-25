from __future__ import absolute_import

import os.path

import pyglet.image
import pyglet.resource
import yaml

from flora.util.direction import Direction, DOWN, LEFT, RIGHT, UP


class Spritesheet(object):
    """I contain sprites for an arbitrary number of poses at multiple angles
    for a single graphical entity.  For example, an actor may have both running
    and walking animations.  "Running" and "walking" are two different poses,
    and both are depicted differently depending on the angle the actor is
    facing.
    """

    _loaded = {}

    @classmethod
    def load(cls, name, sprite_def):
        if name in cls._loaded:
            return cls._loaded[name]

        # TODO put this in __init__
        # TODO require a default pose
        # TODO default angle to DOWN
        # TODO simpler way to support a single sprite, like a flower

        self = cls()
        sprite_path = os.path.join('sprites', sprite_def['base_path'])

        # Poses: either one (pose) or many (poses)
        if 'pose' in sprite_def:
            poses = dict(default=sprite_def['pose'])
        else:
            poses = sprite_def['poses']


        for pose_name, pose_data in poses.iteritems():
            for angle_name, angle_data in pose_data.iteritems():
                pose = self._views.setdefault(pose_name, {})
                if angle_name in pose:
                    raise ValueError

                # Frames: either one (frame) or many (frames)
                if 'frame' in angle_data:
                    frames = [angle_data['frame']]
                else:
                    frames = angle_data['frames']

                frame_textures = []
                for frame_path in frames:
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

                if angle_name == 'ALL':
                    pose[LEFT] = pose[RIGHT] = pose[UP] = pose[DOWN] = animation, anchor
                else:
                    angle = Direction._instances[angle_name]
                    pose[angle] = animation, anchor

            if 'LEFT' in pose_data and 'RIGHT' not in pose_data:
                self.flip_pose(pose_name, LEFT, RIGHT)
            elif 'RIGHT' in pose_data and 'LEFT' not in pose_data:
                self.flip_pose(pose_name, RIGHT, LEFT)

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

from __future__ import absolute_import

import os.path

import pyglet.image
import pyglet.resource

from flora.util.data import reify
from flora.util.direction import Direction, DOWN, LEFT, RIGHT, UP


class EntityTypeData(object):
    def __init__(self, loader, name, data):
        #if name in cls._loaded:
        #    return cls._loaded[name]

        self.name = name
        self._loader = loader
        self._data = data

        sprite_path = 'sprites/' + data['base_path']
        if 'pose' in data:
            # 'pose' as a key is a shortcut for a single pose and a single
            # angle
            self._load_poses(sprite_path, dict(default=dict(ALL=data['pose'])))
        else:
            self._load_poses(sprite_path, data['poses'])

    @reify
    def scale(self):
        return self._data.get('scale', 1)

    @reify
    def shape(self):
        return self._data['shape']

    @reify
    def solid(self):
        return self._data.get('solid', True)

    def _load_poses(self, sprite_path, poses):

        self._views = dict()

        # TODO put this in __init__
        # TODO require a default pose
        # TODO default angle to DOWN

        for pose_name, pose_data in poses.iteritems():
            for angle_name, angle_data in pose_data.iteritems():
                pose = self._views.setdefault(pose_name, {})
                if angle_name in pose:
                    raise ValueError("Duplicate angle {0} for pose {1}"
                        .format(angle_name, pose_name))

                # Frames: either one (frame) or many (frames)
                if 'frame' in angle_data:
                    frames = [angle_data['frame']]
                else:
                    frames = angle_data['frames']

                frame_textures = []
                for frame_path in frames:
                    frame_textures.append(pyglet.resource.texture(
                        u'/'.join((sprite_path, frame_path))))

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
                self._mirror_pose(pose_name, LEFT, RIGHT)
            elif 'RIGHT' in pose_data and 'LEFT' not in pose_data:
                self._mirror_pose(pose_name, RIGHT, LEFT)

    def _mirror_pose(self, view_name, angle_from, angle_to):
        # copies with a horizontal flip
        view = self._views[view_name]
        if angle_to in view:
            raise ValueError

        animation, anchor = view[angle_from]
        new_animation = animation.get_transform(flip_x=True)
        new_anchor = new_animation.get_max_width() - anchor[0], anchor[1]
        view[angle_to] = new_animation, new_anchor


    def image_anchor_for(self, pose, angle):
        """Returns a tuple of (image, anchor) for the given pose and angle.
        """
        return self._views[pose][angle]

from __future__ import absolute_import

import os.path

import cocos
import pyglet.image
import yaml

import flora
from flora.engine.plane import Direction, UP, DOWN, LEFT, RIGHT


# TODO: build all this stuff on top of pyglet.resource


def file_path(fn):
    path, _ = os.path.split(flora.__file__)
    return os.path.join(path, 'data', fn)


class Spritesheet(object):
    """I contain sprites for an arbitrary number of poses at multiple angles
    for a single graphical entity.  For example, an actor may have both running
    and walking animations.  "Running" and "walking" are two different poses,
    and both are depicted differently depending on the angle the actor is
    facing.
    """

    @classmethod
    def load(cls, name):
        character_defs = yaml.load(open(file_path('spritesheets/characters.yaml')))
        sprite_def = character_defs[name]

        self = cls()
        for pose, posedata in sprite_def['poses'].iteritems():
            for anglename, angledata in posedata.iteritems():
                angle = Direction._instances[anglename]
                # TODO pull this out, i think?  or maybe this whole thing
                # should merge with add_pose
                frames = [os.path.join('sprites', sprite_def['filepath'], frame) for frame in angledata['frames']]

                self.add_pose(frames, pose, angle, anchor=angledata['anchor'])

            if 'LEFT' in posedata and 'RIGHT' not in posedata:
                self.flip_pose(pose, LEFT, RIGHT)
            elif 'RIGHT' in posedata and 'LEFT' not in posedata:
                self.flip_pose(pose, RIGHT, LEFT)

        return self


    def __init__(self, *args, **kwargs):
        self._views = {}
        # XXX don't hard-code this.  also, what's a good size
        self._txbin = pyglet.image.atlas.TextureBin(
            texture_width=1024, texture_height=1024)
        self._current_pose = None
        self._current_angle = DOWN

    def add_pose(self, filenames, view_name, angle, anchor=None):
        # TODO support angle=ALL, and make it default?
        # TODO support reflecting left/right
        view = self._views.setdefault(view_name, {})
        if angle in view:
            raise ValueError

        animation = pyglet.image.Animation.from_image_sequence(
            sequence=(pyglet.image.load(file_path(fn)) for fn in filenames),
            period=0.1,
        )
        animation.add_to_texture_bin(self._txbin)

        if not anchor:
            anchor = animation.get_max_width() / 2, animation.get_max_height() / 2

        view[angle] = animation, anchor

    def flip_pose(self, view_name, angle_from, angle_to):
        # copies with a horizontal flip
        view = self._views[view_name]
        if angle_to in view:
            raise ValueError

        animation, anchor = view[angle_from]
        new_animation = animation.get_transform(flip_x=True)
        new_anchor = new_animation.get_max_width() - anchor[0], anchor[1]
        view[angle_to] = new_animation, new_anchor


    @property
    def pose(self):
        return self._current_pose

    @pose.setter
    def pose(self, value):
        if value not in self._views:
            raise KeyError

        self._current_pose = value

    @property
    def angle(self):
        return self._current_angle

    @angle.setter
    def angle(self, value):
        if value not in (UP, DOWN, LEFT, RIGHT):
            raise KeyError

        self._current_angle = value


    def _pick_image(self):
        return self._views[self._current_pose][self._current_angle][0]

    def _pick_anchor(self):
        return self._views[self._current_pose][self._current_angle][1]

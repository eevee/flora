# encoding: utf8
from __future__ import division

import cocos
import pyglet

TIC = 1 / 24

from flora.spriteset import PosableSprite, UP, DOWN, LEFT, RIGHT
class Actor(cocos.sprite.Sprite):
    # TODO this is already aching to be componentized, oh no

    def __init__(self, spriteset, *args, **kwargs):
        self.spriteset = spriteset
        kwargs.setdefault('anchor', (0, 0))
        super(Actor, self).__init__(spriteset._pick_image(), *args, **kwargs)

        self.current_frame = 0
        self.frames = []#imagelist

        self.set_state()

    walk_action = None

    def walk(self, dx, dy):
        self.set_state(pose='walking')

        step_size = 64

        if self.walk_action:
            self.remove_action(self.walk_action)

        action = cocos.actions.MoveBy((dx * step_size, dy * step_size), 1)
        action = cocos.actions.Repeat(action)
        self.walk_action = self.do(action)

    def stop_walking(self):
        if self.walk_action:
            self.remove_action(self.walk_action)
            self.walk_action = None
            self.set_state(pose='standing')


    def set_state(self, pose=None, angle=None):
        if pose:
            self.spriteset.pose = pose
        if angle:
            self.spriteset.angle = angle

        self.image = self.spriteset._pick_image()
        self.image_anchor = self.spriteset._pick_anchor()


    def dont_draw(self):
        super(Actor, self).draw()

        from pyglet import gl

        # TODO this is all almost certainly not the nicest way to do any of
        # this.

        gl.glColor3f(1, 1, 0)

        # NOTE: a vertex list has a .draw() but it does its own thang that
        # includes setting the color
        v = list(self._vertex_list.vertices)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glLineStipple(1, 0x5555)
        gl.glEnable(gl.GL_LINE_STIPPLE)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(v[0], v[1])
        gl.glVertex2f(v[2], v[3])
        gl.glVertex2f(v[4], v[5])
        gl.glVertex2f(v[6], v[7])
        gl.glEnd()
        gl.glDisable(gl.GL_LINE_STIPPLE)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

        # Draw a dot at the anchor point
        gl.glPushMatrix()
        self.transform()
        n = 2 / self.scale
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(n, n)
        gl.glVertex2f(n, -n)
        gl.glVertex2f(-n, -n)
        gl.glVertex2f(-n, n)
        gl.glEnd()
        gl.glPopMatrix()

        gl.glColor3f(1, 1, 1) 


class Background(cocos.layer.Layer):
    def __init__(self):
        super(Background, self).__init__()

        self.add(cocos.layer.ColorLayer(0x6b, 0x87, 0x48, 0xff))


class Midground(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(Midground, self).__init__()

        cagroo_sprite = PosableSprite()
        cagroo_sprite.add_pose([
            'assets/characters/cagroo/side3.png',
        ],
            'standing',
            LEFT,
            anchor=(385, 530 - 456))
        cagroo_sprite.add_pose([
            'assets/characters/cagroo/front3.png',
        ],
            'standing',
            DOWN,
            anchor=(116, 581 - 528))
        cagroo_sprite.add_pose([
            'assets/characters/cagroo/back3.png',
        ],
            'standing',
            UP,
            anchor=(141, 743 - 546))
        cagroo_sprite.add_pose([
            'assets/characters/cagroo/side4.png',
            'assets/characters/cagroo/side5.png',
            'assets/characters/cagroo/side6.png',
            'assets/characters/cagroo/side1.png',
            'assets/characters/cagroo/side2.png',
            'assets/characters/cagroo/side3.png',
        ],
            'walking',
            LEFT,
            anchor=(385, 530 - 456))
        cagroo_sprite.add_pose([
            'assets/characters/cagroo/front4.png',
            'assets/characters/cagroo/front5.png',
            'assets/characters/cagroo/front6.png',
            'assets/characters/cagroo/front1.png',
            'assets/characters/cagroo/front2.png',
            'assets/characters/cagroo/front3.png',
        ],
            'walking',
            DOWN,
            anchor=(116, 581 - 528))
        cagroo_sprite.add_pose([
            'assets/characters/cagroo/back4.png',
            'assets/characters/cagroo/back5.png',
            'assets/characters/cagroo/back6.png',
            'assets/characters/cagroo/back1.png',
            'assets/characters/cagroo/back2.png',
            'assets/characters/cagroo/back3.png',
        ],
            'walking',
            UP,
            anchor=(141, 743 - 546))

        cagroo_sprite.flip_pose('standing', LEFT, RIGHT)
        cagroo_sprite.flip_pose('walking', LEFT, RIGHT)

        cagroo_sprite.pose = 'standing'
        cagroo_sprite.angle = UP
        self.cagroo = Actor(cagroo_sprite, position=(400, 300), scale=0.25)
        self.add(self.cagroo)

    current_direction = None

    def on_key_press(self, key, mod):
        if key in (pyglet.window.key.RIGHT, pyglet.window.key.LEFT, pyglet.window.key.UP, pyglet.window.key.DOWN):
            self.current_direction = key

        if key == pyglet.window.key.RIGHT:
            self.cagroo.spriteset.angle = RIGHT
            self.cagroo.walk(1, 0)
        elif key == pyglet.window.key.LEFT:
            self.cagroo.spriteset.angle = LEFT
            self.cagroo.walk(-1, 0)
        elif key == pyglet.window.key.DOWN:
            self.cagroo.spriteset.angle = DOWN
            self.cagroo.walk(0, -1)
        elif key == pyglet.window.key.UP:
            self.cagroo.spriteset.angle = UP
            self.cagroo.walk(0, 1)

    def on_key_release(self, key, mod):
        if key == self.current_direction:
            self.cagroo.stop_walking()


def main():
    dx = cocos.director.director

    dx.init(width=800, height=600, caption=u'❀  flora  ✿')

    scene = cocos.scene.Scene(Background(), Midground())

    dx.run(scene)

if __name__ == '__main__':
    main()

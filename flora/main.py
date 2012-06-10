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


GRID_SIZE = 64

class DebugLayer(cocos.layer.Layer):
    def __init__(self):
        super(DebugLayer, self).__init__()

        self.label_cache = {}

    def draw(self):
        import pyglet.graphics
        dx = cocos.director.director
        w, h = dx.get_window_size()

        # NOTE: This requires that the direct parent is the ScrollableLayer.
        # If layers are ever rearranged, this code will need to change to
        # something less janky
        x0 = self.parent.view_x
        y0 = self.parent.view_y

        TEXT_OFFSET = 4

        for x in range(x0 - x0 % GRID_SIZE, x0 + w, GRID_SIZE):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (x, y0, x, y0 + h)))

            if x not in self.label_cache:
                self.label_cache[x] = pyglet.text.Label(str(x), font_size=8)
            # TODO need to expire these?  might be more effort than it's worth tbh
            self.label_cache[x].x = x + TEXT_OFFSET
            self.label_cache[x].y = y0 + TEXT_OFFSET
            self.label_cache[x].draw()

        for y in range(y0 - y0 % GRID_SIZE, y0 + h, GRID_SIZE):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (x0, y, x0 + w, y)))

            if y not in self.label_cache:
                self.label_cache[y] = pyglet.text.Label(str(y), font_size=8)
            # TODO need to expire these?  might be more effort than it's worth tbh
            self.label_cache[y].x = x0 + TEXT_OFFSET
            self.label_cache[y].y = y + TEXT_OFFSET
            self.label_cache[y].draw()


class Midground(cocos.layer.Layer):

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


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(GameLayer, self).__init__()

        manager = cocos.layer.scrolling.ScrollingManager()
        scroller = cocos.layer.scrolling.ScrollableLayer()
        scroller.px_width = 1400
        scroller.px_height = 1000


        scroller.add(Background())


        mid = Midground()
        scroller.add(mid)
        scroller.add(DebugLayer())

        manager.add(scroller)
        self.add(manager)

        self.cagroo = mid.cagroo

        self.schedule(lambda *a: manager.set_focus(*self.cagroo.position))

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

    scene = cocos.scene.Scene(GameLayer())

    dx.run(scene)

if __name__ == '__main__':
    main()

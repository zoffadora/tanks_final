from hitbox import Hitbox
import world
import texture as skin

_missiles = []
_canvas = None


def initialize(canvas):
    global _canvas
    _canvas = canvas


class Missile:
    def __init__(self, canvas, x, y, vx, vy, owner):
        self._canvas = canvas
        self._x = x
        self._y = y
        self._vx = vx
        self._vy = vy
        self._owner = owner
        self._speed = 10
        self._alive = True
        self._damage = 34
        self._size = 32

        if vx == 1:
            img = 'missile_right'
        elif vx == -1:
            img = 'missile_left'
        elif vy == -1:
            img = 'missile_up'
        elif vy == 1:
            img = 'missile_down'
        else:
            img = 'missile_up'

        self._id = canvas.create_image(x, y, image=skin.get(img), anchor='nw')
        self._hitbox = Hitbox(x, y, self._size, self._size, padding=5)

    def update(self):
        if not self._alive:
            return

        self._x += self._vx * self._speed
        self._y += self._vy * self._speed
        self._hitbox.moveto(self._x, self._y)

        if self._x < -200 or self._x > world.get_width() + 200 or self._y < -200 or self._y > world.get_height() + 200:
            self._destroy()
            return

        import tanks_collection
        for tank in tanks_collection._tanks:
            if tank == self._owner:
                continue
            if not tank.is_alive():
                continue
            # Используем _Tank__hitbox для доступа к приватному атрибуту
            if self._hitbox.intersects(tank._Tank__hitbox):
                tank.take_damage(self._damage)
                self._destroy()
                return

        row = world.get_row(self._y)
        col = world.get_col(self._x)
        if world._inside_of_map(row, col):
            block = world.get_block(row, col)
            if block == world.BRICK:
                world.destroy(row, col)
                self._destroy()
                return
            elif block not in [world.GROUND, world.AIR]:
                self._destroy()
                return

        screen_x = world.get_screen_x(self._x)
        screen_y = world.get_screen_y(self._y)
        self._canvas.moveto(self._id, x=screen_x, y=screen_y)

    def _destroy(self):
        self._alive = False
        try:
            self._canvas.delete(self._id)
        except:
            pass
        if self in _missiles:
            _missiles.remove(self)

    def is_alive(self):
        return self._alive


def fire(owner):
    vx = owner.get_vx()
    vy = owner.get_vy()
    offset = 50
    x = owner.get_x() + vx * offset
    y = owner.get_y() + vy * offset
    missile = Missile(_canvas, x, y, vx, vy, owner)
    _missiles.append(missile)


def update():
    for missile in _missiles[:]:
        missile.update()
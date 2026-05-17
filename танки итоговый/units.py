import world
import texture as skin
from hitbox import Hitbox
from tkinter import NW
from random import randint
import time

import missiles_collection


class Unit:
    def __init__(self, canvas, x, y, speed, padding, bot, default_image):
        self._speed = speed
        self._x = x
        self._y = y
        self._vx = 0
        self._vy = 0
        self._canvas = canvas
        self._hp = 100
        self._dx = 0
        self._dy = 0
        self._bot = bot
        self._hitbox = Hitbox(x, y, world.BLOCK_SIZE, world.BLOCK_SIZE, padding=padding)

        self._default_image = default_image
        self._left_image = default_image
        self._right_image = default_image
        self._forward_image = default_image
        self._backward_image = default_image
        self._alive = True
        self._id = None

        self._create()

    def _create(self):
        self._id = self._canvas.create_image(self._x, self._y,
                                             image=skin.get(self._default_image),
                                             anchor=NW)

    def __del__(self):
        try:
            if self._id:
                self._canvas.delete(self._id)
        except Exception:
            pass

    def forward(self):
        self._vx = 0
        self._vy = -1
        if self._id:
            self._canvas.itemconfig(self._id, image=skin.get(self._forward_image))

    def backward(self):
        self._vx = 0
        self._vy = 1
        if self._id:
            self._canvas.itemconfig(self._id, image=skin.get(self._backward_image))

    def left(self):
        self._vx = -1
        self._vy = 0
        if self._id:
            self._canvas.itemconfig(self._id, image=skin.get(self._left_image))

    def right(self):
        self._vx = 1
        self._vy = 0
        if self._id:
            self._canvas.itemconfig(self._id, image=skin.get(self._right_image))

    def stop(self):
        self._vx = 0
        self._vy = 0

    def update(self):
        if not self._alive:
            return
        if self._bot:
            self._AI()
        self._dx = self._vx * self._speed
        self._dy = self._vy * self._speed
        self._x += self._dx
        self._y += self._dy

        self._update_hitbox()
        self._check_map_collision()
        self._repaint()

    def _AI(self):
        pass

    def _update_hitbox(self):
        self._hitbox.moveto(self._x, self._y)

    def _check_map_collision(self):
        details = {}
        self._hitbox.check_map_collision(details)
        if details:
            self._on_map_collision(details)
        else:
            self._no_map_collision()

    def _no_map_collision(self):
        pass

    def _on_map_collision(self, details):
        pass

    def _repaint(self):
        if not self._alive or not self._id:
            return
        screen_x = world.get_screen_x(self._x)
        screen_y = world.get_screen_y(self._y)
        self._canvas.moveto(self._id, x=screen_x, y=screen_y)

    def _undo_move(self):
        if self._dx == 0 and self._dy == 0:
            return
        self._x -= self._dx
        self._y -= self._dy
        self._update_hitbox()
        self._repaint()
        self._dx = 0
        self._dy = 0

    def intersects(self, other_unit):
        if not self._alive or not other_unit._alive:
            return False
        value = self._hitbox.intersects(other_unit._hitbox)
        if value:
            self._on_intersects(other_unit)
        return value

    def _on_intersects(self, other_unit):
        self._undo_move()

    def _change_orientation(self):
        rand = randint(0, 3)
        if rand == 0:
            self.left()
        elif rand == 1:
            self.forward()
        elif rand == 2:
            self.right()
        elif rand == 3:
            self.backward()

    def take_damage(self, damage):
        self._hp -= damage
        if self._hp <= 0:
            self._destroy()

    def _destroy(self):
        self._alive = False
        try:
            if self._id:
                self._canvas.delete(self._id)
                self._id = None
        except:
            pass

    def is_alive(self):
        return self._alive

    def get_hp(self):
        return self._hp

    def get_speed(self):
        return self._speed

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_vx(self):
        return self._vx

    def get_vy(self):
        return self._vy

    def get_size(self):
        return world.BLOCK_SIZE

    def is_bot(self):
        return self._bot


class Tank(Unit):
    def __init__(self, canvas, row, col, bot=True):
        super().__init__(canvas,
                         col * world.BLOCK_SIZE,
                         row * world.BLOCK_SIZE,
                         2,
                         8,
                         bot,
                         'tank_up')
        if bot:
            self._forward_image = 'tank_up'
            self._backward_image = 'tank_down'
            self._left_image = 'tank_left'
            self._right_image = 'tank_right'
        else:
            self._forward_image = 'tank_up_player'
            self._backward_image = 'tank_down_player'
            self._left_image = 'tank_left_player'
            self._right_image = 'tank_right_player'

        self.forward()
        self._ammo = 80
        self._usual_speed = self._speed
        self._water_speed = self._speed // 2
        self._super_speed = self._speed * 4
        self._super_speed_end_time = 0
        self._target = None
        self._hp = 100
        self._fuel = 1000
        self._shoot_cooldown = 0

    def _take_heart(self):
        self._hp += 20
        if self._hp > 100:
            self._hp = 100

    def _take_ammo(self):
        self._ammo += 10
        if self._ammo > 100:
            self._ammo = 100
        self._fuel += 100
        if self._fuel > 1000:
            self._fuel = 1000

    def _set_super_speed(self):
        self._speed = self._super_speed
        self._super_speed_end_time = time.time() + 5

    def update(self):
        if not self._alive:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        if self._super_speed_end_time > 0 and time.time() > self._super_speed_end_time:
            self._speed = self._usual_speed
            self._super_speed_end_time = 0

        if self._vx != 0 or self._vy != 0:
            self._fuel -= 0.3
            if self._fuel < 0:
                self._fuel = 0

        super().update()

    def set_target(self, target):
        self._target = target
        return self

    def _AI_goto_target(self):
        if self._target is None or not self._target.is_alive():
            return
        if randint(1, 2) == 1:
            if self._target.get_x() < self.get_x():
                self.left()
            else:
                self.right()
        else:
            if self._target.get_y() < self.get_y():
                self.forward()
            else:
                self.backward()

    def _AI(self):
        if not self._alive:
            return

        if self._target is not None and self._target.is_alive():
            dx = self._target.get_x() - self.get_x()
            dy = self._target.get_y() - self.get_y()

            can_shoot = False
            if self._vx == 1 and dx > 0 and abs(dy) < 60:
                can_shoot = True
            elif self._vx == -1 and dx < 0 and abs(dy) < 60:
                can_shoot = True
            elif self._vy == -1 and dy < 0 and abs(dx) < 60:
                can_shoot = True
            elif self._vy == 1 and dy > 0 and abs(dx) < 60:
                can_shoot = True

            if can_shoot and self._shoot_cooldown == 0 and randint(1, 25) == 1:
                self.fire()
                self._shoot_cooldown = 40

        if randint(1, 30) == 1:
            if randint(1, 10) < 9 and self._target is not None and self._target.is_alive():
                self._AI_goto_target()
            else:
                self._change_orientation()

    def fire(self):
        if self._ammo > 0 and self._alive:
            self._ammo -= 1
            missiles_collection.fire(self)

    def get_ammo(self):
        return self._ammo

    def get_fuel(self):
        return int(self._fuel)

    def _set_usual_speed(self):
        if self._super_speed_end_time == 0 or time.time() > self._super_speed_end_time:
            self._speed = self._usual_speed

    def _set_water_speed(self):
        if self._super_speed_end_time > 0 and time.time() < self._super_speed_end_time:
            self._speed = self._super_speed // 2
        else:
            self._speed = self._water_speed

    def _on_map_collision(self, details):
        bonus_collected = False

        if world.HEART in details:
            pos = details[world.HEART]
            if world.take(pos['row'], pos['col']) != world.AIR:
                self._take_heart()
                bonus_collected = True

        if world.MISSLE in details:
            pos = details[world.MISSLE]
            if world.take(pos['row'], pos['col']) != world.AIR:
                self._take_ammo()
                bonus_collected = True

        if world.TURBO in details:
            pos = details[world.TURBO]
            if world.take(pos['row'], pos['col']) != world.AIR:
                self._set_super_speed()
                bonus_collected = True

        if bonus_collected:
            if world.WATER in details and len(details) == 1:
                self._set_water_speed()
            return

        if world.WATER in details and len(details) == 1:
            self._set_water_speed()
            return

        if details:
            self._undo_move()
            if self._bot:
                self._change_orientation()

    def _no_map_collision(self):
        self._set_usual_speed()

    def _on_intersects(self, other_unit):
        super()._on_intersects(other_unit)
        if self._bot:
            self._change_orientation()


class Missile(Unit):
    def __init__(self, canvas, owner):
        # Определяем изображение в зависимости от направления
        if owner.get_vx() == 1:
            img = 'missile_right'
        elif owner.get_vx() == -1:
            img = 'missile_left'
        elif owner.get_vy() == -1:
            img = 'missile_up'
        elif owner.get_vy() == 1:
            img = 'missile_down'
        else:
            img = 'missile_up'

        # Создаём ракету
        self._speed = 8
        self._x = owner.get_x()
        self._y = owner.get_y()
        self._vx = owner.get_vx()
        self._vy = owner.get_vy()
        self._canvas = canvas
        self._hp = 100
        self._dx = 0
        self._dy = 0
        self._bot = False
        self._hitbox = Hitbox(self._x, self._y, 32, 32, padding=10)
        self._alive = True
        self._owner = owner
        self._damage = 34
        self._id = None

        # Создаём изображение
        self._id = canvas.create_image(self._x, self._y, image=texture.get(img), anchor=NW)

        # Смещаем ракету от танка
        offset = 50
        self._x += owner.get_vx() * offset
        self._y += owner.get_vy() * offset

        self._update_hitbox()
        self._repaint()

    def _update_hitbox(self):
        self._hitbox.moveto(self._x, self._y)

    def _repaint(self):
        if not self._alive or not self._id:
            return
        screen_x = world.get_screen_x(self._x)
        screen_y = world.get_screen_y(self._y)
        self._canvas.moveto(self._id, x=screen_x, y=screen_y)

    def update(self):
        if not self._alive:
            return

        self._dx = self._vx * self._speed
        self._dy = self._vy * self._speed
        self._x += self._dx
        self._y += self._dy

        self._update_hitbox()
        self._check_collision()
        self._repaint()

    def _check_collision(self):
        # Проверка границ карты
        if self._x < 0 or self._x > world.get_width() or self._y < 0 or self._y > world.get_height():
            self._destroy()
            return

        # Проверка столкновения с танками
        import tanks_collection
        for tank in tanks_collection._tanks[:]:
            if tank == self._owner:
                continue
            if not tank.is_alive():
                continue
            if self._hitbox.intersects(tank._hitbox):
                tank.take_damage(self._damage)
                self._destroy()
                return

        # Проверка столкновения с блоками
        row = world.get_row(self._y)
        col = world.get_col(self._x)
        if world._inside_of_map(row, col):
            block = world.get_block(row, col)
            if block == world.BRICK:
                world.destroy(row, col)
                self._destroy()
                return
            elif block != world.GROUND and block != world.AIR:
                self._destroy()
                return

    def _destroy(self):
        self._alive = False
        try:
            if self._id:
                self._canvas.delete(self._id)
                self._id = None
        except:
            pass
        import missiles_collection
        if self in missiles_collection._missiles:
            missiles_collection._missiles.remove(self)

    def is_alive(self):
        return self._alive

    def get_owner(self):
        return self._owner
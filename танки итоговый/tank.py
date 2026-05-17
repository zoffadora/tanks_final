from hitbox import Hitbox
from tkinter import *
from random import randint
import world
import texture as skin
import missiles_collection
import time


class Tank:
    __count = 0

    def __init__(self, canvas, x, y, model="Т-14 Армата", ammo=100, speed=5, bot=True):
        self.__bot = bot
        self.target = None
        self.__hitbox = Hitbox(x, y, self.get_size(), self.get_size(), padding=2)
        self.__canvas = canvas
        Tank.__count += 1
        self.__model = model
        self.__hp = 100
        self.__xp = 0
        self.__ammo = ammo
        self.__fuel = 10000
        self.__speed = speed
        self.__original_speed = speed
        self.__x = x
        self.__y = y
        self.__vx = 0
        self.__vy = 0
        self.__dx = 0
        self.__dy = 0
        self.__alive = True
        self.__turbo_end_time = 0

        if self.__x < 0:
            self.__x = 0
        if self.__y < 0:
            self.__y = 0

        self.__super_speed = self.__speed * 3
        self.__usual_speed = speed
        self.__water_speed = speed / 2
        self.__create()
        self.right()

    def is_alive(self):
        return self.__alive

    def take_damage(self, damage):
        self.__hp -= damage
        if self.__hp <= 0:
            self.__alive = False
            try:
                self.__canvas.delete(self.__id)
            except:
                pass
            print(f"Танк {self.__model} уничтожен!")
        return self.__hp

    def __take_heart(self):
        self.__hp += 20
        if self.__hp > 100:
            self.__hp = 100
        print(f"❤️ Сердце! HP = {self.__hp}")

    def __take_ammo(self):
        self.__ammo += 10
        if self.__ammo > 100:
            self.__ammo = 100
        self.__fuel += 100
        if self.__fuel > 10000:
            self.__fuel = 10000
        print(f"💣 Боеприпасы! Аммуниция = {self.__ammo}")

    def __set_usual_speed(self):
        if time.time() > self.__turbo_end_time:
            self.__speed = self.__usual_speed

    def __set_water_speed(self):
        if time.time() > self.__turbo_end_time:
            self.__speed = self.__water_speed
        else:
            self.__speed = self.__super_speed / 2

    def __set_super_speed(self):
        self.__speed = self.__super_speed
        self.__turbo_end_time = time.time() + 5
        print(f"⚡ ТУРБО! Скорость = {self.__speed} на 5 сек!")

    def __check_map_collision(self):
        details = {}
        self.__set_usual_speed()
        result = self.__hitbox.check_map_collision(details)
        if result:
            self.__on_map_collision(details)

    def __on_map_collision(self, details):
        # Сначала обрабатываем бонусы
        if world.HEART in details:
            pos = details[world.HEART]
            if world.take(pos['row'], pos['col']) != world.AIR:
                self.__take_heart()
            return

        if world.MISSLE in details:
            pos = details[world.MISSLE]
            if world.take(pos['row'], pos['col']) != world.AIR:
                self.__take_ammo()
            return

        if world.TURBO in details:
            pos = details[world.TURBO]
            if world.take(pos['row'], pos['col']) != world.AIR:
                self.__set_super_speed()
            return

        # Проверяем воду
        if world.WATER in details and len(details) == 1:
            self.__set_water_speed()
            return

        # Всё остальное - препятствия
        self.__undo_move()
        if self.__bot:
            self.__AI_change_orientation()

    def __check_out_of_world(self):
        if self.__hitbox.left < 0 or self.__hitbox.top < 0 or self.__hitbox.bottom >= world.get_height() or self.__hitbox.right >= world.get_width():
            self.__undo_move()
            if self.__bot:
                self.__AI_change_orientation()

    def set_target(self, target):
        self.__target = target
        return self

    def __AI_goto_target(self):
        if self.__target is None:
            return
        if randint(1, 2) == 1:
            if self.__target.get_x() < self.get_x():
                self.left()
            else:
                self.right()
        else:
            if self.__target.get_y() < self.get_y():
                self.forward()
            else:
                self.backward()

    def __AI(self):
        if not self.__alive:
            return

        # СТРЕЛЬБА ПО ИГРОКУ
        if self.__target is not None and self.__target.is_alive():
            dx = self.__target.get_x() - self.get_x()
            dy = self.__target.get_y() - self.get_y()

            can_shoot = False
            if self.__vx == 1 and dx > 0 and abs(dy) < 60:
                can_shoot = True
            elif self.__vx == -1 and dx < 0 and abs(dy) < 60:
                can_shoot = True
            elif self.__vy == -1 and dy < 0 and abs(dx) < 60:
                can_shoot = True
            elif self.__vy == 1 and dy > 0 and abs(dx) < 60:
                can_shoot = True

            # Стреляем с вероятностью 1/15
            if can_shoot and randint(1, 15) == 1:
                self.fire()

        # ДВИЖЕНИЕ
        if randint(1, 30) == 1:
            if randint(1, 10) < 9 and self.__target is not None and self.__target.is_alive():
                self.__AI_goto_target()
            else:
                self.__AI_change_orientation()

    def __AI_change_orientation(self):
        rand = randint(0, 3)
        if rand == 0:
            self.left()
        if rand == 1:
            self.right()
        if rand == 2:
            self.forward()
        if rand == 3:
            self.backward()

    def fire(self):
        if self.__ammo > 0 and self.__alive:
            self.__ammo -= 1
            missiles_collection.fire(self)
            if not self.__bot:
                print(f"🔫 Вы стреляли! Осталось: {self.__ammo}")
            else:
                print(f"💥 Враг {self.__model} стреляет в вас!")  # <-- должно появляться в консоли

    def forward(self):
        self.__vx = 0
        self.__vy = -1
        if self.__alive:
            if self.__bot:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_up'))
            else:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_up_player'))

    def backward(self):
        self.__vx = 0
        self.__vy = 1
        if self.__alive:
            if self.__bot:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_down'))
            else:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_down_player'))

    def left(self):
        self.__vx = -1
        self.__vy = 0
        if self.__alive:
            if self.__bot:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_left'))
            else:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_left_player'))

    def right(self):
        self.__vx = 1
        self.__vy = 0
        if self.__alive:
            if self.__bot:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_right'))
            else:
                self.__canvas.itemconfig(self.__id, image=skin.get('tank_right_player'))

    def update(self):
        if not self.__alive:
            return

        # Проверяем, закончилось ли турбо
        if time.time() > self.__turbo_end_time and self.__turbo_end_time > 0:
            self.__speed = self.__usual_speed
            self.__turbo_end_time = 0
            print(f"Скорость вернулась к {self.__speed}")

        if self.__fuel > self.__speed:
            if self.__bot:
                self.__AI()

            self.__dx = self.__vx * self.__speed
            self.__dy = self.__vy * self.__speed
            self.__x += self.__dx
            self.__y += self.__dy
            self.__fuel -= self.__speed
            self.__update_hitbox()
            self.__check_map_collision()
            self.__check_out_of_world()
            self.__repaint()

    def __undo_move(self):
        if self.__dx == 0 and self.__dy == 0:
            return

        self.__x -= self.__dx
        self.__y -= self.__dy
        self.__update_hitbox()
        self.__repaint()
        self.__dx = 0
        self.__dy = 0

    def __create(self):
        if self.__bot:
            img = skin.get('tank_up')
        else:
            img = skin.get('tank_up_player')
        self.__id = self.__canvas.create_image(self.__x, self.__y, image=img, anchor='nw')

    def __repaint(self):
        if not self.__alive:
            return
        self.__canvas.moveto(self.__id, x=world.get_screen_x(self.__x), y=world.get_screen_y(self.__y))

    def __update_hitbox(self):
        self.__hitbox.moveto(self.__x, self.__y)

    def intersects(self, other_tank):
        value = self.__hitbox.intersects(other_tank.__hitbox)
        if value:
            self.__undo_move()
            if self.__bot:
                self.__AI_change_orientation()
        return value

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_vx(self):
        return self.__vx

    def get_vy(self):
        return self.__vy

    def get_model(self):
        return self.__model

    def get_hp(self):
        return self.__hp

    def get_xp(self):
        return self.__xp

    def get_fuel(self):
        return self.__fuel

    def get_speed(self):
        return self.__speed

    def get_ammo(self):
        return self.__ammo

    @staticmethod
    def get_quantity():
        return Tank.__count

    def get_size(self):
        if self.__bot:
            return skin.get('tank_up').width()
        else:
            return skin.get('tank_up_player').width()

    def __del__(self):
        print('Танк удален')
        try:
            self.__canvas.delete(self.__id)
        except Exception:
            pass

    def __str__(self):
        return f"Модель:{self.__model}, здоровье: {self.__hp}, опыт: {self.__xp}, боеприпасы:{self.__ammo}, координаты: {self.__x},{self.__y}"
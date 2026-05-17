from tank import Tank
import world
from random import randint

_tanks = []
_canvas = None


def initialize(canv):
    global _canvas
    _canvas = canv

    # Игрок
    player = Tank(_canvas, world.SCREEN_WIDTH // 2, world.SCREEN_HEIGHT // 2, model="Игрок", speed=2, bot=False)
    _tanks.append(player)
    print("Игрок создан")

    # 7 врагов, разбросанных по всей карте
    for i in range(7):
        # Случайные координаты по всей карте
        x = randint(100, world.WIDTH - 100)
        y = randint(100, world.HEIGHT - 100)

        enemy = Tank(_canvas, x, y, model=f"Враг{i + 1}", speed=2, bot=True)
        enemy.set_target(player)
        _tanks.append(enemy)
        print(f"Враг {i + 1} создан на позиции ({x}, {y})")


def get_player():
    for tank in _tanks:
        if not tank._Tank__bot:
            return tank
    return None


def update():
    # Обновляем все танки
    for tank in _tanks:
        if tank.is_alive():
            tank.update()

    # Проверка столкновений между танками
    for i in range(len(_tanks)):
        for j in range(i + 1, len(_tanks)):
            if _tanks[i].is_alive() and _tanks[j].is_alive():
                _tanks[i].intersects(_tanks[j])


def check_collision(tank):
    for other_tank in _tanks:
        if tank == other_tank:
            continue
        if tank.is_alive() and other_tank.is_alive():
            if tank.intersects(other_tank):
                return True
    return False
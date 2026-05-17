import missiles_collection
from tkinter import *
import world
import tanks_collection
import texture

KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN = 37, 39, 38, 40
KEY_W = 87
KEY_S = 83
KEY_A = 65
KEY_D = 68
KEY_SPACE = 32
FPS = 60


def update():
    tanks_collection.update()
    missiles_collection.update()
    player = tanks_collection.get_player()

    if player and player.is_alive():
        world.set_camera_xy(player.get_x() - world.SCREEN_WIDTH // 2 + player.get_size() // 2,
                            player.get_y() - world.SCREEN_HEIGHT // 2 + player.get_size() // 2)
        world.update_map()
        update_stats()

    w.after(1000 // FPS, update)


def update_stats():
    player = tanks_collection.get_player()
    if player:
        stats_label.config(
            text=f"HP: {player.get_hp()}   Ammo: {player.get_ammo()}   Fuel: {int(player.get_fuel())}   Speed: {player.get_speed()}")


def key_press(event):
    player = tanks_collection.get_player()
    if not player or not player.is_alive():
        return

    if event.keycode == KEY_W:
        player.forward()
    elif event.keycode == KEY_S:
        player.backward()
    elif event.keycode == KEY_A:
        player.left()
    elif event.keycode == KEY_D:
        player.right()
    elif event.keycode == KEY_UP:
        world.move_camera(0, -5)
    elif event.keycode == KEY_DOWN:
        world.move_camera(0, 5)
    elif event.keycode == KEY_LEFT:
        world.move_camera(-5, 0)
    elif event.keycode == KEY_RIGHT:
        world.move_camera(5, 0)
    elif event.keycode == KEY_SPACE:
        player.fire()


def load_textures():
    texture.load('tank_down', 'img/tank_down.png')
    texture.load('tank_up', 'img/tank_up.png')
    texture.load('tank_left', 'img/tank_left.png')
    texture.load('tank_right', 'img/tank_right.png')

    texture.load('tank_down_player', 'img/tank_down_player.png')
    texture.load('tank_up_player', 'img/tank_up_player.png')
    texture.load('tank_left_player', 'img/tank_left_player.png')
    texture.load('tank_right_player', 'img/tank_right_player.png')

    texture.load(world.BRICK, 'img/brick.png')
    texture.load(world.WATER, 'img/water.png')
    texture.load(world.CONCRETE, 'img/wall.png')
    texture.load(world.MISSLE, 'img/bonus.png')
    texture.load(world.HEART, 'img/heart.png')
    texture.load(world.TURBO, 'img/молния.png')

    texture.load('missile_up', 'img/missile_up.png')
    texture.load('missile_down', 'img/missile_down.png')
    texture.load('missile_left', 'img/missile_left.png')
    texture.load('missile_right', 'img/missile_right.png')

    print("Все текстуры загружены!")


w = Tk()
load_textures()
w.title("ТАНКИ")
canv = Canvas(w, width=world.SCREEN_WIDTH, height=world.SCREEN_HEIGHT, bg='#8ccb5e')
canv.pack()

# Табличка сдвинута левее - x=world.SCREEN_WIDTH - 370 (было -320)
stats_label = Label(w, text="HP: 100   Ammo: 100   Fuel: 10000   Speed: 5",
                    font=("Arial", 12, "bold"),
                    bg="black", fg="white",
                    padx=15, pady=8)
stats_label.place(x=world.SCREEN_WIDTH - 370, y=10)

world.initialize(canv)
tanks_collection.initialize(canv)
missiles_collection.initialize(canv)

w.bind('<KeyPress>', key_press)
update()
w.mainloop()
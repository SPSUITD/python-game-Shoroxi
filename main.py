from ursina import *
import setting
import main_menu

from game import Player
from game import Gameplay
from game import Level

import my_json
import os.path

options = None

if __name__ == "__main__":

    if os.path.isfile("assets/options.json"):
        options = my_json.read("assets/options")

    window.borderless = True
    window.cog_button = False
    window.vsync = True
    window.forced_aspect_ratio = options["aspect"][0]/options["aspect"][1]
    #print(window.aspect_ratio)
    #window.fullscreen_size = (options["window_size"][0], options["window_size"][1])
    #window.size = (options["window_size"][0], options["window_size"][1])
    #window.fixed_size = window.size

    app = Ursina()

    if options["autodetect"]:
        window.fullscreen = True
    else:
        window.fullscreen = False

    window.cog_button = False

    # НАСТРОЙКА ПЕРЕМЕННЫХ, ПРИЛОЖЕНИЯ, ДВИЖКА
    scene = None
    # window.icon = "Icon.ico"
    window.title = setting.title
    window.fps_counter.enabled = True
    window.fps_counter.position = (100, 100)
    window.exit_button.visible = setting.window_show_quit_button

    window.color = color.black
    mouse.enabled = setting.cursor
    # mouse.locked = setting.cursor_lock
    Text.default_font = setting.game_font

    text.default_resolution = 720 * Text.size
    Texture.default_filtering = False
    application.development_mode = True

    load_scene = Gameplay()
    menu_scene = main_menu.MainMenu()

    # НАСТРОЙКА БОЛЬШОГО СВЕТА
    # camera.ui
    from UrsinaLighting import *

    color_sky_night2 = color.rgb(40, 40, 40)
    color_sky_night = color.rgb(10, 10, 10)

    DL = Entity()
    DirectionalLight(parent=DL, y=35, rotation=(45, 0, 0), shadows=True)
    # PointLight(parent=DL, position=load_scene.player.camera_pivot,direction=Vec3(camera.forward), color=(0,0.5,0,0), shadows=True)
    AmbientLight(color=color_sky_night2)
    # lit = LitInit()
    # LitSpotLight(position=scene1.player.camera_pivot,direction=Vec3(camera.forward),range=6)

    app.run()

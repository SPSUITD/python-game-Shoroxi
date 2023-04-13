from ursina import *
import setting
import main_menu
from direct.filter.CommonFilters import CommonFilters
from ursina.shaders import fxaa_shader

from game import Player
from game import Gameplay
from game import Level
from game import Trigger
from game import Audio3d

import my_json
import os.path
import os

from direct.showbase import Audio3DManager

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

    application.development_mode = False
    # Filters
    Texture.default_filtering = False
    filters = CommonFilters(app.win, app.cam)

    filters.setCartoonInk(separation=0.8, color=(0,0,0,0.5))
    filters.setAmbientOcclusion(radius=0.02,falloff=0.009)

    filters.setSrgbEncode()
    filters.setHighDynamicRange()

    # Anti-aliasing
    filters.set_msaa(samples=8)
    camera.shader = fxaa_shader

    scene = Gameplay()
    scene = main_menu.MainMenu()

    app.run()

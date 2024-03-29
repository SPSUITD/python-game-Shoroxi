from ursina import *
import setting
import my_json
import main as gm
import os.path
import ui
import ursina

scene = None
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

bg_options = "bg_test.png"
bg_main_menu = "bg_test.png"

class MainMenu(Entity):

    def __init__(self):
        super().__init__(parent=camera.ui)
        global scene
        scene = self

        self.menu_buttons_counter = 0
        self.menu_buttons_list = [
            "Новая игра",
            "Настройки",
            "Выход"
        ]
        self.click_sound = Audio(sound_folder + "click", autoplay=False, loop=False)
        self.main_menu = Entity(parent=self, enabled=True)
        Entity(parent=self.main_menu, model="quad", color=rgb(2, 2, 0), scale=2)
        Sprite(parent=self.main_menu, texture=bg_main_menu, y=0.1, scale=0.5)
        self.menu_punkt = Text(parent=self.main_menu, text="← {0} →".format(self.menu_buttons_list[self.menu_buttons_counter]),
                               origin=(0, 0), y=-0.4,
                               color=setting.color_orange)

    def StartNewGame(self,level=None):
        camera.overlay.color = color.black
        loading = Text("Загрузка", origin=(0, 0), color=setting.color_orange, always_on_top=True)
        destroy(loading, delay=2)
        invoke(gm.Gameplay,level=level, delay=1)
        destroy(self)
        invoke(setattr, camera.overlay, 'color', color.clear, delay=2)

    def input(self, key):
        if self.main_menu.enabled:
            if key == "a" or key == "left arrow":
                self.click_sound.play()
                if self.menu_buttons_counter > 0:
                    self.menu_buttons_counter -= 1
                else:
                    self.menu_buttons_counter = 2
            if key == "d" or key == "right arrow":
                self.click_sound.play()
                if self.menu_buttons_counter < 2:
                    self.menu_buttons_counter += 1
                else:
                    self.menu_buttons_counter = 0
            if key == "enter":
                if self.menu_buttons_counter == 0:
                    self.StartNewGame()
                if self.menu_buttons_counter == 1:
                    self.main_menu.enabled = False
                    Options().options_menu.enabled = True
                if self.menu_buttons_counter == 2: application.quit()
            self.menu_punkt.text = "← {0} →".format(self.menu_buttons_list[self.menu_buttons_counter])

class Options(Entity):
    def __init__(self):
        super().__init__()

        self.click_sound = Audio(sound_folder + "click", autoplay=False, loop=False)
        self.options = my_json.read("assets/options")
        self.options_menu = Entity(parent=camera.ui, enabled=False)

        self.sens = self.options["mouse_sensitivity"]
        self.fps_show_mode = self.options["show_fps"]
        self.fullscreen = self.options["fullscreen"]
        self.window_size = self.options["window_size"]

        self.option_selector = 0
        self.option_punkts_list = []
        self.value_selector = 0

        Entity(parent=self.options_menu, model="quad", color=rgb(2, 2, 0), scale=2)

        self.frame = Sprite(bg_options, parent=self.options_menu, scale=0.222)

        # --------------------------
        Text(parent=self.options_menu,
             text="Настройки", y=window.top.y - 0.1, origin=(0.05, 0),
             color=setting.color_orange)
        # -------------
        self.lang_punkt = Text(parent=self.options_menu, text="mouse_sens", origin=(-.5, 0), x=-0.4,
                               y=0.2)
        self.lang_text = ui.UIText(parent=self.options_menu, color=setting.color_orange,
                                   text="[{0}]".format(self.sens),
                                   origin=(.5, -.5), x=0.3, y=0.21)
        # -------------
        self.fps_punkt = Text(parent=self.options_menu, text="Отображение фпс", origin=(-.5, 0), x=-0.4, y=0.15)
        self.fps_text = ui.UIText(parent=self.options_menu, color=setting.color_orange,
                                  text="[{0}]".format("Да" if self.options["show_fps"] else "Нет"),
                                  origin=(.5, -.5), x=0.3, y=0.16)
        # -------------
        self.autodetect_punkt = Text(parent=self.options_menu, text="На весь экран", origin=(-.5, 0), x=-0.4, y=0.08)
        self.auto_text = ui.UIText(parent=self.options_menu, color=setting.color_orange,
                                   text="[{0}]".format("Да" if self.options["fullscreen"] else "Нет"),
                                   origin=(.5, -.5), x=0.3, y=0.07)
        # -------------
        self.apply_punkt = Text(parent=self.options_menu,
                                text="Применить", origin=(0, 0), color=setting.color_orange,
                                y=-0.3)
        # --------------------------
        self.option_punkts_list.append(self.lang_punkt)
        self.option_punkts_list.append(self.fps_punkt)
        self.option_punkts_list.append(self.autodetect_punkt)
        self.option_punkts_list.append(self.apply_punkt)

        self.selector = Sprite(texture="arrow_right", parent=self.options_menu,
                               y=self.option_punkts_list[self.option_selector].y,
                               x=self.option_punkts_list[self.option_selector].x - 0.05,
                               scale=.1,
                               origin=(-.5, 0))
        self.tip_bottom = Text(
            dedent("Здесь могла быть подсказка").strip(),
            parent=self.options_menu, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)

    def input(self, key):
        if self.enabled and key == "escape":
            scene.main_menu.enable()
            self.option_selector = 0
            self.options_menu.disable()
        # ------------ Selector ---------------
        if key == "w" or key == "up arrow":
            if self.option_selector > 0:
                self.option_selector -= 1
            else:
                self.option_selector = len(self.option_punkts_list) - 1
            self.selector.y = self.option_punkts_list[self.option_selector].y
        if key == "s" or key == "down arrow":
            if self.option_selector < len(self.option_punkts_list) - 1:
                self.option_selector += 1
            else:
                self.option_selector = 0
            self.selector.y = self.option_punkts_list[self.option_selector].y
        # ------------ Values ---------------
        if self.enabled and key == "d" or key == "right arrow":
            self.click_sound.play()
            if self.option_selector == 0:
                if self.value_selector < 2:
                    self.value_selector += 1
                else:
                    self.value_selector = 0
                self.sens = setting.mouse_sensitivity[self.value_selector]
                self.lang_text.setText("[{0}]".format(self.sens))
        if self.enabled and key == "a" or key == "left arrow":
            self.click_sound.play()
            if self.option_selector == 0:
                if self.value_selector > 0:
                    self.value_selector -= 1
                else:
                    self.value_selector = 2
                self.sens = setting.mouse_sensitivity[self.value_selector]
                self.lang_text.setText("[{0}]".format(self.sens))
        if self.enabled and key == "enter" or key == "d" or key == "a" \
                or key == "right arrow" or key == "left arrow":
            self.click_sound.play()
            if self.option_selector == 1:
                self.fps_show_mode = not self.fps_show_mode
                self.fps_text.setText("[{0}]".format("yes" if self.fps_show_mode else "no"))
            elif self.option_selector == 2:
                self.fullscreen = not self.fullscreen
                self.auto_text.setText("[{0}]".format("yes" if self.fullscreen else "no"))

            # ------------ Apply ---------------

            if self.option_selector == len(self.option_punkts_list) - 1:
                my_json.change_key("assets/options", "mouse_sensitivity", self.sens)
                my_json.change_key("assets/options", "show_fps", self.fps_show_mode)
                my_json.change_key("assets/options", "fullscreen", self.fullscreen)

                scene.main_menu.enable()
                self.option_selector = 0
                self.options_menu.disable()

if __name__ == '__main__':
    app = Ursina()
    app.run()

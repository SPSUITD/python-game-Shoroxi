from ursina import *
import setting
import my_json
import main as gm
import os.path
import ui

scene = None
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

cursor = ui_folder + "set.ico"
bg_options = "/bg_test.png"
bg_mm = "bg_test.png"

class MainMenu(Entity):

    def __init__(self):
        super().__init__(parent=camera.ui, z=-0.001)
        global scene
        scene = self
        self.menu_buttons_counter = 0
        self.menu_buttons_list = [
            "Новая игра",
            "Настройки",
            "Выход"
        ]
        self.click_sound = Audio(sound_folder + "spider_hiss", autoplay=False, loop=False)
        self.main_menu = Entity(parent=self, enabled=True)
        Entity(parent=self.main_menu, model="quad", color=rgb(2, 2, 0), scale=2)
        Sprite(parent=self.main_menu, texture=bg_mm, y=0.1, scale=0.5)
        self.menu_punkt = Text(parent=self.main_menu, text="← {0} →".format(self.menu_buttons_list[self.menu_buttons_counter]),
                               origin=(0, 0), y=-0.4,
                               color=setting.color_orange)

    def StartNewGame(self,level=None):
        camera.overlay.color = color.black
        loading = Text("loading", origin=(0, 0), color=setting.color_orange, always_on_top=True)
        destroy(loading, delay=2)
        invoke(gm.Gameplay,level=level, delay=1)
        destroy(self)
        invoke(setattr, camera.overlay, 'color', color.clear, delay=2)
        self.ignore_input = False
        #invoke(story.show_intro_text,delay=2)

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
        super().__init__(z=0.002)
        global scene

        # -----------------------
        self.click_sound = Audio(sound_folder + "click", autoplay=False, loop=False)
        self.options = my_json.read("assets/options")
        self.options_menu = Entity(parent=camera.ui, enabled=False)

        self.fps_show_mode = self.options["show_fps"]
        self.autodotect_size = self.options["autodetect"]

        self.option_selector = 0
        self.option_punkts_list = []
        Entity(parent=self.options_menu, model="quad", color=rgb(2, 2, 0), scale=2)

        self.frame = Sprite(bg_options, parent=self.options_menu, scale=0.222)

        # --------------------------
        Text(parent=self.options_menu,
             text="Настройки", y=window.top.y - 0.1, origin=(0.05, 0),
             color=setting.color_orange)
        # -------------
        self.lang_punkt = Text(parent=self.options_menu, text="Что-то", origin=(-.5, 0), x=-0.4,
                               y=0.2)
        self.lang_text = ui.UIText(parent=self.options_menu, color=setting.color_orange,
                                   text="[{0}]".format("Да" if self.options["show_fps"] else "Нет"),
                                   origin=(.5, -.5), x=0.3, y=0.21)
        # -------------
        self.fps_punkt = Text(parent=self.options_menu, text="Отображение фпс", origin=(-.5, 0), x=-0.4, y=0.15)
        self.fps_text = ui.UIText(parent=self.options_menu, color=setting.color_orange,
                                  text="[{0}]".format("Да" if self.options["show_fps"] else "Нет"),
                                  origin=(.5, -.5), x=0.3, y=0.16)
        # -------------
        self.autodetect_punkt = Text(parent=self.options_menu, text="авто разрешение", origin=(-.5, 0), x=-0.4, y=0.08)
        self.auto_text = ui.UIText(parent=self.options_menu, color=setting.color_orange,
                                   text="[{0}]".format("Да" if self.options["autodetect"] else "Нет"),
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

        self.selector = Sprite(cursor, parent=self.options_menu,
                               y=self.option_punkts_list[self.option_selector].y,
                               x=self.option_punkts_list[self.option_selector].x - 0.05, scale=.01,
                               origin=(-.5, 0))
        self.message = None
        self.tip_bottom = Text(
            dedent("control.tip").strip(),
            parent=self.options_menu, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)

    def input(self, key):
        if self.enabled and key == "escape":
            scene.main_menu.enable()
            self.option_selector = 0
            self.options_menu.disable()

        if key == "w" or key == "up arrow":
            if self.option_selector > 0:
                self.option_selector -= 1
            else:
                self.option_selector = len(self.option_punkts_list) - 1

            if self.option_selector == len(self.option_punkts_list) - 1:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.15,
                                          self.option_punkts_list[self.option_selector].y)
            else:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.05,
                                          self.option_punkts_list[self.option_selector].y)

        if key == "s" or key == "down arrow":
            if self.option_selector < len(self.option_punkts_list) - 1:
                self.option_selector += 1
            else:
                self.option_selector = 0

            if self.option_selector == len(self.option_punkts_list) - 1:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.15,
                                          self.option_punkts_list[self.option_selector].y)
            else:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.05,
                                          self.option_punkts_list[self.option_selector].y)

        if self.enabled and (key == "enter") or key == "d" or key == "a" or key == "right arrow" or key == "left arrow":
            self.click_sound.play()
            if self.option_selector == 0:
                self.fps_show_mode = not self.fps_show_mode
                self.fps_text.setText("[{0}]".format("yes" if self.fps_show_mode else "no"))
            elif self.option_selector == 1:
                self.fps_show_mode = not self.fps_show_mode
                self.fps_text.setText("[{0}]".format("yes" if self.fps_show_mode else "no"))
            elif self.option_selector == 2:
                self.autodotect_size = not self.autodotect_size
                self.auto_text.setText("[{0}]".format("yes" if self.autodotect_size else "no"))

            if self.option_selector == len(self.option_punkts_list) - 1:
                # my_json.change_key ("assets/options", "show_fps", self.fps_show_mode)
                # my_json.change_key ("assets/options", "autodetect", self.autodotect_size)
                scene.main_menu.enable()
                self.option_selector = 0
                self.options_menu.disable()

if __name__ == '__main__':
    app = Ursina()
    app.run()

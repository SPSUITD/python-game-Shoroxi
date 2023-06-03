from ursina import *
import setting
import game
import main_menu

ui_folder = "assets/ui/"

class UIText(Text):
    def hideHUD(self):
        return color.rgba(1,1,1,0) if not setting.show_hud else color.rgba(1,1,1,1)

    def __init__(self,text="",origin=(0,0), color=color.white,**kwargs):
        super().__init__(parent=camera.ui, origin=origin)
        self.shadow = True
        self.origin_text = Text(text=dedent(text).strip(), parent=self,
                                origin=self.origin,color = color,x=self.x,
                                y=self.y,z=self.z)
        for key, value in kwargs.items ():
            setattr (self, key, value)
    def setText(self,text):
        self.origin_text.text = dedent(text).strip()

class GameOverScreen(Entity):
    def __init__(self,**kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True)
        Entity(parent=self, model="quad", color=color.rgba(2, 2, 0, 255),
               scale=window.size, position=(0, 0))
        Text("gameover",parent=self,origin=(0,0))
        for key, value in kwargs.items ():
            setattr(self, key, value)

    def input(self,key):
        if self.enabled:
            if key == "escape" or key == "enter":
                destroy(game.game_session)
                scene.clear()
                game.pause = False
                camera.overlay.color = color.black
                loading = Text("Загрузка", origin=(0, 0), color=color.orange, always_on_top=True)

                invoke(main_menu.MainMenu, delay=0.0001)
                destroy(self)
                destroy(loading)
                invoke(setattr, camera.overlay, 'color', color.clear, delay=1)
                application.paused = False

class GamePause(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.selected_element = 0
        self.menu_punkts = [
            Text("Продолжить", color=color.orange),
            Text("Вернуться в главное меню", color=color.orange)
        ]
        self.parent = camera.ui
        Entity(parent=self, model="quad", color=rgb(2, 2, 0), scale=window.size)
        self.frame = Sprite(ui_folder + "Pause texture", parent=self, scale=0.222,z=-0.001)
        self.click_sound = Audio("assets/sounds/click", autoplay=False, loop=False)
        Text("Menu Title", parent=self, y=0.35, x=0, origin=(0, 0))
        Text("Pause Title", parent=self, y=0.30, x=0, origin=(0, 0))
        self.tip_bottom = Text(dedent("Здесь могла быть подсказка").strip(),
                               parent=self, y=-0.40, x=-0.7,z=-0.001, origin=(-.5, 0),
                               color=color.dark_gray, size=4)
        if self.menu_punkts:
            offset = 0.25
            spacing = .01
            height = 0.01 - spacing
            if isinstance(self.menu_punkts, dict):
                self.menu_punkts = self.menu_punkts.values()
            for p in self.menu_punkts:
                if isinstance(p, Text):
                    p.x -= .045
                    p.y = offset
                    p.parent = self
                    p.origin = (-.5, 0)
                    height += len(p.lines) / 100 * 7
                    p.y -= height
                    p.z = -0.01
            self.selector = Sprite(texture="arrow_right", parent=self,
                                   y=self.menu_punkts[self.selected_element].y,
                                   x=self.menu_punkts[self.selected_element].x - 0.05,
                                   scale=.21,
                                   origin=(-.5, 0))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def input(self, key):
        if game.pause and self.enabled:
            if key == "escape":
                game.pause = False
                self.disable()
            if key == "down arrow" or key == "s":
                self.click_sound.play()
                self.selected_element += 1
                if self.selected_element > len(self.menu_punkts) - 1:
                    self.selected_element = 0
                self.selector.y = self.menu_punkts[self.selected_element].y
            if key == "up arrow" or key == "w":
                self.click_sound.play()
                self.selected_element -= 1
                if self.selected_element < 0:
                    self.selected_element = len(self.menu_punkts) - 1
                self.selector.y = self.menu_punkts[self.selected_element].y
            if key == "enter":
                if self.selected_element == 0:
                    game.pause = False
                    self.disable()

                if self.selected_element == len(self.menu_punkts) - 1:
                    destroy(game.game_session.enemy)
                    destroy(game.game_session.player)
                    destroy(game.game_session)
                    scene.clear()
                    game.pause = False

                    camera.overlay.color = color.black
                    loading = Text("Загрузка", origin=(0, 0), color=color.orange, always_on_top=True)
                    invoke(main_menu.MainMenu, delay=0.0001)
                    destroy(self)
                    destroy(loading)
                    invoke(setattr, camera.overlay, 'color', color.clear, delay=1)
                    application.paused = False
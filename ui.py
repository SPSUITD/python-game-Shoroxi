from ursina import *
import setting
import game
import main_menu
ui_folder = "assets/ui/"
message_box = ui_folder+"message_box.png"
class UIText(Text):
    def hideHUD(self):
        return color.rgba(1,1,1,0) if not setting.show_hud else color.rgba(1,1,1,1)

    def __init__(self,text="",origin=(0,0),offset=(0.001,0.001), color=color.white,**kwargs):
        super().__init__(parent=camera.ui, origin=origin)
        self.shadow = True

        if self.shadow:
            self.shadow_text = Text(text=dedent(text).strip(),parent=self,origin=self.origin,x=self.x+offset[0],
                                y=self.y-offset[1],color=rgb(10,10,10) if setting.show_hud else self.hideHUD(),z=self.z+0.001)
        self.origin_text = Text(text=dedent(text).strip(), parent=self, origin=self.origin,color = color,x=self.x,
                                y=self.y,z=self.z)

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def setText(self,text):
        if self.shadow:
            self.shadow_text.text = text
        self.origin_text.text = dedent(text).strip()

# MESSAGE BOX
class MessageBox(Entity):
    def __init__(self, title, message, type="info", **kwargs):
        super().__init__(parent=camera.ui,z=-999)
        self.ignored_input_entity = None
        Entity(parent=self, model="quad", color=color.rgba(2,2,0,200), scale = (1*window.aspect_ratio,1),position=(0,0))
        Sprite(message_box,parent=self,scale=0.25, position=(0, 0))

        self.title = UIText(title,shadow=True, parent=self,color=setting.color_orange,origin=(-.5,0),position=(-.32,0.168))
        self.close = Button("OK",position=(0,-0.15),scale=(0.1,0.04),parent=self)
        self.close.on_click = self.close_window
        self.message = Text(parent=self, text=dedent(message).strip(), origin=(-.5, .5),wordwrap=33,
                            position=(-.3,0.14)).set_scissor(Vec3(-1,-0.3,0), Vec3(1,1,0))

        self.msg_box_type = type
        game.pause = True
        game.get_player().mouse_control = False
        mouse.locked = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def close_window(self):
        game.pause = False
        game.get_player().mouse_control = True
        mouse.locked = True

        if self.ignored_input_entity is not None:
            self.ignored_input_entity.ignore_input = False

        invoke(destroy, self, delay=0.0001)

    def input(self,key):
        if key == "enter" or key == "escape":
            self.close_window()

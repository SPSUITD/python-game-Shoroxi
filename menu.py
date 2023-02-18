from ursina import *

class MainMenu(Entity):
    def __init__(self, player):
        super().__init__(
            parent=camera.ui,
            ignore_paused=True
        )

        self.main_menu = Entity(parent=self, enabled=True)
        self.options_menu = Entity(parent=self, enabled=False)
        self.help_menu = Entity(parent=self, enabled=False)
        self.player = player
        self.background = Sprite('shore', color=color.dark_gray, z=1)

        Text("MAIN MENU", parent=self.main_menu, y=0.4, x=0, origin=(0,0))

        def switch(menu1, menu2):
            menu1.enable()
            menu2.disable()

        def play():
            self.player.enable()
            mouse.locked = True
            self.main_menu.disable()
            self.background.disable()
            # TODO: Loading screen
            t = Text('''\nКошмар''', font='unifont.ttf', scale=3, origin=(0, 0))
            t.appear(speed=.05)
            t.fade_out(delay=3, duration=1, curve=curve.linear)



        # Button list
        ButtonList(button_dict={
            "Start": Func(play),
            "Options": Func(lambda: switch(self.options_menu, self.main_menu)),
            "Help": Func(lambda: switch(self.help_menu, self.main_menu)),
            "Exit": Func(lambda: application.quit())
        },y=0,parent=self.main_menu)

        # [OPTIONS MENU] WINDOW START

        Text ("OPTIONS MENU", parent=self.options_menu, y=0.4, x=0, origin=(0, 0))

        # Button
        Button("Back",parent=self.options_menu,y=-0.3,scale=(0.1,0.05),color=rgb(50,50,50),
               on_click=lambda: switch(self.main_menu, self.options_menu))

        # [HELP MENU] WINDOW START
        Text ("HELP MENU", parent=self.help_menu, y=0.4, x=0, origin=(0, 0))

        ButtonList (button_dict={
            "Gameplay": Func(print_on_screen,"You clicked on Gameplay help button!", position=(0,.1), origin=(0,0)),
            "Battle": Func(print_on_screen,"You clicked on Battle help button!", position=(0,.1), origin=(0,0)),
            "Control": Func(print_on_screen,"You clicked on Control help button!", position=(0,.1), origin=(0,0)),
            "Back": Func (lambda: switch(self.main_menu, self.help_menu))
        }, y=0, parent=self.help_menu)

    def menu_input(self, key):

        if self.main_menu.enabled and key == "escape":
            application.quit()
        elif self.options_menu.enabled and key == "escape":
            self.main_menu.enable()
            self.options_menu.disable()
        elif self.help_menu.enabled and key == "escape":
            self.main_menu.enable()
            self.help_menu.disable()

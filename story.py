from ursina import *
import game
import ui

def show_intro_text():
    intro_window = ui.UIWindow()
    Sprite("assets/ui/wnd_3.png",position=(0,0),world_parent=intro_window,scale=1)

def first_qs():
    game.get_player().quests.add_quest("quest_1")
    invoke(game.show_message, "Найдите радио", 5, delay=0.001)

def two_qs():
    if game.get_player().quests.has_quest("quest_1"):
        game.get_player().quests.get_quest("quest_1").complete()
        game.get_player().quests.add_quest("quest_find_camp")
        invoke(game.show_message, "Вы прошли игру", 5, delay=0.001)
        print(game.get_current_status())

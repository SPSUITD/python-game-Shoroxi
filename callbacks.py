import game
import ui

# TODO: quests load

def check_level(lvl_name):
    if game.get_current_level_id() == lvl_name:
        return True
    else:
        return False

def on_level_loaded():
    if check_level("test"):
        print("FIRST IN VILLAGE")

def on_game_started():
    pass

def on_quest_add(quest):
    pass
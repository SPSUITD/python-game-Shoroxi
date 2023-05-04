from ursina import *
import my_json
import game
import callbacks

system = None

class Quests():
    def __init__(self):
        global system
        self.quests_list = []
        self.active_quest = None
        self.player = None
        system = self
        self.q_file = my_json.read("assets/quests")

    def add_quest(self, quest_id):
        for q in self.q_file:
            if q["id"] == quest_id:
                self.quests_list.append(quest_element(q["id"], q["title"], q["quest_items"]))
                print("добавил задание {0}".format(q["id"]))
                break

        invoke(callbacks.on_quest_add, self)

    def has_quest(self, quest_id):
        for q in self.quests_list:
            if q.id == quest_id:
                return True
            else:
                return False

    def get_quest(self, quest_id):
        for q in self.quests_list:
            if q.id == quest_id:
                return q

class quest_element():
    def __init__(self, id=None, title="", quest_items=[]):
        self.id = id
        self.title = title
        self.quest_items = quest_items

    def check(self):
        pass

    def complete(self):
        has_all_items = False
        q_item_need_count = 0

        for itm in self.quest_items:
            for inv_itm in game.get_player().inventory.items_in_inventory:
                if itm == inv_itm.item_id:
                    print("Item [{0}] in inventory!".format(itm))
                    q_item_need_count += 1
        print("[DEBUG QUEST] need item count [{0}]".format(q_item_need_count))

        if q_item_need_count == len(self.quest_items):
            has_all_items = True

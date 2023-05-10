from ursina import *
import my_json

i_db = my_json.read("assets/items")
player_creature = my_json.read("assets/player")

class ItemNew():
    def __init__(self, **kwargs):
        super().__init__()
        self.item_id = ""
        self.item_data = {}
        self.item_count = 1

        for key, value in kwargs.items():
            setattr(self, key, value)

# Inventory system class
class Inventory(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=-0.001)
        self.items_in_inventory = []
        self.stack_items = True

        # >> Add items from player.json file
        for item in player_creature["start_items"]:
            self.add_item(item)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_item(self, item_id):
        if item_id in i_db:
            if not has_item:
                self.items_in_inventory.append(
                    ItemNew(item_id=item_id, item_data=i_db[item_id]))
                print("Подобрал [{0}]".format(item_id),1)
        else:
            print("Ошибка Item ID - [{0}]! объект не найден в assets/items.json!".format(item_id),1)

    def has_item(self, item_id):
        if item_id in self.items_in_inventory:
            return True

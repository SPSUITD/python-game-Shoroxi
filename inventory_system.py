from ursina import *
import my_json

i_db = my_json.read("assets/items")
player_creature = my_json.read("assets/player")

class Inventory(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=-0.001)
        self.items_in_inventory = []
        self.stack_items = True

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_items_count(self):
        return len(self.items_in_inventory)

    def add_item(self, item_id):
        if item_id in i_db:
            self.items_in_inventory.append(item_id)
            print("Inventory: Подобрал [{0}]".format(item_id))
        else:
            print("Inventory: Ошибка Item ID - [{0}]! объект не найден в data/items.json!".format(item_id))

    def has_item(self, item_id):
        if self.items_in_inventory:
            for item in self.items_in_inventory:
                if item == item_id:
                    return True

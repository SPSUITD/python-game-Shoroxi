import json
import os
# by leksi
def read(asset):
    with open(asset+".json", "r", encoding="utf8") as read_file:
        data = json.load(read_file)

    return data

# Смена значения в заданном ключе
def change_key(asset,key,value):
    a_file = open (asset+".json", "r",encoding="utf8")
    json_object = json.load(a_file)
    a_file.close()

    json_object[key] = value

    a_file = open (asset+".json", "w")
    json.dump(json_object, a_file,sort_keys=True,indent=4)
    a_file.close()

def create_key(asset,key,value):
    json_object = {}

    if os.path.isfile(asset+".json"):
        change_key(asset,key,value)
    else:

        json_object[key] = value

        a_file = open(asset+".json","x")
        json.dump(json_object,a_file,sort_keys=True,indent=4)
        a_file.close()

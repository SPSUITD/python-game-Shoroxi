from ursina import *
from direct.actor.Actor import Actor

app = Ursina()
anim_folder = "assets/animations/low.gltf"

entity = Entity()
# animations are stored within the file
actor = Actor(anim_folder)
actor.reparent_to(entity)
actor.loop("MXManim")

app.run()

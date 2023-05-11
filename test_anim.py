from ursina import *
from direct.actor.Actor import Actor

app = Ursina()
anim_folder = "assets/animations/low.gltf"

entity = Entity()
actor = Actor(anim_folder)
actor.reparent_to(entity)
actor.loop("MXManim")



app.run()

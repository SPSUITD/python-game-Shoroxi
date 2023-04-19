# ## FLASHLIGHT
# self.FlashlightNode = NodePath('Flashlight Node')
# self.FlashlightNode.reparentTo(camera)
#
# self.FlashlightLens = PerspectiveLens()
# self.FlashlightLens.setFov(25)
#
# self.Flashlight = PitoSpotLight()
# self.Flashlight._light.setLens(self.FlashlightLens)
# self.flashlight = PitoSpotLight(shadows=True,
#                                color=color.rgba(255, 255, 255, 1),
#                                position=(0, 0, 0),
#                                rotation=camera.rotation,
#                                distance=0.01,
#                                parent=camera,
#                                lens=self.FlashlightLens,
#                                name="flashlight",
#                                enabled=False)
#
# self.FlashlightNodePath = self.FlashlightNode.attachNewNode(self.flashlight._light)
#
# self.proj = render.attachNewNode(LensNode('proj'))
# self.proj.node().setLens(self.FlashlightLens)
#
# self.proj.reparentTo(self.FlashlightNode)



from ursina import *
from direct.actor.Actor import Actor

app = Ursina()
anim_folder = "assets/animations/low.gltf"

entity = Entity()
#animations are stored within the file
actor = Actor(anim_folder)
actor.reparent_to(entity)

actor.loop("MXManim")

app.run()
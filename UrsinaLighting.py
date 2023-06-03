from ursina import *

vert, frag = open("shaders/vert.glsl", "r"), open("shaders/frag.glsl", "r")
LitShader = Shader(language=Shader.GLSL, vertex=vert.read(), fragment=frag.read())
vert.close()
frag.close()

LitTime = 0

class LitInit(Entity):
    def __init__(self):
        super().__init__(
            model = None
        )

    def update(self):
        global LitTime
        LitTime += time.dt

class LitDirectionalLight():
    def __init__(self, direction=Vec3(0), color=Vec3(1), intensity=0):
        self.sun = DirectionalLight(shadows=False)
        self.sun.look_at(direction)

        LitLightList[0] = Vec4(color.x, color.y, color.z, 1)
        LitLightList[1] = Vec4(direction.x, direction.y, direction.z, intensity)

    @staticmethod
    def setIntensity(intensity=1):
        LitLightList[1].w = intensity

    @staticmethod
    def setColor(color=Vec3(1)):
        LitLightList[0].xyz = color

    @staticmethod
    def setDirection(direction=Vec3(-1)):
        LitLightList[1].xyz = direction

    def toggleShadows(self):
        self.sun.shadows = not self.sun.shadows
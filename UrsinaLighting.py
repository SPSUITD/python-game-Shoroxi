from ursina import *
import numpy as np

vert, frag = open("shaders/vert.glsl", "r"), open("shaders/frag.glsl", "r")
LitShader = Shader(language=Shader.GLSL, vertex=vert.read(), fragment=frag.read())
vert.close()
frag.close()

# list containing all light data
LitLightList = [Vec4(1), Vec4(0)]
LitSpotList = [Vec4(1), Vec4(0), Vec4(0)]

LitTime = 0

class LitInit(Entity):
    def __init__(self):
        super().__init__(
            model = None
        )
    
    def update(self):
        global LitTime
        LitTime += time.dt

# по хорошему через это надо прогружать все объекты уровня
class LitObject(Entity):
    def __init__(self, model='plane', scale=1, position=(0, 0, 0), rotation=(0, 0, 0), texture=None, collider=None,
                 color=rgb(255, 255, 255), tiling=Vec2(1), lightDirection=Vec3(0), lightColor=Vec3(1),
                 smoothness=128, ambientStrength=0.1, normalMap=None, specularMap=None, water=False, cubemap="Textures/cubemap_#.jpg", cubemapIntensity=0.5,
                 onUpdate=lambda self: None, **kwargs):
        super().__init__(
            shader=LitShader,
            model=model,
            collider=collider,
            position=position,
            rotation=rotation,
            scale=scale,
            texture=texture,
            color=color,
        )

        for key, value in kwargs.items():
            setattr(self, key, value)
        
        if normalMap == None: normalMap = Texture("Textures/default_norm.png")
        if specularMap == None: specularMap = Texture("Textures/default_spec.png")
        if water:
            normalMap = Texture("Textures/water_norm.png")
            smoothness = 512
        
        cubemaps = loader.loadCubeMap(cubemap)

        self.set_shader_input("tiling", tiling)
        self.set_shader_input("smoothness", smoothness)
        self.set_shader_input("ambientStrength", ambientStrength)
        self.set_shader_input("normalMap", normalMap)
        self.set_shader_input("specularMap", specularMap)
        self.set_shader_input("water", water)
        self.set_shader_input("cubemap", cubemaps)
        self.set_shader_input("cubemapIntensity", cubemapIntensity)
        self.onUpdate = onUpdate
    
    def update(self):
        self.set_shader_input("lightsArray", LitLightList)
        self.set_shader_input("lightsArrayLength", Vec2(len(LitLightList), len(LitSpotList)))
        self.set_shader_input("spotArray", LitSpotList)
        self.set_shader_input("time", LitTime)
        self.onUpdate(self)

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
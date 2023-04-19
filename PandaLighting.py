from ursina import *
from panda3d.core import PerspectiveLens

from panda3d.core import PointLight as PandaPointLight
from panda3d.core import Spotlight as PandaSpotLight

from panda3d.core import LVector3

class Light(Entity):
    def __init__(self, **kwargs):
        super().__init__(rotation_x=90)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._light.setColor(value)

class PointLight(Light):
    def __init__(self, distance=1, color=(1,1,1,1), **kwargs):
        super().__init__()
        self.keys = None
        self._light = PandaPointLight('point_light')
        self._light.attenuation = (1, 0, 2)
        self._light.max_distance = distance
        self._light.setColor(color)
        render.setLight(self.attachNewNode(self._light))

        for key, value in kwargs.items():
            setattr(self, key,value)

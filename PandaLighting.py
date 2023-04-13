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

class SpotLight(Light):
    def __init__(self, distance=1, color=(1,1,1,1), **kwargs):
        super().__init__()
        self.keys = None
        self._light = PandaSpotLight('spot_light')
        self._light.max_distance = distance
        self._light.setColor(color)
        self._light.setSpecularColor((0, 0, 0, 1))
        # The cone of a spotlight is controlled by it's lens. This creates the lens
        self._light.setLens(PerspectiveLens())
        # This sets the Field of View (fov) of the lens, in degrees for width
        # and height.  The lower the numbers, the tighter the spotlight.
        self._light.getLens().setFov(16, 16)
        # Attenuation controls how the light fades with distance.  The three
        # values represent the three attenuation constants (constant, linear,
        # and quadratic) in the internal lighting equation. The higher the
        # numbers the shorter the light goes.
        self._light.setAttenuation(LVector3(1, 0.0, 0.0))
        self._light.setExponent(60.0)
        # self._light.set_attenuation()
        # self._light.set_max_distance()
        render.setLight(self.attachNewNode(self._light))

        for key, value in kwargs.items():
            setattr(self, key,value)

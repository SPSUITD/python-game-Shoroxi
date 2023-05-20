from ursina import *
from panda3d.core import PointLight as PandaPointLight

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
    def __init__(self, distance=1, color=(0.05,0.05,0.05,0.05), **kwargs):
        super().__init__()
        self.keys = None
        self._light = PandaPointLight('point_light')
        self._light.attenuation = (1, 0, 2)
        self._light.max_distance = distance
        self._light.setColor(color)
        render.setLight(self.attachNewNode(self._light))
        self.light_id = None

        for key, value in kwargs.items():
            setattr(self, key,value)

    def get_light_id(self):
        return self.light_id

    def color_off(self, off):
        color = Vec4(0.3,0.3,0.3,0.3)
        if off:
            color = color * 0
        return self._light.setColor(color)

import ursina
from ursina.prefabs.first_person_controller import FirstPersonController

class Player(FirstPersonController):
    def __init__(self):
        super().__init__(
            model="cube",
            jump_height=0.5,
            jump_duration=0.2,
            origin_y=-2,
            collider="box",
            speed=7
        )
        ursina.destroy(self.cursor)
        self.cursor = ursina.Cursor(
            model=ursina.Mesh(vertices=[(-.5, 0, 0), (.5, 0, 0), (0, -.5, 0), (0, .5, 0)], triangles=[(0, 1), (2, 3)],
                              mode='line', thickness=2), scale=.02)
        self.disable()

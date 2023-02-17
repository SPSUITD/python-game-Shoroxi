from ursina import *
from Models import *
from direct.stdpy import thread

# class FirstPersonController(Entity):
#     def __init__(self, **kwargs):
#         self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
#         super().__init__()
#         self.speed = 5
#         self.height = 2
#         self.camera_pivot = Entity(parent=self, y=self.height)
#
#         camera.parent = self.camera_pivot
#         camera.position = (0,0,0)
#         camera.rotation = (0,0,0)
#         camera.fov = 90
#         mouse.locked = True
#         self.mouse_sensitivity = Vec2(40, 40)
#
#         self.gravity = 1
#         self.grounded = False
#         self.jump_height = 2
#         self.jump_up_duration = .5
#         self.fall_after = .35 # will interrupt jump up
#         self.jumping = False
#         self.air_time = 0
#
#         for key, value in kwargs.items():
#             setattr(self, key ,value)
#
#         # make sure we don't fall through the ground if we start inside it
#         if self.gravity:
#             ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
#             if ray.hit:
#                 self.y = ray.world_point.y
#
#
#     def update(self):
#         self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
#
#         self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
#         self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)
#
#         self.direction = Vec3(
#             self.forward * (held_keys['w'] - held_keys['s'])
#             + self.right * (held_keys['d'] - held_keys['a'])
#             ).normalized()
#
#         feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, ignore=(self,), distance=.5, debug=False)
#         head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, ignore=(self,), distance=.5, debug=False)
#         if not feet_ray.hit and not head_ray.hit:
#             move_amount = self.direction * time.dt * self.speed
#
#             if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, ignore=(self,)).hit:
#                 move_amount[0] = min(move_amount[0], 0)
#             if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, ignore=(self,)).hit:
#                 move_amount[0] = max(move_amount[0], 0)
#             if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, ignore=(self,)).hit:
#                 move_amount[2] = min(move_amount[2], 0)
#             if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, ignore=(self,)).hit:
#                 move_amount[2] = max(move_amount[2], 0)
#             self.position += move_amount
#
#             # self.position += self.direction * self.speed * time.dt
#
#         if self.gravity:
#             # gravity
#             ray = raycast(self.world_position+(0,self.height,0), self.down, ignore=(self,))
#             # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))
#
#             if ray.distance <= self.height+.1:
#                 if not self.grounded:
#                     self.land()
#                 self.grounded = True
#                 # make sure it's not a wall and that the point is not too far up
#                 if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
#                     self.y = ray.world_point[1]
#                 return
#             else:
#                 self.grounded = False
#
#             # if not on ground and not on way up in jump, fall
#             self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
#             self.air_time += time.dt * .25 * self.gravity
#
#
#     def input(self, key):
#         if key == 'space':
#             self.jump()
#
#
#     def jump(self):
#         if not self.grounded:
#             return
#
#         self.grounded = False
#         self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
#         invoke(self.start_fall, delay=self.fall_after)
#
#
#     def start_fall(self):
#         self.y_animator.pause()
#         self.jumping = False
#
#     def land(self):
#         # print('land')
#         self.air_time = 0
#         self.grounded = True
#
#     def on_enable(self):
#         mouse.locked = True
#         self.cursor.enabled = True
#
#
#     def on_disable(self):
#         mouse.locked = False
#         self.cursor.enabled = False

# class LoadingWheel(Entity):
#     def __init__(self, **kwargs):
#         super().__init__()
#         self.parent = camera.ui
#         self.point = Entity(
#             parent=self,
#             model=Circle(24, mode='line', thickness=3),
#             color=color.light_gray,
#             y=.75,
#             scale=2
#             )
#         self.scale = .025
#         self.text_entity = Text(
#             world_parent = self,
#             text = '  loading...',
#             origin = (0,1.5),
#             color = color.light_gray,
#             )
#         self.y = -.25
#
#         self.bg = Entity(parent=self, model='quad', scale_x=camera.aspect_ratio, color=color.black, z=1)
#         self.bg.scale *= 400
#
#         for key, value in kwargs.items():
#             setattr(self, key ,value)

    # def update(self):
    #     self.point.rotation_y += 5


if __name__ == '__main__':
    from ursina.prefabs.first_person_controller import FirstPersonController
    window.vsync = False
    window.title = "BarGame"
    # window.icon = ""
    app = Ursina()

    ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100,100), collider='box')
    bar = Entity(model='Comb_Bar.obj', scale=(0.01,0.01,0.01), texture='white_cube', mode='triangle', collider='box')
    # limit without optmz = 300 k vert / Not bad '-'
    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))

    from ursina.shaders import lit_with_shadows_shader
    for e in scene.entities:
        e.shader = lit_with_shadows_shader
        # 'Change Render Mode <gray>[F10]<default>': self.next_render_mode,
        # 'Reset Render Mode <gray>[Shift+F10]<default>': Func(setattr, self, 'render_mode', 'default'),
        # 'Reload Models <gray>[F7]<default>': application.hot_reloader.reload_models,
        # 'Reload Code <gray>[F5]<default>': application.hot_reloader.reload_code,

    player = FirstPersonController(y=2, origin_y=-.5)
    player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

    editor_camera = EditorCamera(enabled=False, ignore_paused=True)
    camera.orthographic = False
    camera.fov = 100
    cursor =  Cursor(model=Mesh(vertices=[(-.5,0,0),(.5,0,0),(0,-.5,0),(0,.5,0)], triangles=[(0,1),(2,3)], mode='line', thickness=2), scale=.02)
    mouse.visible = False

    def pause_input(key):
        if key == 'tab':  # press tab to toggle edit/play mode
            editor_camera.enabled = not editor_camera.enabled

            player.visible_self = editor_camera.enabled
            player.cursor.enabled = not editor_camera.enabled
            mouse.locked = not editor_camera.enabled
            editor_camera.position = player.position

            application.paused = editor_camera.enabled

    pause_handler = Entity(ignore_paused=True, input=pause_input)

    # FPS
    # _________________________________________________________________
    # player.gun = None

    # gun = Button(parent=scene, model='cube', color=color.blue, origin_y=-.5, position=(3,0,3), collider='box')
    # gun.on_click = Sequence(Func(setattr, gun, 'parent', camera), Func(setattr, player, 'gun', gun))
    # gun_2 = duplicate(gun, z=7, x=8)

    # hookshot_target = Button(parent=scene, model='cube', color=color.brown, position=(4,5,5))
    # hookshot_target.on_click = Func(player.animate_position, hookshot_target.position, duration=.5, curve=curve.linear)
    # def input(key):
    #     if key == 'left mouse down' and player.gun:
    #         gun.blink(color.orange)
    #         bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
    #         bullet.world_parent = scene
    #         bullet.animate_position(bullet.position+(bullet.forward*50), curve=curve.linear, duration=1)
    #         destroy(bullet, delay=1)

    # LOADING SCREEN
    # _________________________________________________________________
    # window.color = color.white
    # loading_screen = LoadingWheel(enabled=False)
    # from ursina.prefabs.health_bar import HealthBar

    # def load_textures():
    #     global loading_screen
    #
    #     textures_to_load = ['brick', 'white_cube'] * 1000
    #     bar = HealthBar(max_value=len(textures_to_load), value=0, position=(-0.25,-0.34,0))
    #     for i, t in enumerate(textures_to_load):
    #         load_texture(t)
    #         print(i)
    #         bar.value = i+1
    #         print('loaded textures')
    #     destroy(bar, delay=.01)
    #     loading_screen.enabled = True
    #
    #     if key == 'enter':
    #             loading_screen.enabled = False
    #             load_textures()

    # player.add_script(NoclipMode())
    app.run()

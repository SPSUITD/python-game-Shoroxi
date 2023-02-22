import ursina
from ursina import window, camera, mouse, Entity, Vec2, Vec3, color

import UrsinaLighting as Ul

from menu import MainMenu
from player import Player

if __name__ == '__main__':

    # TODO: make settings file
    window.title = "BarGame"
    # window.icon = ""

    window.fps_counter = True
    window.cog_button = True
    window.always_on_top = False
    window.vsync = False
    window.borderless = True

    app = ursina.Ursina(development_mode=True)
    # False -> Fullscreen

    # MODELS
    # cube = Ul.LitObject(model="cube", position=(0, 0.5, 1))
    land = Ul.LitObject(model='land.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', collider="mesh", normalMap = None, specularMap = None)
    land2 = Ul.LitObject(model='land2.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', collider=None, normalMap = None, specularMap = None)
    Pirate = Ul.LitObject(model='Pirate.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', collider=None, normalMap=None, specularMap=None)
    Welck = Ul.LitObject(model='Welck.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', collider=None, normalMap=None, specularMap=None)
    GOLD = Ul.LitObject(model='GOLD.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', collider=None, normalMap=None, specularMap=None)
    Cloud = Ul.LitObject(model='Cloud.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', color=(255,255,255,200), collider=None, normalMap=None, specularMap=None)
    Water = Ul.LitObject(model='Water.obj', scale=(0.01, 0.01, 0.01), position=(0, 0, 0), texture='white_cube', mode='triangle', color=(255,255,255,200), collider=None, normalMap=None, specularMap=None)

    e = Ul.LitObject(model=ursina.Terrain('loddefjord_height_map', skip=8), texture='loddefjord_color', scale=100, scale_y=30, normalMap=None, specularMap=None)
    e.model.save('loddefjord_terrain')

    # GRAPHIC
    # lit = Ul.LitInit()
    # sun = Ul.LitDirectionalLight(direction=Vec3(0), color=Vec3(1), intensity=1, shadows=True)
    sky = ursina.Sky()
    sun = Ul.LitDirectionalLight(direction=Vec3(0.5, -0.6, 1), intensity=0, color=color.gray)
    ursina.camera.clip_plane_far = 3000
    ursina.camera.clip_plane_near = 5

    from ursina.shaders import basic_lighting_shader
    # from ursina.shaders.screenspace_shaders.ssao import ssao_shader
    # camera.shader = ssao_shader

    ursina.scene.fog_color = color.gray
    ursina.scene.fog_density = 0.1

    # lit_with_shadows_shader basic_lighting_shader
    for e in ursina.scene.entities:
        e.shader = basic_lighting_shader
    # 'Change Render Mode <gray>[F10]<default>': self.next_render_mode,
    # 'Reset Render Mode <gray>[Shift+F10]<default>': Func(setattr, self, 'render_mode', 'default'),
    # 'Reload Models <gray>[F7]<default>': application.hot_reloader.reload_models,
    # 'Reload Code <gray>[F5]<default>': application.hot_reloader.reload_code,

    # CAMERA, MOUSE
    camera.orthographic = False
    camera.fov = 100

    # MOUSE
    mouse_sensitivity = Vec2(50,50)
    mouse.locked = True
    mouse.visible = False

    # CAMERA


    player = Player()
    # def update(self):
    #     player.update()
    #
    #     ursina.Animation()
    #     pass
    # Realization interact with E
    hookshot_target = ursina.Button(parent=ursina.scene, model='cube', color=color.brown, position=Vec3(4,5,5))

    ec = ursina.EditorCamera(enabled=False, ignore_paused=True)

    def pause_input(key):
        if key == 'tab':    # press tab to toggle edit/play mode
            ec.enabled = not ec.enabled
            # player.visible_self = ec.enabled
            ec.position = player.position
            ursina.application.paused = ec.enabled
        elif key == "escape":
            ursina.application.quit()
        elif hookshot_target.on_mouse_enter and key == 'e':
            hookshot_target.animate_position(value=player.position, duration=1, curve=ursina.curve.linear)

            # ursina.destroy(hookshot_target, delay=1)

    pause_handler = Entity(ignore_paused=True, input=pause_input)

if __name__ == '__main__':
    lit = Ul.LitInit()
    # LOADING SCREEN
    # _________________________________________________________________
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


    menu = MainMenu(player)

    app.run()

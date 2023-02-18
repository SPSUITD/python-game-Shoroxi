import ursina
from ursina import window, camera, mouse, Entity, Vec2, Vec3, color

import UrsinaLighting as Ul

from menu import MainMenu
from player import Player

if __name__ == '__main__':

    # TODO: make settings file
    window.title = "BarGame"
    # window.icon = ""

    window.fps_counter = False
    window.cog_button = True
    window.always_on_top = False
    window.vsync = False
    window.borderless = True

    app = ursina.Ursina(development_mode=False)
    # False -> Fullscreen

    # MODELS
    ground = Ul.LitObject(model='plane', position=(0, -0.2, 0), scale=(100, 1, 100), color=color.yellow.tint(-.2), texture='white_cube', texture_scale=(100, 100), collider='box')
    # bar = Entity(model='Comb_Bar.obj', scale=(0.01,0.01,0.01), texture='white_cube', mode='triangle', collider='box', ambientStrength=1)
    cube = Ul.LitObject(model="cube", position=(0, 0.5, 1))

    e = Ul.LitObject(model=ursina.Terrain('loddefjord_height_map', skip=8), texture='loddefjord_color', scale=100, scale_y=30)
    e.model.save('loddefjord_terrain')

    # GRAPHIC
    lit = Ul.LitInit()
    sun = Ul.LitDirectionalLight(direction=Vec3(0), color=Vec3(1), intensity=1, shadows=True)
    ursina.camera.clip_plane_far = 500
    ursina.camera.clip_plane_near = 5

    from ursina.shaders import basic_lighting_shader
    from ursina.shaders.screenspace_shaders.ssao import ssao_shader
    camera.shader = ssao_shader

    ursina.scene.fog_color = color.gray
    ursina.scene.fog_density = 0.5

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
    ec = ursina.EditorCamera(enabled=False, ignore_paused=True)

    # Realization interact with E
    hookshot_target = ursina.Button(parent=ursina.scene, model='cube', color=color.brown, position=(4,5,5))
    hookshot_target.on_click = ursina.Func(hookshot_target.animate_position, Player.position, duration=.5, curve=ursina.curve.linear)

    def pause_input(key):
        if key == 'tab':    # press tab to toggle edit/play mode
            ec.enabled = not ec.enabled
            # player.visible_self = ec.enabled
            ec.position = player.position
            ursina.application.paused = ec.enabled
        elif key == "escape":
            ursina.application.quit()
        elif key == 'e':
            ursina.destroy(hookshot_target, delay=1)

    pause_handler = Entity(ignore_paused=True, input=pause_input)

if __name__ == '__main__':

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

    player = Player(ursina.Vec3(0, 1, 0))
    menu = MainMenu(player)

    app.run()

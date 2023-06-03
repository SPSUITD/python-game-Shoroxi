import os.path

from direct.actor.Actor import Actor
from ursina.shaders import *

import UrsinaLighting as ulight
import main
import my_json
import setting
import ui
import pprint

from inventory_system import Inventory

# то панда то урсина полное фуфло, а не свет делают.
from PandaLighting import *

anim_folder = "assets/animations/"
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

player_creature = my_json.read("assets/player")
options_file = my_json.read("assets/options")
# -----------
gameplay = True
game_session = None
pause = True


# menu = False
# hiss = Audio(sound_folder + "spider_hiss", volume=5, autoplay=False, loop=False)

def check_itm(itm):
    if game_session.player.inventory.has_item(itm):
        return True
    else:
        pass


def add_itm(itm):
    game_session.player.inventory.add_item(itm)


def del_item(item_id):
    game_session.player.inventory.del_item(item_id)


def get_player():
    if game_session:
        if game_session.player is not None:
            return game_session.player
    else:
        return None


def get_enemy():
    if game_session:
        if game_session.enemy is not None:
            return game_session.enemy
    else:
        return None


def get_trigger(id):
    for trigger in game_session.current_level.level_objects:
        if trigger.name == "trigger":
            if trigger.trigger_id == id:
                return trigger


def set_current_status(trigger):
    if game_session:
        if game_session.player is not None:
            game_session.player.trigger_status = trigger


def get_current_status():
    if game_session:
        if game_session.player is not None:
            return game_session.player.trigger_status
    else:
        return None


# получить класс текущего уровня, на котором мы сейчас находимся
def get_current_level():
    if game_session:
        return game_session.current_level
    else:
        return None


# запустить новый уровень по id из папки levels
def set_current_level(lvl):
    if game_session:
        game_session.current_level = Level(get_player(), level_id=lvl)


# def show_message(txt, life_time=5):
#     get_player().msg.setText("")
#     get_player().msg.setText(txt)
#     invoke(get_player().msg.setText, "", delay=life_time)

def set_player_to_level_spawn_point():
    get_player().position = get_current_level().spawn_point["position"]


class Player(Entity):

    def __init__(self, **kwargs):
        super().__init__(
            model="cube",
            visible_self=False,
            scale=(25, 25, 25),
            render_queue=0
        )
        # ------------ Camera 1 ---------------
        self.camera_pivot = Entity(parent=self, y=1)
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.parent = self.camera_pivot
        camera.fov = 105
        self.original_fov = camera.fov
        camera.clip_plane_near = 0.06
        camera.clip_plane_far = 500
        self.direction = Vec3(camera.forward)
        # ------------ Camera 2 ---------------
        # self.camHolder = Entity(position=camera.position)
        # self.camStartPos = camera.position
        # self.amplitude = .0058
        # self.frequency = 10
        # self.timer = 0
        # ------------ Player ---------------
        self.speed = 40
        self.height = 165
        self.gravity = 7
        self.grounded = False
        self.jump_height = 14
        self.jump_up_duration = .7
        self.fall_after = .3
        self.jumping = False
        self.air_time = 0
        # ------------  ---------------
        self.inventory = Inventory()
        self.pause_menu = ui.GamePause(enabled=False)
        # ------------ Ray ---------------
        # self.hit_text = "None"
        self.ray_hit = raycast(self.position + (0, 20, 0), self.direction, ignore=(self,),
                               distance=100, debug=False)
        # ------------ Ui ---------------
        self.press_e = ui.UIText("press [E]", parent=camera.ui, offset=(0.0018, 0.0018), y=-0.35,
                                 enabled=False, color=color.white, origin=(0, 0))
        self.fps_counter = ui.UIText("", (0.0018, 0.0018), color=setting.color_orange,
                                     position=(window.right.x - 0.13, window.top.y - .1))
        self.cursor = Entity(model="quad", parent=camera.ui, scale=.005, color=color.white)
        self.crosshair_tip_text = ""
        self.crosshair_tip = ui.UIText(parent=camera.ui, offset=(0.0015, 0.0015), text=self.crosshair_tip_text,
                                       origin=(0, 0), y=0.04,
                                       color=color.white, scale=1, x=0, z=-0.001)
        self.msg = ui.UIText("", origin=(-.5, 0), offset=(0.0015, 0.0015), parent=camera.ui,
                             position=(window.left.x + 0.02, 0), color=color.orange)
        self.gameover_screen = ui.GameOverScreen(enabled=False)
        # ------------ Status ---------------
        self.trigger_status = ""
        # ------------ Mouse ---------------
        mouse.locked = setting.cursor_lock
        self.mouse_sensitivity = Vec2(options_file["mouse_sensitivity"], options_file["mouse_sensitivity"])
        self.mouse_control = True
        # ------------ Mouse ---------------
        # self.flashlight = SpotLight(parent=camera, position=(0, 0, 0.5))
        # self.torch = Entity(model='cube', color=color.orange, scale=(0.1, 0.1, 0.3), position=(0, 0, 0.5))
        # ------------ Trigger ---------------
        # ------------ DEV ---------------
        # if setting.developer_mode:
        #     self.debug_info_window = Entity(parent=camera.ui, model=Quad(radius=.03), color=color.rgba(10, 10, 10, 200),
        #                                     origin=(-.5, .5),
        #                                     position=Vec2(window.top_left.x + 0.02, window.top_left.y - 0.09),
        #                                     scale=Vec2(0.3, 0.35))
        #     self.debug_text = Text(parent=camera.ui, text="null", color=setting.color_orange, origin=(-.5, .5),
        #                            position=(window.top_left.x + 0.03, window.top_left.y - 0.095, -0.003))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def load_location(self):
        camera.overlay.color = color.black
        loading = Text("loading", origin=(0, 0), color=setting.color_orange, always_on_top=True)

        set_player_to_level_spawn_point()
        self.set_crosshair()
        self.raycast_once()
        destroy(loading)
        invoke(setattr, camera.overlay, 'color', color.clear, delay=1)

    def raycast_once(self):
        self.ray_hit = raycast(self.position + (0, 20, 0), self.direction, ignore=(self,), distance=100, debug=False)

    def get_player_pos(self):
        return self.position

    def set_crosshair(self):
        self.press_e.enable()

    # ------------- Gravity --------------
    def jump(self):
        if not self.grounded:
            return
        self.grounded = False
        self.animate_y(self.y + self.jump_height, self.jump_up_duration, resolution=int(1 // time.dt),
                       curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)

    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        self.air_time = 0
        self.grounded = True

    def input(self, keypress):
        global gameplay
        global pause

        if not pause:
            if keypress == 'space':
                self.jump()
            # if keypress == 'w':
            #     # steps_sound = s_sys.create_sound(sound_folder + "walk.opus")
            #     # s_sys.play_sound(steps_sound)
            #     pass
            #
            # if keypress == 'p':
            #     pos = self.get_player_pos()
            #     print(pos)
            #     # steps_sound = s_sys.create_sound(sound_folder + "walk.opus")
            #     # s_sys.play_sound(steps_sound)
            #     pass
            # # TODO: step sound
            # # if not (key == 'w') and self.steps_sound.get_state() == AL_PLAYING:
            # #     oalQuit()
            #
            # # TODO: flashlight
            # # if keypress == 'f':
            # #     self.flashlight.enabled = not self.flashlight.enabled
            # #     self.torch.enabled = not self.torch.enabled
            #
            # # TODO: Head Bobbing
            # # if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
            # #     pos = Vec3(0, 0, 0)
            # #     pos.y += math.sin(self.timer * self.frequency) * self.amplitude / 1.5
            # #     pos.x += math.cos(self.timer * self.frequency * 0.5) * self.amplitude / 1.7
            # #     camera.position += pos
            # #     pos = Vec3(camera.position.x, camera.position.y + self.camHolder.y, camera.position.z)
            # #     pos += self.camHolder.forward * 15
            # #     camera.look_at(pos)
            # #
            # #     if not camera.position == self.camStartPos:
            # #         camera.position = Vec3(lerp(camera.position, self.camStartPos, time.dt))
            if self.ray_hit.hit:
                def getHitData():
                    return self.ray_hit.entity

                if getHitData() and getHitData().id is not None:
                    if getHitData().keys["type"] == "loot":
                        if keypress == "e" and game_session:
                            invoke(self.raycast_once, delay=.01)
                            if getHitData().id == "light":
                                if not check_itm("light"):
                                    light_off = False
                                    add_itm("light")
                                elif check_itm("light"):
                                    light_off = True
                                    del_item("light")
                                for i in game_session.current_level.level_objects:
                                    if i.name == "point_light":
                                        i.color_off(light_off)
                            else:
                                add_itm(getHitData().id)
                                destroy(getHitData())
                            self.crosshair_tip_text = ""
            if keypress == "escape":
                pause = True
                invoke(self.pause_menu.enable, delay=0.001)
                # pause = True
                # ui.GameOverScreen()

    # ФУНКЦИЯ ОБНОВЛЕНИЯ ДЛЯ КАЖДОГО КАДРА
    def update(self):

        if not pause:
            if options_file["show_fps"]:
                self.fps_counter.setText("FPS: {0}".format(window.fps_counter.text))

            def setCrosshairTip(tip_text):
                self.crosshair_tip_text = tip_text
                # self.press_e.enabled = True

            def clearCrosshairText():
                self.crosshair_tip_text = ""
                self.press_e.enabled = False

            def getHitData():
                if self.ray_hit.hit:
                    return self.ray_hit.entity

            # ------------ DEV ---------------
            # if setting.developer_mode:
            #     # if getHitData():
            #     #     self.hit_text2 = getHitData().keys["type"] if getHitData().keys["type"] else "None"
            #     #     self.hit_text = getHitData().id if getHitData().id else "None"
            #         self.debug_text.text = "POS X: " + str(round(self.x, 2)) + \
            #                                "\nPOS Y: " + str(round(self.y, 2)) + \
            #                                "\nPOS Z: " + str(round(self.z, 2)) + \
            #                                "\n\nROT X: " + str(round(self.camera_pivot.rotation.x, 2)) + \
            #                                "\nROT Y: " + str(round(self.rotation.y, 2)) + \
            #                                "\nROT Z: " + str(round(self.camera_pivot.rotation.z, 2)) + \
            #                                "\n\nVEL X: " + str(round(mouse.velocity[0], 2)) + \
            #                                "\nVEL Y: " + str(round(mouse.velocity[1], 2))
            #                                # "\n\nHIT: " + str(self.hit_text) + \
            #                                # "\n\nHIT: " + str(self.hit_text2)

            # РЭЙКАСТИНГ, ВЗАИМОДЕЙСТВИЕ С МИРОМ
            if self.ray_hit.hit:
                if getHitData().keys["type"] == "loot":
                    # TODO: name key for id items
                    self.set_crosshair()
                    if getHitData().id == "tovar":
                        setCrosshairTip("Проверить товар")
                    if getHitData().id == "pistol":
                        setCrosshairTip("Пистолет")
                    if getHitData().id == "light":
                        setCrosshairTip("Включить")
                    if getHitData().id == "tv":
                        setCrosshairTip("Включить")
                    if getHitData().id == "trash_out":
                        setCrosshairTip("Выкинуть")
                    if getHitData().id == "trash_1":
                        setCrosshairTip("Прибрать")

                    if getHitData().id == "" or getHitData().id is None:
                        clearCrosshairText()
                else:
                    self.cursor.color = color.white
            else:
                clearCrosshairText()
            if self.mouse_control:
                # Interact
                self.direction = Vec3(camera.forward)
                self.ray_hit = raycast(self.position + (0, 24, 0), self.direction, ignore=(self,), distance=20,
                                       debug=False)
                # Camera
                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -60,
                                                     60) if not setting.developer_mode \
                    else clamp(self.camera_pivot.rotation_x, -90, 90)
                # Movement
                self.direction_move = Vec3(
                    self.forward * (held_keys['w'] - held_keys['s']) + self.right * (
                                held_keys['d'] - held_keys['a'])).normalized()
                # Collider
                feet_ray = raycast(self.position + Vec3(0, 3, 0), self.direction_move, ignore=(self,), distance=4,
                                   debug=False)
                head_ray = raycast(self.position + (0, 24, 0), self.direction_move, ignore=(self,), distance=4,
                                   debug=False)

                if not feet_ray.hit and not head_ray.hit:
                    move_amount = self.direction_move * time.dt * self.speed
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(1, 0, 0), distance=4, ignore=(self,)).hit:
                        move_amount[0] = min(move_amount[0], 0)
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(-1, 0, 0), distance=4, ignore=(self,)).hit:
                        move_amount[0] = max(move_amount[0], 0)
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(0, 0, 1), distance=4, ignore=(self,)).hit:
                        move_amount[2] = min(move_amount[2], 0)
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(0, 0, -1), distance=4, ignore=(self,)).hit:
                        move_amount[2] = max(move_amount[2], 0)
                    self.position += move_amount
                self.crosshair_tip.setText(self.crosshair_tip_text)
            if self.gravity:
                ray = raycast(self.world_position + (0, self.height, 0), self.down, ignore=(self,))
                if ray.distance <= self.height + .1:
                    if not self.grounded:
                        self.land()
                    self.grounded = True
                    # make sure it's not a wall and that the point is not too far up
                    if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5:  # walk up slope
                        self.y = ray.world_point[1]
                    return
                else:
                    self.grounded = False

                self.y -= min(self.air_time, ray.distance - .05) * time.dt * 100
                self.air_time += time.dt * .25 * self.gravity


class Enemy(Entity):

    def __init__(self, **kwargs):
        super().__init__(
            position=(50, -30, -60),
            rotation=Vec3(0, 90, 0),
            scale=14
        )
        self.actor = Actor(anim_folder + "goblin.gltf")
        self.actor.reparent_to(self)

        for key, value in kwargs.items():
            setattr(self, key, value)
        # other logics
        # ray-cast
        # memory
        # path-searcher


class Trigger(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.trigger_id = None
        self.trigger_targets = (self,)
        self.radius = None
        self.scale = self.radius
        self.color = color.rgba(10, 10, 10, 50)
        self.parent = None
        self.triggerers = []
        self.update_rate = 5
        self._i = 0
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_trigger_id(self):
        return self.trigger_id

    def update(self):
        global pause
        self._i += 1
        if self._i < self.update_rate:
            return
        self._i = 0

        # ------------ END ---------------
        if get_current_status() == "enemy":
            get_player().gameover_screen.enabled = True

            pause = True
            # game_session.video_player = Entity(model='quad', parent=camera.ui, scale=(1.5, 1), texture='video.mp4')
            # game_session.video_sound = loader.loadSfx('video.mp4')
            # game_session.video_player.texture.synchronizeTo(game_session.video_sound)
            # game_session.video_sound.play()
            # if check_itm("pistol"):
            #     video_player.play()
            # else:
            #     get_player().gameover_screen.enabled = True

        if get_current_status() == "stash":
            if check_itm("trash_out") and check_itm("tv"):
                if check_itm("tovar"):
                    # отрубить звук тв
                    get_player().msg.setText("Проверьте окно")
                    # пугающий звук у окна, упавший товар
                    # hiss.play()
                    # закрыть выход
                    # Entity()

        if get_current_status() == "window":
            if check_itm("tovar") and not check_itm("pistol"):
                add_itm("pistol")
                get_player().msg.setText("Проверьте кто это был (Представьте что вы взяли пистолет из под прилавка)")

        for other in self.trigger_targets:
            if other == self:
                continue
            dist = distance(other, self)
            if other not in self.triggerers and dist <= self.radius:
                print("Вошел в триггер: " + self.get_trigger_id())
                self.triggerers.append(other)
                set_current_status(self.get_trigger_id())

                # ------------ END ---------------
                if get_current_status() == "door_enter":
                    if check_itm("pistol"):
                        get_trigger("enemy").animate_position(value=(-40, -44, 168), duration=0.5, curve=curve.linear)
                        get_enemy().actor.play("jump")
                    if not check_itm("light"):
                        get_player().msg.setText("Включите свет")

                if get_current_status() == "cass":
                    if not check_itm("trash_1") and check_itm("light"):
                        get_player().msg.setText("Соберите и выбросите мусор")
                    elif check_itm("tv"):
                        get_player().msg.setText("Проверьте товар")
                    elif check_itm("pistol"):
                        get_player().msg.setText("Проверьте кто это был")

                if get_current_status() == "trash":
                    if check_itm("trash_1") and check_itm("trash_out"):
                        get_player().msg.setText("Включите телевизор")

                if get_current_status() == "tv":
                    if check_itm("trash_1") and check_itm("trash_out"):
                        if check_itm("tv"):
                            # врубить тв
                            get_player().msg.setText("Проверьте товар")

                # if get_current_status() == "window":
                #     # if self.check_itm("tovar"):
                #     get_player().msg.setText("Представьте что вы взяли пистолет из под прилавка - Проверьте кто это был")

            if other in self.triggerers and dist > self.radius:
                self.triggerers.remove(other)
                if hasattr(self, 'on_trigger_exit'):
                    self.on_trigger_exit()
                continue
            if other in self.triggerers and hasattr(self, 'on_trigger_stay'):
                self.on_trigger_stay()

# # TODO audio change volume by distance
# class Audio3d(Audio):
#     def __init__(self, sound_file_name, max_distance=10, **kwargs):
#         super().__init__(sound_file_name, autoplay=False, **kwargs)
#         self.max_distance = max_distance
#
#     def update(self):
#         self.balance = math.sin((self.world_position.xz - self.player.world_position.xz).normalized().signedAngleRad(self.player.forward.xz) / 2)
#         self.volume = 1 - min(distance(self.world_position, self.player.world_position) / self.max_distance, 1)
#         print(self.balance," | ",self.volume)
#
# # TODO anim
# class Anim(Entity):
#     def __init__(self, anim_id, **kwargs):
#         super().__init__(scale=17)
#         self.actor = Actor(anim_folder + anims_id + ".gltf")
#         self.actor.reparent_to(self)
#
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#
#     def get_anim_id(self):
#         return self.anim_id
#
#     def play_anim(self, anim):
#         self.actor.play(anim)
#
#     def isPlaying(self, anim):
#         myAnimControl = self.actor.getAnimControl(anim)
#         return myAnimControl.isPlaying()

# Главный класс игрового процесса

class Gameplay(Entity):
    def __init__(self, level=None, **kwargs):
        super().__init__()
        global gameplay
        global game_session
        global pause

        options = my_json.read("assets/options")
        window.fps_counter.enabled = options["show_fps"]
        window.fullscreen = options["fullscreen"]

        pause = False
        game_session = self
        self.player = Player()
        self.enemy = Enemy()

        # передаём ссылку с созданным гг в уровень для дальнейшего доступа к классу гг (получаем какой уовень на данный момент нужно запускать)
        invoke(self.player.load_location, delay=0.00001)
        self.current_level = Level(self.player, level_id=player_creature["start_level"] if level is None else level)

        set_player_to_level_spawn_point()
        gameplay = True
        self.player.msg.setText("Зайдите в свой магазин")

        Audio(sound_folder + "amb", volume=0.1, autoplay=False, loop=True).play()
        for key, value in kwargs.items():
            setattr(self, key, value)

# Класс уровня
class Level(Entity):
    def __init__(self, p, **kwargs):
        super().__init__()
        self.level_id = None
        self.level_objects = []
        self.player_data = p
        self.spawn_point = None
        for key, value in kwargs.items():
            setattr(self, key, value)

        if os.path.isdir("assets/levels/" + str(self.level_id)):
            level_data = my_json.read("assets/levels/" + str(self.level_id) + "/level")
            for obj in level_data["models"]:
                lvl_obj = LevelObject(
                    parent=self,
                    model=obj["model"] if "model" in obj else None,
                    position=obj["position"] if "position" in obj else (0, 0, 0),
                    scale=obj["scale"] if "scale" in obj else 1,
                    collider=obj["collider"] if "collider" in obj else None,
                    texture=obj["texture"] if "texture" in obj else None,
                    type=obj["type"] if "type" in obj else None,
                    color=color.rgba(obj["color"][0], obj["color"][1], obj["color"][2], obj["color"][3])
                    if "color" in obj else color.clear
                    if obj["type"] in obj and obj["type"] == "collider" or obj["type"] == "loot"
                       or obj["type"] == "trigger" else color.clear
                    if obj["type"] in obj and obj["type"] == "loot" else color.white,
                    id=obj["id"] if "id" in obj else None)
                # звук от предмета
                # if "sound" in obj and obj["sound"]:
                #     a = Audio3d()
                #     attach_to(lvl_obj)
                #
                # if "animation" in obj and obj["animation"]:
                #     a = Anim()
                #     attach_to(lvl_obj)
                if "type" in obj:
                    if obj["type"] == "spawn_point":
                        get_player().position = obj["position"]
                        self.spawn_point = obj
                if "shader" in obj:
                    lvl_obj.shader = lit_with_shadows_shader
                    lvl_obj.setShaderAuto()
                scene.fog_density = 0.01
                scene.fog_color = color.rgb(level_data["weather_color"][0],
                                            level_data["weather_color"][1],
                                            level_data["weather_color"][2])
                # sunsetSky = load_texture(tex_folder+'sunset.jpg')
                # Sky(texture=sunsetSky)
                lvl_obj.keys = obj
                lvl_obj.setShaderAuto()
                self.level_objects.append(lvl_obj)

            # for sounds in level_data["sound"]:
            #     if sounds["type"] == "amb":
            #         ambient = (sound_folder + "amb.opus")
            #         # Source.set_gain(value)
            #         # Source.set_max_distance(value)
            #         # Source.set_position([0, 0, 0])
            #         # Source.set_looping(value)
            #         # print("AMB: {0}".format(ambient.position))
            #         pass
            #     elif sounds["type"] == "loop":
            #         source = (sound_folder + "fan.opus")
            #         pass

            for trigger in level_data["trigger"]:
                t = Trigger(parent=trigger["parent"] if "parent" in trigger else self,
                            trigger_targets=(self.player_data,),
                            model=trigger["model"],
                            position=trigger["position"] if "position" in trigger else [0, 0, 0],
                            color=color.rgba(10, 10, 10, 0),
                            radius=trigger["radius"],
                            scale=trigger["radius"],
                            trigger_id=trigger["id"],
                            id=trigger["id"] if "id" in trigger else None)

                if "id" in trigger:
                    if trigger["id"] == "enemy":
                        get_enemy().reparent_to(t)
                t.keys = trigger
                self.level_objects.append(t)
            for light in level_data["light"]:
                if light["type"] == "point":
                    l = PointLight(parent=self,
                                   color=color.rgb(light["color"][0], light["color"][1],
                                                   light["color"][2]),
                                   position=light["position"],
                                   rotation=light["rotation"],
                                   distance=light["distance"])
                    l.keys = light
                    self.level_objects.append(l)
                elif light["type"] == "direction":
                    l = PointLight(parent=self,
                                   color=color.rgb(light["color"][0], light["color"][1],
                                                   light["color"][2]),
                                   position=light["position"],
                                   rotation=light["rotation"],
                                   distance=light["distance"],
                                   attenuation=(light["attenuation"][0], light["attenuation"][1],
                                                light["attenuation"][2]) if "attenuation" in light else (1, 0, 2))
                    l.keys = light
                    self.level_objects.append(l)
                elif light["type"] == "spot":
                    l = SpotLight(parent=self,
                                  color=color.rgba(light["color"][0], light["color"][1], light["color"][2]),
                                  position=light["position"],
                                  rotation=light["rotation"],
                                  distance=light["distance"])
                    l.keys = light
                    self.level_objects.append(l)
                elif light["type"] == "ambient":
                    l = ulight.AmbientLight(parent=self,
                                            color=color.rgb(light["color"][0], light["color"][1], light["color"][2]))
                    l.keys = light
                    self.level_objects.append(l)

class LevelObject(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        # ключ идентификатор
        # self.id = None
        # self.name = None
        # словарь ключей из файла с уровнем "ключ": значение
        self.keys = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

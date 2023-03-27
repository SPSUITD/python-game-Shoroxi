from ursina.shaders import *
import callbacks
import ui
import setting
import os.path
import my_json
from panda_light import *
# import pyfmodex

import time

tex_folder = "assets/textures/"
mesh_folder = "assets/models/"
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

player_creature = my_json.read("assets/player")
options_file = my_json.read("assets/options")
# -----------
gameplay = True
game_session = None
pause = True

# s_sys = pyfmodex.System()
# s_sys.init()
#
# sound = s_sys.create_sound("somefile.mp3")
# channel = sound.play()

def get_player():
    if game_session:
        if game_session.player is not None:
            return game_session.player
    else:
        return None

def get_loot():
    if game_session:
        if game_session.player is not None:
            return game_session.player
    else:
        return None

# получить текстовый идентификатор уровня
def get_current_level_id():
    if game_session:
        return game_session.get_level()
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

def show_message(txt, life_time=5):
    get_player().msg.setText("")
    get_player().msg.setText(txt)
    invoke(get_player().msg.setText, "", delay=life_time)

def set_player_to_level_spawn_point():
    get_player().position = get_current_level().spawn_point["position"]

class Player(Entity):
    def hideHUD(self):
        return color.rgba(1,1,1,0) if not setting.show_hud else color.rgba(1,1,1,1)

    def __init__(self, **kwargs):
        super().__init__(
            model="cube",
            visible_self=False,
            scale=(25,25,25)
        )
        self.speed = 40
        self.camera_pivot = Entity(parent=self, y=1)
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 105
        self.original_fov = camera.fov
        camera.clip_plane_near = 0.06
        camera.clip_plane_far = 500
        mouse.locked = setting.cursor_lock
        # ---------------------------
        self.height = 165
        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35
        self.jumping = False
        self.air_time = 0
        # ---------------------------
        # from shaders.camera_shader import ouline_shader
        # camera.shader = ouline_shader
        # camera.set_shader_input("blur_size", 0.04)
        # print(window.getConfigProperties())
        # ---------------------------
        # self.listener_pos = s_sys.listener(0).position(self.get_player_pos())
        # self.listener_vel = s_sys.listener(0).velocity(self.get_player_vel())
        # ---------------------------
        self.mouse_sensitivity = Vec2(options_file["mouse_sensitivity"], options_file["mouse_sensitivity"])
        # ---------------------------
        self.ray_hit = raycast(self.position + (self.down * 0.04), direction=(0, -1, 0), ignore=(self,), distance=50, debug=False)
        # ---------------------------
        self.press_f = ui.UIText("press [F]", parent=camera.ui,offset=(0.0018,0.0018), y=-0.35, enabled=False, color=color.white,origin=(0,0))
        self.fps_counter = ui.UIText("", (0.0018, 0.0018), color=setting.color_orange, position=(window.right.x - 0.13, window.top.y - .1))
        # ---------------------------
        self.rotation_range_y = [-180,180]
        self.mouse_control = True
        self.panel_opened = False

        # TODO: Enable menu
        # if pause:
        #     self.pause_menu.enable()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def load_location(self,level):
        camera.overlay.color = color.black
        loading = Text("loading", origin=(0, 0), color=setting.color_orange, always_on_top=True)

        destroy(get_current_level())

        invoke(set_current_level,level,delay=2)
        self.set_crosshair()
        self.raycast_once()
        invoke(setattr, camera.overlay, 'color', color.clear, delay=2)
        destroy(loading, delay=2)

    def raycast_once(self):
        self.ray_hit = raycast(self.position + (self.down * 0.04), direction=Vec3(camera.forward), ignore=(self,),
                               distance=50,
                               debug=False)

    def set_player_pos(self,x,y,z):
        self.position = (x,y,z)

    def get_player_pos(self):
        return self.position

    def set_crosshair(self):
        self.press_f.enable()

    def jump(self):
        if not self.grounded:
            return
        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
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

            if keypress == 'w':
                # steps_sound = s_sys.create_sound(sound_folder + "walk.opus")
                # s_sys.play_sound(steps_sound)
                # TODO: add Fade
                # camera.shake(duration=1, magnitude=2, speed=.8, direction=(0, 1))

                pass
            # if not (key == 'w') and self.steps_sound.get_state() == AL_PLAYING:
            #     oalQuit()

            if self.ray_hit.hit:

                def getHitData():
                    return self.ray_hit.entity

                if getHitData() and getHitData().id is not None:
                    if getHitData().id == "loot":
                        if keypress == "f" and game_session:
                            invoke(self.raycast_once, delay=.05)
                            getHitData().animate_position(value=self.position, duration=1, curve=curve.linear)
                            destroy(getHitData(), delay=1)
                    if getHitData().id == "npc":
                        pass

            if keypress == "escape" and not self.dialogue.enabled:
                pass

    # ФУНКЦИЯ ОБНОВЛЕНИЯ ДЛЯ КАЖДОГО КАДРА
    def update(self):

        if not pause:

            if options_file["show_fps"]:
                self.fps_counter.setText("FPS: {0}".format(window.fps_counter.text))
            self.direction = Vec3(camera.forward)

            def setCrosshairTip(text):
                self.crosshair_tip_text = text
                self.press_f.enabled = True

            def clearCrosshairText():
                self.crosshair_tip_text = ""
                self.press_f.enabled = False

            def getHitData():
                if self.ray_hit.hit:
                    return self.ray_hit.entity

            # РЭЙКАСТИНГ, ВЗАИМОДЕЙСТВИЕ С МИРОМ
            if self.ray_hit.hit:
                if getHitData() is not None:

                    if getHitData().id == "transition" or getHitData().id == "transition_to_level":
                        setCrosshairTip("interact.go")

                    # TODO: name key for loot items
                    if getHitData().id == "loot":
                        setCrosshairTip("interact.loot")
                    # TODO: dialogue system
                    if getHitData().id == "" or getHitData().id is None:
                        clearCrosshairText()

                else:
                    self.cursor.color = color.white
            else:
                clearCrosshairText()
            # ---------------------------
            if self.mouse_control:

                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -30, 30) if not setting.developer_mode else clamp(self.camera_pivot.rotation_x, -90, 90)

                self.direction = Vec3(
                    self.forward * (held_keys['w'] - held_keys['s'])
                    + self.right * (held_keys['d'] - held_keys['a'])).normalized()

                feet_ray = raycast(self.position + Vec3(0, 0.5, 0), self.direction, ignore=(self,), distance=.5,
                                   debug=False)
                head_ray = raycast(self.position + Vec3(0, self.height - .1, 0), self.direction, ignore=(self,),
                                   distance=.5, debug=False)
                if not feet_ray.hit and not head_ray.hit:
                    move_amount = self.direction * time.dt * self.speed

                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(1, 0, 0), distance=.5, ignore=(self,)).hit:
                        move_amount[0] = min(move_amount[0], 0)
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(-1, 0, 0), distance=.5, ignore=(self,)).hit:
                        move_amount[0] = max(move_amount[0], 0)
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(0, 0, 1), distance=.5, ignore=(self,)).hit:
                        move_amount[2] = min(move_amount[2], 0)
                    if raycast(self.position + Vec3(-.0, 1, 0), Vec3(0, 0, -1), distance=.5, ignore=(self,)).hit:
                        move_amount[2] = max(move_amount[2], 0)
                    self.position += move_amount
            # ---------------------------
            if self.gravity:
                ray = raycast(self.world_position + (0, self.height, 0), self.down, ignore=(self,))
                # ray = boxcast(self.world_position+(0,2,0), self.down, ignore=(self,))

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
                # TODO: NEW FALL PHYSICS + Running
                # от этого управление будет чувствоваться живей
                # if not on ground and not on way up in jump, fall
                self.y -= min(self.air_time, ray.distance - .05) * time.dt * 100
                self.air_time += time.dt * .25 * self.gravity

class Trigger(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.trigger_id = None
        self.trigger_targets = (self,)
        self.radius = None
        self.triggerers = []
        self.update_rate = 40
        self._i = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_trigger_id(self):
        return self.trigger_id

    def get_radius(self):
        return self.radius

    def update(self):
        self._i += 1
        if self._i < self.update_rate:
            return
        self._i = 0
        for other in self.trigger_targets:
            if other == self:
                continue
            dist = distance(other, self)
            # TODO: radius
            if other not in self.triggerers and dist <= 10:
                print(self.get_trigger_id)
                self.triggerers.append(other)
                if hasattr(self, 'on_trigger_enter'):

                    # реализация события от id тригера - через другой файл с сюжетом
                    if self.get_trigger_id() == "test":
                        pass
                      # invoke(self.play_anim)
                      # invoke(self.add_quest)
                    self.on_trigger_enter()
                continue

            if other in self.triggerers and dist > self.radius:
                self.triggerers.remove(other)
                if hasattr(self, 'on_trigger_exit'):
                    self.on_trigger_exit()
                continue

            if other in self.triggerers and hasattr(self, 'on_trigger_stay'):
                # if self.trig.num and time==120:
                print("123")
                self.on_trigger_stay()


# Главный класс игрового процесса
class Gameplay(Entity):
    def __init__(self, level=None, **kwargs):
        super().__init__()
        global gameplay
        global game_session

        game_session = self
        self.player = Player()

        # передаём ссылку с созданным гг в уровень для дальнейшего доступа к классу гг
        invoke(self.player.load_location, player_creature["start_level"] if level is None else level,delay=0.00001)
        self.current_level = Level(self.player, level_id=player_creature["start_level"] if level is None else level)
        # self.current_quest = Story()
        gameplay = True
        # t.on_trigger_enter = Func(print, 'enter')
        # t.on_trigger_exit = Func(print, 'exit')
        # t.on_trigger_stay = Func(print, 'stay')
        for key, value in kwargs.items():
            setattr(self, key, value)



# Класс уровня
class Level(Entity):
    def __init__(self, p, **kwargs):
        super().__init__()
        self.level_id = None
        self.with_light = False
        self.level_objects = []

        self.player_data = p
        self.spawn_point = None

        for key, value in kwargs.items():
            setattr(self, key, value)
        # Если мы начали игру
        if os.path.isdir("assets/levels/" + str(self.level_id)):
            level_data = my_json.read("assets/levels/" + str(self.level_id) + "/level")
            window.color = color.rgb(level_data["weather_color"][0], level_data["weather_color"][1], level_data["weather_color"][2])

            # TODO: sound
            for sounds in level_data["sound"]:
                if sounds["type"] == "amb":
                    # ambient = (sound_folder + "amb.opus")
                    # # Source.set_gain(value)
                    # # Source.set_max_distance(value)
                    # # Source.set_position([0, 0, 0])
                    # # Source.set_looping(value)
                    # print("AMB: {0}".format(ambient.position))
                    pass

                elif sounds["type"] == "loop":
                    source = (sound_folder + "fan.opus")
                    pass

            # Создаём объекты из папки с уровнем из файла level
            for obj in level_data["level_data"]:
                if "light" in level_data:
                    for light in level_data["light"]:
                        # TODO: other types
                        if light["type"] == "point":
                            l = SpotLight(parent=self, shadows=light["shadows"],
                                       colour=color.rgba(light["color"][0],light["color"][1],light["color"][2],.1),
                                       position=light["position"],
                                       rotation=light["rotation"],
                                       distance=light["distance"])
                            l.keys = light
                            self.level_objects.append(l)
                            break

                if "trigger" in level_data:
                    for trigger in level_data["trigger"]:
                        if trigger["type"] == "trigger":
                            t = Trigger(parent=self, trigger_targets=(self.player_data,), model=trigger["model"],
                                    colour=color.rgba(0,0,0,255),
                                    position=trigger["position"],
                                    radius=trigger["radius"],
                                    trigger_id=trigger["name"])
                            t.keys = trigger
                            self.level_objects.append(t)
                            break

                # специфичные вещи
                if "id" in obj:

                    if obj["id"] == "spawn_point":
                        get_player().position = obj["position"]
                        self.spawn_point = obj

                    if obj["id"] == "animation":
                        Animation(tex_folder + obj["sequence"], position=obj["position"], rotation=obj["rotation"],
                                  scale=obj["scale"],parent=self)

                lvl_obj = LevelObject(parent=self, model=obj["model"],
                                      texture=obj["texture"] if "texture" in obj else None,
                                      # filtering=Texture.default_filtering,
                                      position=obj["position"] if "position" in obj else (0, 0, 0),
                                      rotation=obj["rotation"] if "rotation" in obj else (0,0,0),
                                      scale=obj["scale"] if "scale" in obj else 1,
                                      double_sided=obj["double_sided"] if "double_sided" in obj else False,
                                      color=color.rgba(obj["color"][0], obj["color"][1], obj["color"][2])
                                      if "color" in obj
                                      else color.white if "id" not in obj
                                      else color.clear if "invisible" in obj and obj["invisible"]
                                      else color.clear,
                                      id=obj["id"] if "id" in obj else None)

                # столкновения
                # if "trigger" in obj and obj["trigger"]:
                #     lvl_obj.trigger = obj["trigger"]

                if "collider" in obj and obj["collider"]:
                    lvl_obj.collider = obj["collider"]

                # звук от предмета
                # if "sound" in obj and obj["sound"]:
                #     lvl_obj.sound = obj["sound"]
                #     play music

                # название подбираемого предмета
                if "name" in obj and obj["name"]:
                    lvl_obj.name = obj["name"]
                    # show name

                if "shader" in obj and obj["shader"]:
                    lvl_obj.shader = lit_with_shadows_shader

                # заливка цветом (light - panda3d) / альфа канал не робит не знаю почему
                if "ambient" in obj:
                    _light = PandaAmbientLight('ambient_light')
                    for light in level_data["light"]:
                        if "id" in light and light["id"] == obj["ambient"]:
                            _light.setColor(color.rgba(light["color"][0],light["color"][1],light["color"][2],light["color"][3]))
                            break
                    lvl_obj.setLight(lvl_obj.attachNewNode(_light))

                scene.fog_density = 0.010
                scene.fog_color = color.rgb(level_data["weather_color"][0], level_data["weather_color"][1], level_data["weather_color"][2])

                # присваиваем ему все ключи из файла с уровнем
                lvl_obj.keys = obj
                lvl_obj.setShaderAuto()
                self.level_objects.append(lvl_obj)

    def update(self):
        pass

class LevelObject(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        # ключ идентификатор
        self.id = None
        # словарь ключей из файла с уровнем "ключ": значение
        self.keys = {}

        for key, value in kwargs.items():
            setattr(self, key, value)

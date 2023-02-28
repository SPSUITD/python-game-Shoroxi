from ursina import *
from ursina import curve
from panda3d.core import *
from ursina.shaders import *
import callbacks
import ui
import setting
import os.path
import my_json
import main_menu
import cmd

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
        )
        self.speed = setting.camera_move_speed
        self.camera_pivot = Entity(parent=self, y=1)
        # текст под прицелом
        self.crosshair_tip_text = "Demo"

        self.crosshair_tip = ui.UIText(parent=camera.ui, offset=(0.0015,0.0015), text=self.crosshair_tip_text, origin=(0, 0), y=0.04,
                                       color=setting.color_orange if setting.show_hud else self.hideHUD(), scale=1, x=0, z=-0.001)
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = setting.camera_fov
        self.original_fov = camera.fov
        camera.clip_plane_near = 0.06
        camera.clip_plane_far = 500

        mouse.locked = setting.cursor_lock
        # ---------------------------
        self.height = 2
        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35 # will interrupt jump up
        self.jumping = False
        self.air_time = 0
        # ---------------------------

        from Shaders.cam_shader import ouline_shader
        camera.shader = ouline_shader
        camera.set_shader_input("blur_size", 0.04)
        print(window.getConfigProperties())

        # ---------------------------
        # дебаг рейкаста (луча столкновения) в режиме разработчика
        self.hit_text = "None"
        self.raycast_point_pos_text = ""
        self.hit_pos_info = Text("", y=0.1, origin=(0, 0))
        # ---------------------------
        self.mouse_sensitivity = Vec2(options_file["mouse_sensitivity"], options_file["mouse_sensitivity"])
        self.rot_array_x = []
        self.rot_average_x = 0.0
        self.rot_array_y = []
        self.rot_average_y = 0.0
        self.rot_x = 0
        self.rot_y = 0
        self.frame_count = 2
        self.strange_mouse = False
        # ---------------------------
        self.steps_sound = Audio(sound_folder+"walk", pitch=random.uniform(.5,1), autoplay=False, loop=False)
        # autoplay - в меню будет тоже но зато без задержек
        self.amb_sound = Audio(sound_folder+"amb2", pitch=random.uniform(.5,1), autoplay=True, loop=True)

        self.ray_hit = raycast(self.position + (self.down * 0.04), direction=(0, -1, 0), ignore=(self,), distance=50,
                               debug=False)
        self.scope = None

        self.press_f = ui.UIText("press [F]", parent=camera.ui,offset=(0.0018,0.0018), y=-0.35, enabled=False,
                                 color=color.white,origin=(0,0))

        self.fps_counter = ui.UIText("", (0.0018, 0.0018), color=setting.color_orange,
                                     position=(window.right.x - 0.13, window.top.y - .1))
        # >> сообщение сбоку экрана
        self.msg = ui.UIText("", origin=(-.5, 0),offset=(0.0015, 0.0015), parent=camera.ui,
                             position=(window.left.x+0.02, 0),
                             color=setting.color_orange if setting.show_hud else self.hideHUD())

        # ------------------------------
        if setting.developer_mode:

            self.debug_info_window = Entity(parent=camera.ui, model=Quad(radius=.03), color=color.rgba(10, 10, 10, 200) if setting.show_hud else self.hideHUD(),
                                            origin=(-.5, .5),
                                            position=Vec2(window.top_left.x + 0.02, window.top_left.y - 0.09),
                                            scale=Vec2(0.3, 0.35))
            # Текст на фоне
            self.debug_text = Text(parent=camera.ui, text="null", color=setting.color_orange if setting.show_hud else self.hideHUD(), origin=(-.5, .5),
                                   position=(window.top_left.x + 0.03, window.top_left.y - 0.095, -0.003))

        # ДИАПАЗОН ПОВОРОТА ПО [Y]
        self.rotation_range_y = [-180,180]
        # ----------------
        self.transition_trigger = None
        self.mouse_control = True
        self.panel_opened = False

        # TODO: Enable menu
        # if pause:
        #     self.pause_menu.enable()

        for key, value in kwargs.items():
            setattr(self, key, value)

    # TODO: load next level
    def load_location(self,level):
        camera.overlay.color = color.black
        loading = Text("loading", origin=(0, 0), color=setting.color_orange, always_on_top=True)

        # destroy(get_current_level())

        invoke(set_current_level,level,delay=2)
        self.set_crosshair(True)
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

    def set_crosshair(self,b):
        if not b:
            self.crosshair_tip.disable()
            self.press_f.disable()
        else:
            self.crosshair_tip.enable()
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
        # print('land')
        self.air_time = 0
        self.grounded = True

    def input(self, key):
        global gameplay
        global pause

        if not pause:
            if key == 'space':
                self.jump()
            if key == 'w':
                # TODO: Fade in to shake
                # camera.shake(duration=1, magnitude=2, speed=.8, direction=(0, 1))
                self.steps_sound.play()
            if self.ray_hit.hit:

                def getHitData():
                    return self.ray_hit.entity

                if getHitData() and getHitData().id is not None:
                    # TODO del obj
                    if key == "f" and game_session:
                        invoke(self.raycast_once, delay=.05)
                        # типа подобрал предмет (в итоге тригер удаляется)
                        getHitData().animate_position(value=self.position, duration=1, curve=curve.linear)
                        destroy(getHitData(), delay=1)
                    if getHitData().id == "npc":
                        pass

            if key == "escape" and not self.dialogue.enabled:
                pass

    # ФУНКЦИЯ ОБНОВЛЕНЯ ДЛЯ КАЖДОГО КАДРА
    def update(self):
        if not pause:

            if options_file["show_fps"]:
                self.fps_counter.setText("FPS: {0}".format(window.fps_counter.text))
            self.direction = Vec3(camera.forward)

            # если мышь двигается
            # if self.mouse_control:
            #     if mouse.velocity > 0 or mouse.velocity < 0:
            #         self.ray_hit = raycast(self.position, self.direction, ignore=(self,), distance=50,
            #                                debug=setting.show_raycast_debug)
                    # self.hit_pos_info.text = self.raycast_point_pos_text

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

                    # if setting.developer_mode:
                    #     self.hit_text = getHitData() if getHitData() else "None"

                    if getHitData().id == "transition" or getHitData().id == "transition_to_level":
                        setCrosshairTip("interact.go")

                    # TODO: nk for loot items
                    if getHitData().id == "loot":
                        setCrosshairTip("interact.loot")

                    if getHitData().id == "" or getHitData().id is None:
                        clearCrosshairText()

                else:
                    self.cursor.color = color.white
            else:
                clearCrosshairText()

            if self.mouse_control:

                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -30, 30) if not setting.developer_mode else clamp(self.camera_pivot.rotation_x, -90, 90)

                if not self.scope:
                    self.crosshair_tip.setText(self.crosshair_tip_text)

                self.direction = Vec3(
                    self.forward * (held_keys['w'] - held_keys['s'])
                    + self.right * (held_keys['d'] - held_keys['a'])
                ).normalized()

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

                # if not on ground and not on way up in jump, fall
                self.y -= min(self.air_time, ray.distance - .05) * time.dt * 100
                self.air_time += time.dt * .25 * self.gravity

# Главный класс игрового процесса
class Gameplay(Entity):
    def __init__(self,level=None, **kwargs):
        super().__init__()
        # Глобальные переменные для изменения
        global gameplay
        global game_session

        game_session = self
        self.player = Player()

        # передаём ссылку с созданным гг в уровень для дальнейшего доступа к классу гг
        invoke(self.player.load_location, player_creature["start_level"] if level is None else level,delay=0.00001)
        self.current_level = Level(self.player, level_id=player_creature["start_level"] if level is None else level)
        # игровой процесс запущен
        gameplay = True
        # цикл проверки аргументов и изменение переменных
        for key, value in kwargs.items():
            setattr(self, key, value)

    # получить идентификатор текущего уровня
    def get_level(self):
        return self.current_level.level_id

# Класс уровня
class Level(Entity):
    def __init__(self, p, **kwargs):
        super().__init__()
        # текстовый идентификатор уровня
        self.level_id = None
        # ссылка на существующего гг
        self.player_data = p
        self.with_light = False
        self.level_objects = []
        self.spawn_point = None

        for key, value in kwargs.items():
            setattr(self, key, value)

        # Если мы начали игру
        if os.path.isdir("assets/levels/" + str(self.level_id)):
            level_data = my_json.read("assets/levels/" + str(self.level_id) + "/level")
            window.color = color.rgb(level_data["weather_color"][0], level_data["weather_color"][1],
                                     level_data["weather_color"][2])



            # Создаём объекты из папки с уровнем из файла level
            for obj in level_data["level_data"]:

                # если в объекте уровня есть ключ ID и его параметр spawn_point
                if "id" in obj:
                    # Присваиваем начальную позицию гг, равную позиции спавн точки
                    if obj["id"] == "spawn_point":
                        get_player().position = obj["position"]
                        self.spawn_point = obj

                    if obj["id"] == "animation":
                        Animation(tex_folder + obj["sequence"], position=obj["position"], rotation=obj["rotation"],
                                  scale=obj["scale"],parent=self)


                    if obj["id"] == "text":
                        Text(parent=scene, text=obj["string"], position=obj["position"],
                             rotation_y=get_player().rotation.y,
                             scale=obj["scale"])

                # Cоздаём объект
                lvl_obj = LevelObject(parent=self, model=obj["model"] if "model" in obj else "cube",
                                      texture=obj["texture"] if "texture" in obj else None,
                                      rotation=obj["rotation"] if "rotation" in obj else (0,0,0),
                                      position=obj["position"] if "position" in obj else (0,0,0),
                                      # filtering=Texture.default_filtering,
                                      scale=obj["scale"] if "scale" in obj else 1,
                                      double_sided=obj["double_sided"] if "double_sided" in obj else False,
                                      color=color.rgba(obj["color"][0],
                                                       obj["color"][1],
                                                       obj["color"][2],
                                                       obj["color"][3]) if "color" in obj and setting.developer_mode or "color" in obj and "id" in obj and setting.developer_mode else color.white if "id" not in obj else color.clear if "invisible" in obj and obj["invisible"] else color.clear,
                                      id=obj["id"] if "id" in obj else None)

                if "collider" in obj and obj["collider"]:
                    lvl_obj.collider = obj["collider"]

                if "name" in obj and obj["name"]:
                    lvl_obj.name = obj["name"]

                if "shader" in obj and obj["shader"]:
                    lvl_obj.shader = lit_with_shadows_shader

                if "ambient" in obj:
                    _light = PandaAmbientLight('ambient_light')
                    for l in level_data["light"]:
                        if "id" in l and l["id"] == obj["ambient"]:
                            _light.setColor(color.rgba(l["color"][0],l["color"][1],l["color"][2],1))
                            break

                    lvl_obj.setLight(lvl_obj.attachNewNode(_light))

                # scene.fog_density = 0.001
                # scene.fog_color = color.rgb(level_data["weather_color"][0], level_data["weather_color"][1],
                #                      level_data["weather_color"][2])

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

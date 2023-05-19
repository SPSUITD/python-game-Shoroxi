from ursina import *

app = Ursina()

video = 'video.mp4'
video_player = Entity(model='quad', parent=camera.ui, scale=(1.5, 1), texture=video)
video_sound = loader.loadSfx(video)
video_player.texture.synchronizeTo(video_sound)
video_sound.play()

app.run()
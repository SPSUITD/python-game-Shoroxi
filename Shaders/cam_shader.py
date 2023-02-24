from ursina import *
from ursina import Shader

pixel = Shader(
fragment='''
#version 150
uniform sampler2D tex;
uniform float blur_size;
in vec2 window_size;
in vec2 uv;
out vec4 color;
void main() {
    float Pixels = 1600.0;
    float dx = 9.0 * (1.0 / Pixels);
    float dy = 16.0 * (1.0 / Pixels);
    vec2 new_uv = vec2(dx * floor(uv.x / dx), dy * floor(uv.y / dy));
    color = texture(tex, new_uv).rgba;
    vec4 col = vec4(0.);
    for(float index=0; index<10; index++) {
        vec2 offset_uv = uv + vec2(0, (index/9 - 0.5) * blur_size);
        col += texture(tex, offset_uv);
    }
        col = col / 10;
    col = 1-((1-color)*(1-col));
    color = mix(color, vec4(col.rgb, 1), blur_size*10);
}
''')

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

ouline_shader = Shader(
vertex='''
#version 130
// Exactly nothing happens in vertex shading.
in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
void main()  {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
''',
fragment='''
#version 130
uniform sampler2D tex;
uniform sampler2D dtex;
out vec4 color;
void main () {
  vec4 color_base = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(0, 0), 0);
  vec4 color_1 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(-1, -1), 0);
  vec4 color_2 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(-1,  0), 0);
  vec4 color_3 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(-1,  1), 0);
  vec4 color_4 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 0, -1), 0);
  vec4 color_5 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 0,  1), 0);
  vec4 color_6 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 1, -1), 0);
  vec4 color_7 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 1,  0), 0);
  vec4 color_8 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 1,  1), 0);
  color = (abs(color_base - color_1) +
           abs(color_base - color_2) +
           abs(color_base - color_3) +
           abs(color_base - color_4) +
           abs(color_base - color_5) +
           abs(color_base - color_6) +
           abs(color_base - color_7) +
           abs(color_base - color_8)) * vec4(512, 512, 512, 0);
}
''',
geometry='')
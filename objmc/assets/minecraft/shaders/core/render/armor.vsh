#version 150

#moj_import <light.glsl>
#moj_import <fog.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform mat4 TextureMat;
uniform int FogShape;
uniform float GameTime;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

out float vertexDistance;
out vec4 vertexColor;
out vec4 lightColor;
out vec4 overlayColor;
out float transition;
flat out int face;
flat out int isCustom;
flat out int isGUI;
flat out int noshadow;
out vec2 uv;
out vec3 uv0;
out vec3 uv1;
out vec3 uv2;
out vec3 Pos;
out vec4 pos0;
out vec4 pos1;
out vec4 pos2;

#define PI 3.1415926535897932
#define PI2 (PI*2)
#define SQ2 0.70710678118

#define SCALE (0.9375 / 16.)
#define GROW_OUTER 2
#define GROW_INNER 1
#define GROW_OUTER_PANTS 1.8
#define GROW_INNER_PANTS 0.8
#define CHEST_BODY ((vec3(8, 12, 4) + GROW_OUTER) * SCALE / 2.)
#define CHEST_ARM ((vec3(4, 12, 4) + GROW_OUTER) * SCALE / 2.)
#define PANTS_BODY ((vec3(8, 12, 4) + GROW_INNER_PANTS) * SCALE / 2.)
#define PANTS_LEG ((vec3(4, 12, 4) + GROW_INNER_PANTS) * SCALE / 2.)
#define BOOTS ((vec3(4, 12, 4) + GROW_OUTER_PANTS) * SCALE / 2.)

vec3[] directions = vec3[](
    vec3(-1, -1, -1), vec3(1, -1, -1), vec3(1, 1, -1), vec3(-1, 1, -1));

vec4[] offset = vec4[](
    // dimensions, directions array offset
    // right arm
    vec4(0), vec4(0), vec4(0), vec4(0), vec4(0), vec4(0),
    // left arm
    vec4(0), vec4(0), vec4(0), vec4(0), vec4(0), vec4(0),
    // body
    vec4(CHEST_BODY.xzy, 0), // top
    vec4(CHEST_BODY.xzy, 2), // bottom offset by 2
    vec4(CHEST_BODY.zyx, 0), // right
    vec4(CHEST_BODY.xyz, 0), // front
    vec4(CHEST_BODY.zyx, 0), // left
    vec4(CHEST_BODY.xyz, 0)  // back
);

#define PART_RIGHT_ARM 0
#define PART_LEFT_ARM 1
#define PART_CHEST 2

#moj_import <objmc_tools.glsl>

void main() {
    uv = UV0;
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color);
    lightColor = texelFetch(Sampler2, UV2 / 16, 0);
    overlayColor = vec4(1);

    #moj_import <objmc_armor.glsl>

    vertexDistance = fog_distance(Pos, FogShape);
    if (render) gl_Position = ProjMat * ModelViewMat * vec4(Pos, 1.0);
    else gl_Position = vec4(0);
}

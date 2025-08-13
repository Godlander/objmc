#version 150

#moj_import <minecraft:light.glsl>
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:globals.glsl>

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
out vec3 Pos;
out vec4 pos0;
out vec4 pos1;
out vec4 pos2;

#define PI 3.1415926535897932
#define SQ2 0.70710678118

#define PART_RIGHT_ARM 0
#define PART_LEFT_ARM 1
#define PART_CHEST 2
#define PART_RIGHT_LEG 3
#define PART_LEFT_LEG 4
#define PART_PANT_CHEST 5
#define PART_RIGHT_FEET 6
#define PART_LEFT_FEET 7

#define SCALE_PLAYER (0.9375/16.) //player, witch, villager, illager, wanderingtrader
#define SCALE_ARMORSTAND (1./16.) //armorstand, zombie, etc
#define SCALE_HUSK (1.0625/16.) //husk
#define SCALE_WITHERSKELETON (1.2/16.) //witherskeleton
#define SCALE_GIANT (6.0/16.) //giant
#define SCALE_BABY (0.5) //babies are half of original size
#define GROW_OUTER 2
#define GROW_INNER 1
#define GROW_OUTER_PANTS 1.8
#define GROW_INNER_PANTS 0.8

vec3[] directions = vec3[](
    vec3(-1, -1, -1), vec3(1, -1, -1), vec3(1, 1, -1), vec3(-1, 1, -1));

vec3 partsize(int scaleid, int body, int face, int corner) {
    float scale = 1;
    switch (scaleid) {
        case 0: scale = SCALE_PLAYER; break;
        case 1: scale = SCALE_ARMORSTAND; break;
        case 2: scale = SCALE_HUSK; break;
        case 3: scale = SCALE_WITHERSKELETON; break;
        case 4: scale = SCALE_GIANT; break;
        case 5: scale = SCALE_BABY; break;
    }

    vec3 size = vec3(0);
    switch (body) {
        case PART_RIGHT_ARM: case PART_LEFT_ARM:
            size = (vec3(4, 12, 4) + GROW_OUTER) * scale / 2.; break;
        case PART_CHEST:
            size = (vec3(8, 12, 4) + GROW_OUTER) * scale / 2.; break;
        case PART_RIGHT_LEG: case PART_LEFT_LEG:
            size = (vec3(4, 12, 4) + GROW_INNER_PANTS) * scale / 2.; break;
        case PART_PANT_CHEST:
            size = (vec3(8, 12, 4) + GROW_INNER_PANTS) * scale / 2.; break;
        case PART_RIGHT_FEET: case PART_LEFT_FEET:
            size = (vec3(4, 12, 4) + GROW_OUTER_PANTS) * scale / 2.; break;
    }

    switch (face) {
        case 0: return size.xzy * directions[corner]; // top
        case 1: return size.xzy * directions[(corner + 2) % 4]; //bottom offset by 2
        case 2: return size.zyx * directions[corner]; // right
        case 3: return size.xyz * directions[corner]; // front
        case 4: return size.zyx * directions[corner]; // left
        case 5: return size.xyz * directions[corner]; // back
    }
    return vec3(0);
}

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
#version 150

#moj_import <minecraft:light.glsl>
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>
#moj_import <minecraft:globals.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in vec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;


out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out vec4 vertexColor;

out vec4 lightColor;
out vec4 overlayColor;
out vec2 texCoord;
out vec2 texCoord2;
out vec3 Pos;
out float transition;

flat out int isCustom;
flat out int isGUI;
flat out int isHand;
flat out int noshadow;

#moj_import <objmc_tools.glsl>

void main() {
    Pos = Position;
    texCoord = UV0;
    overlayColor = vec4(1);
    lightColor = texelFetch(Sampler2, UV2 / 16, 0);
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color);

    //objmc
    #define ENTITY
    #moj_import <objmc_main.glsl>

    gl_Position = ProjMat * ModelViewMat * vec4(Pos, 1.0);

    sphericalVertexDistance = fog_spherical_distance(Pos);
    cylindricalVertexDistance = fog_cylindrical_distance(Pos);
}

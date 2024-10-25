#version 150

#moj_import <light.glsl>
#moj_import <fog.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform vec3 ModelOffset;
uniform int FogShape;
uniform float GameTime;

out float vertexDistance;
out vec4 vertexColor;
out vec4 lightColor;
out vec2 texCoord;
out vec2 texCoord2;
out vec3 Pos;
out float transition;

flat out int isCustom;
flat out int noshadow;

#moj_import <objmc_tools.glsl>

void main() {
    //default
    Pos = Position + ModelOffset;
    texCoord = UV0;
    vertexColor = Color;
    lightColor = minecraft_sample_lightmap(Sampler2, UV2);

    //objmc
    #define BLOCK
    #moj_import <objmc_main.glsl>

    gl_Position = ProjMat * ModelViewMat * vec4(Pos, 1.0);
    vertexDistance = fog_distance(Pos, FogShape);
}
#version 440

#moj_import <light.glsl>
#moj_import <fog.glsl>
#moj_import <tools.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform vec3 ChunkOffset;
uniform int FogShape;
uniform float GameTime;

out float vertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
out vec2 texCoord02;
out vec3 normal;
out float transition;

void main() {
    //default
    vec3 Pos = Position + ChunkOffset;
    texCoord0 = UV0;
    vertexColor = Color;
    normal = (ProjMat * ModelViewMat * vec4(Normal, 0.0)).rgb;

    //objmc
    #define BLOCK
    #moj_import <objmc.glsl>

    if (isCustom) { //custom shading
        vertexColor = vec4(vec3(clamp(dot(normal, vec3(0,1,0)) * 0.8 + 0.2, 0,1)), 1.0);
    }
    //non custom color
    else {vertexColor = Color;}
    vertexColor *= minecraft_sample_lightmap(Sampler2, UV2);
    gl_Position = ProjMat * ModelViewMat * vec4(Pos + posoffset, 1.0);
    vertexDistance = fog_distance(ModelViewMat, Position + posoffset, FogShape);
}
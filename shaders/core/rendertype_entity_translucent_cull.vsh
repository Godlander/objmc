#version 150

#moj_import <light.glsl>
#moj_import <fog.glsl>
#moj_import <getp.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in vec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform mat3 IViewRotMat;
uniform float GameTime;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

out float vertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
out vec2 texCoord1;
out vec2 texCoord2;
out vec4 normal;
out float transition;

void main() {
    //default
    normal = ProjMat * ModelViewMat * vec4(Normal, 0.0);
    texCoord0 = UV0;
    texCoord1 = UV1;
    texCoord2 = UV2;

    //objmc
    #define ENTITY
    #moj_import <objmc.glsl>

    vertexColor = vec4(vec3(max(dot(normal.xyz * IViewRotMat, Light0_Direction), 0.0)), 1.0);
    vertexColor *= vec4(vec3(max(dot(normal.xyz * IViewRotMat, Light1_Direction), 0.0)), 1.0);
    vertexColor += 0.4;
    gl_Position = ProjMat * ModelViewMat * (vec4(Position + (inverse(IViewRotMat) * posoffset), 1.0));
    vertexDistance = cylindrical_distance(ModelViewMat, Position + (inverse(IViewRotMat) * posoffset));
}
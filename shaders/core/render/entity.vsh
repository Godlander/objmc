#version 150

#moj_import <light.glsl>
#moj_import <fog.glsl>
#moj_import <tools.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV1;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform sampler2D Sampler2;

uniform float FogStart;
uniform float FogEnd;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform mat3 IViewRotMat;
uniform float GameTime;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

out float vertexDistance;
out vec4 vertexColor;
out vec4 lightMapColor;
out vec4 overlayColor;
out vec2 texCoord0;
out vec2 texCoord02;
out vec3 normal;
out float transition;

void main() {
    normal = (ProjMat * ModelViewMat * vec4(Normal, 0.0)).rgb;
    texCoord0 = UV0;
    overlayColor = texelFetch(Sampler1, UV1, 0);
    lightMapColor = texelFetch(Sampler2, UV2 / 16, 0);

    //objmc
    #define ENTITY
    #moj_import <objmc.glsl>
    //estimate rotation from normal
    if (autorotate) {
        vec3 localZ = IViewRotMat * Normal;
        vec3 localX = normalize(cross(vec3(0, 1, 0), localZ));
        vec3 localY = cross(localZ, localX);
        mat3 localRot = mat3(localX, localY, localZ);
        normal = inverse(IViewRotMat) * rotateX(rotation.r * 2*PI) * rotateY(rotation.g * 2*PI) * rotateZ(rotation.b * 2*PI) * localRot * normal;
        posoffset = inverse(IViewRotMat) * rotateX(rotation.x) * rotateY(rotation.y) * rotateZ(rotation.z) * localRot * posoffset;
    }
    //pure color rotation
    else if (isCustom && !isgui(ProjMat) && !(FogStart*0.000001 > 1)) {
        normal = inverse(IViewRotMat) * rotateX(rotation.r * 2*PI) * rotateY(rotation.g * 2*PI) * rotateZ(rotation.b * 2*PI) * normal;
        posoffset = inverse(IViewRotMat) * rotateX(rotation.x) * rotateY(rotation.y) * rotateZ(rotation.z) * posoffset;
    }
    //flip shading in gui bcos light goes the other way
    if (isgui(ProjMat)) {normal.xz = -normal.xz;}

    //maintain gui shading
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, Normal, Color);
    if (isCustom) { //custom shading
        vertexColor = vec4(vec3(max(dot(normal, Light0_Direction), 0.0)), 1.0);
        vertexColor *= vec4(vec3(max(dot(normal, Light1_Direction), 0.0)), 1.0);
        vertexColor = clamp(vertexColor+0.4, 0,1);
    }

    gl_Position = ProjMat * ModelViewMat * (vec4(Position + posoffset, 1.0));
    vertexDistance = cylindrical_distance(ModelViewMat, Position + posoffset);
}
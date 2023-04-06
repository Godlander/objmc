#version 150

#moj_import <light.glsl>
#moj_import <fog.glsl>

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

in float vertexDistance;
in vec4 vertexColor;
in vec4 lightColor;
in vec4 overlayColor;
in vec2 texCoord;
in vec2 texCoord2;
in vec3 Pos;
in float transition;

flat in int isCustom;
flat in int isGUI;
flat in int isHand;
flat in int noshadow;

out vec4 fragColor;

void main() {
    vec4 color = mix(texture(Sampler0, texCoord), texture(Sampler0, texCoord2), transition);

    //custom lighting
    #define ENTITY
    #moj_import<objmc_light.glsl>

    if (color.a < 0.01) discard;
    fragColor = linear_fog(color, vertexDistance, FogStart, FogEnd, FogColor);
}
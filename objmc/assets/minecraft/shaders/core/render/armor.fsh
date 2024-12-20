#version 150

#moj_import <fog.glsl>
#moj_import <light.glsl>

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;
uniform float GameTime;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

in float vertexDistance;
in vec4 vertexColor;
in vec4 lightColor;
in vec4 overlayColor;
in float transition;
flat in int face;
flat in int isCustom;
flat in int isGUI;
flat in int noshadow;
in vec2 uv;
in vec3 uv0;
in vec3 uv1;
in vec3 uv2;
in vec3 Pos;
in vec4 pos0;
in vec4 pos1;
in vec4 pos2;

out vec4 fragColor;

void main() {
    vec4 color = texture(Sampler0, uv);

    if (isCustom == 1) {
        //discard the upside down face between front and back
        vec2 _uv0 = uv0.xy / uv0.z;
        vec2 _uv1 = uv1.xy / uv1.z;
        vec2 _uv2 = uv2.xy / uv2.z;
        vec3 _pos0 = pos0.xyz / pos0.w;
        vec3 _pos1 = pos1.xyz / pos1.w;
        vec3 _pos2 = pos2.xyz / pos2.w;
        vec3 maxpos = max(max(_pos0, _pos1), _pos2);
        bool orientation = (_pos2.y == maxpos.y);
        switch (face) {
            case 15: if (!orientation) discard; break;
            case 17: if (orientation) discard; break;
        }
    }

    //custom lighting
    #define ENTITY
    #moj_import <objmc_light.glsl>

    if (color.a < ALPHA_CUTOUT) discard;
    fragColor = linear_fog(color, vertexDistance, FogStart, FogEnd, FogColor);
}

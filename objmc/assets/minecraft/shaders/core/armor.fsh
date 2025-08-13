#version 150

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:light.glsl>
#moj_import <minecraft:dynamictransforms.glsl>

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
in vec3 Pos;
in vec4 pos0;
in vec4 pos1;
in vec4 pos2;

out vec4 fragColor;

void main() {
    vec4 color = texture(Sampler0, uv);

    if (isCustom == 1) {
        //discard the upside down face between front and back
        float y0 = pos0.y / pos0.w;
        float y1 = pos1.y / pos1.w;
        float y2 = pos2.y / pos2.w;
        float maxy = max(max(y0, y1), y2);
        bool orientation = (y2 == maxy);
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
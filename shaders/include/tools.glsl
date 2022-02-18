//objmc
//https://github.com/Godlander/objmc

#define PI 3.1415926535897932

ivec2 getp(ivec2 topleft, ivec2 size, int yoffset, int index, int offset) {
    int i = (index * 5) + offset;
    return topleft + ivec2(i % size.x, int(i / size.x) + yoffset);
}

//3d rotation functions from github copilot autocomplete
mat3 rotateX(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(1, 0, 0, 0, c, -s, 0, s, c);
}
mat3 rotateY(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(c, 0, s, 0, 1, 0, -s, 0, c);
}
mat3 rotateZ(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat3(c, -s, 0, s, c, 0, 0, 0, 1);
}

//gui item model detection from Onnowhere
bool isgui(mat4 ProjMat) {
    return ProjMat[3][2] == -2.0;
}
//first person hand item model detection from esben
bool ishand(float FogStart) {
    return FogStart*0.000001 > 1;
}

//4 point bezier formula from Dominexis
vec3 bezb(vec3 a, vec3 b, vec3 c, vec3 d, float t) {
    float t2 = t * t;
    float t3 = t2 * t;
    return (d-3*c+3*b-a)*t3 + (3*c-6*b+3*a)*t2 + (3*b-3*a)*t + a;
}
vec3 bezier(vec3 a, vec3 b, vec3 c, vec3 d, float t) {
    return bezb(b,b+(c-a)/6,c-(d-b)/6,c,t);
}
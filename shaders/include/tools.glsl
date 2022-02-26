//objmc
//https://github.com/Godlander/objmc

#define PI 3.1415926535897932

ivec2 getp(ivec2 topleft, ivec2 size, int yoffset, int index, int offset) {
    int i = (index * 5) + offset;
    return topleft + ivec2(i % size.x, int(i / size.x) + yoffset);
}

//3d rotation matrix from Barf Creations
mat3 rotate(vec3 angles) {
    float sx = sin(angles.x);
    float cx = cos(angles.x);
    float sy = sin(-angles.y);
    float cy = cos(-angles.y);
    float sz = sin(-angles.z);
    float cz = cos(-angles.z);
    return mat3(cy*cz,            cy*sz,           -sy,
                sx*sy*cz - cx*sz, sx*sy*sz + cx*cz, sx*cy,
                cx*sy*cz + sx*sz, cx*sy*sz - sx*cz, cx*cy);
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
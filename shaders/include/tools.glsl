//objmc
//https://github.com/Godlander/objmc

#define PI 3.1415926535897932

bool isgui(mat4 ProjMat) {
    return ProjMat[3][2] == -2.0;
}

ivec2 getp(ivec2 topleft, ivec2 size, int yoffset, int index, int offset) {
    int i = (index * 5) + offset;
    return topleft + ivec2(i % size.x, int(i / size.x) + yoffset);
}

mat3 rotateX(float angle) {
    return mat3(1.0,    0.0    ,     0.0    ,
                0.0, cos(angle), -sin(angle),
                0.0, sin(angle),  cos(angle));
}
mat3 rotateY(float angle) {
    return mat3(cos(angle), 0.0, sin(angle),
                   0.0    , 1.0,    0.0    ,
               -sin(angle), 0.0, cos(angle));
}
mat3 rotateZ(float angle) {
    return mat3(cos(angle), -sin(angle), 0.0,
                sin(angle),  cos(angle), 0.0,
                   0.0    ,    0.0     , 1.0);
}

// From Onnowhere's shader utils: https://github.com/onnowhere/core_shaders/blob/master/.shader_utils/vsh_util.glsl
#define LIGHT0_DIRECTION vec3(0.2, 1.0, -0.7)
#define LIGHT1_DIRECTION vec3(-0.2, 1.0, 0.7)
mat3 getWorldMat(vec3 light0, vec3 light1) {
    if (abs(light0) == abs(light1)) return mat3(10000.0);
    
    mat3 V = mat3(normalize(LIGHT0_DIRECTION), normalize(LIGHT1_DIRECTION), normalize(cross(LIGHT0_DIRECTION, LIGHT1_DIRECTION)));
    mat3 W = mat3(normalize(light0), normalize(light1), normalize(cross(light0, light1)));
    return W * inverse(V);
}
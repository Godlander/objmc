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
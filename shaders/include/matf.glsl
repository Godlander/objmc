//credit to DartCat25

#define X 0
#define Y 1
#define Z 2

mat4 MakeMat4() {
    return mat4(1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0);
}

mat4 Translate(float x, float y, float z) {
    return mat4(1.0, 0.0, 0.0,  x,
                0.0, 1.0, 0.0,  y,
                0.0, 0.0, 1.0,  z,
                0.0, 0.0, 0.0, 1.0);
}

mat4 Translate(vec3 offset) {
    return mat4(1.0, 0.0, 0.0, offset.x,
                0.0, 1.0, 0.0, offset.y,
                0.0, 0.0, 1.0, offset.z,
                0.0, 0.0, 0.0, 1.0);
}

mat4 Scale(float x, float y, float z) {
    return mat4( x , 0.0, 0.0, 0.0,
                0.0,  y , 0.0, 0.0,
                0.0, 0.0,  z , 0.0,
                0.0, 0.0, 0.0, 1.0);
}

mat4 Scale(vec3 scale) {
    return mat4( scale.x,   0.0  ,   0.0  , 0.0,
                   0.0  , scale.y,   0.0  , 0.0,
                   0.0  ,   0.0  , scale.z, 0.0,
                   0.0  ,   0.0  ,   0.0  , 1.0);
}
mat3 Rotate3(float angle, int type)
{
    if (type == 0)
        return mat3(1.0,    0.0    ,     0.0    ,
                    0.0, cos(angle), -sin(angle),
                    0.0, sin(angle),  cos(angle));
    if (type == 1)
        return mat3( cos(angle), 0.0, sin(angle),
                        0.0    , 1.0,    0.0    ,
                    -sin(angle), 0.0, cos(angle));
    if (type == 2)
        return mat3(cos(angle), -sin(angle), 0.0,
                    sin(angle),  cos(angle), 0.0,
                       0.0    ,    0.0     , 1.0);

    return mat3(0.0);
}
mat4 Rotate(float angle, int type) {
    if (type == 0)
        return mat4(1.0,    0.0    ,     0.0    , 0.0,
                    0.0, cos(angle), -sin(angle), 0.0,
                    0.0, sin(angle),  cos(angle), 0.0,
                    0.0,    0.0    ,     0.0    , 1.0);
    if (type == 1)
        return mat4( cos(angle), 0.0, sin(angle), 0.0,
                        0.0    , 1.0,    0.0    , 0.0,
                    -sin(angle), 0.0, cos(angle), 0.0,
                        0.0    , 0.0,    0.0    , 1.0);
    if (type == 2)
        return mat4(cos(angle), -sin(angle), 0.0, 0.0,
                    sin(angle),  cos(angle), 0.0, 0.0,
                       0.0    ,    0.0     , 1.0, 0.0,
                       0.0    ,    0.0     , 0.0, 1.0);
    return mat4(0.0);
}
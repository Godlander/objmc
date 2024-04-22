//objmc
//https://github.com/Godlander/objmc

#define PI 3.1415926535897932

ivec4 getmeta(ivec2 topleft, int offset) {
    return ivec4(texelFetch(Sampler0, topleft + ivec2(offset,0), 0) * 255);
}
vec3 getpos(ivec2 topleft, int w, int h, int index) {
    int i = index*3;
    vec4 x = texelFetch(Sampler0, topleft + ivec2((i  )%w,h+((i  )/w)), 0);
    vec4 y = texelFetch(Sampler0, topleft + ivec2((i+1)%w,h+((i+1)/w)), 0);
    vec4 z = texelFetch(Sampler0, topleft + ivec2((i+2)%w,h+((i+2)/w)), 0);
    return vec3(
        (x.r*256)+(x.g)+(x.b/256),
        (y.r*256)+(y.g)+(y.b/256),
        (z.r*256)+(z.g)+(z.b/256)
    )*(255./256.) - vec3(128);
}
vec2 getuv(ivec2 topleft, int w, int h, int index) {
    int i = index*2;
    vec4 x = texelFetch(Sampler0, topleft + ivec2((i  )%w,h+((i  )/w)), 0);
    vec4 y = texelFetch(Sampler0, topleft + ivec2((i+1)%w,h+((i+1)/w)), 0);
    return vec2(
        ((x.g*65280)+(x.b*255))/65535,
        ((y.g*65280)+(y.b*255))/65535
    );
}
ivec2 getvert(ivec2 topleft, int w, int h, int index, bool compressionEnabled) {

    if(!compressionEnabled) {
        int i = index*2;
        ivec4 a = ivec4(texelFetch(Sampler0, topleft + ivec2((i  )%w,h+((i  )/w)), 0)*255);
        ivec4 b = ivec4(texelFetch(Sampler0, topleft + ivec2((i+1)%w,h+((i+1)/w)), 0)*255);
        return ivec2(
            ((a.r*65536)+(a.g*256)+a.b),
            ((b.r*65536)+(b.g*256)+b.b)
        );
    } else {
        ivec4 a = ivec4(texelFetch(Sampler0, topleft + ivec2((index  )%w,h+((index  )/w)), 0)*255);
        return ivec2(
            ((a.r*65536)+(a.g*256)+a.b),
            a.a - 1
        );
    }
}

ivec2 huv(int id) {
  if (id < 1056)
    return ivec2((32 + id % 32), (id/32));
  else
    id -= 1056;
    return ivec2((id % 64), 33 + int(id/64));
}

bool getb(int i, int b) {
    return bool((i>>b)&1);
}
int getb(int i, int b, int s) {
    return (i>>b)&((1<<s)-1);
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
    return ProjMat[2][3] == 0.0;
}
//first person hand item model detection from esben
bool ishand(float FogStart, mat4 ProjMat) {
    return (FogStart > 3e38) && (ProjMat[2][3] != 0);
}

//hue to rgb
vec3 hrgb(float h) {
    vec3 K = vec3(1.0, 2.0 / 3.0, 1.0 / 3.0);
    vec3 p = abs(fract(K.xyz + h) * 6.0 - 3.0);
    return clamp(p - K.xxx, 0.0, 1.0);
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


float over_color(float c_a, float a_a, float c_b, float a_b, float a_0) {
    return (c_a * a_a + c_b * a_b * (1.0 - a_a)) / a_0;
}
vec4 over(vec4 overC, vec4 under) {
    float a_0 = overC.a + (under.a * (1.0 - overC.a));
    return vec4(
        over_color(overC.r, overC.a, under.r, under.a, a_0),
        over_color(overC.g, overC.a, under.g, under.a, a_0),
        over_color(overC.b, overC.a, under.b, under.a, a_0),
        a_0
    );
}

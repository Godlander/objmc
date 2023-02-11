//objmc
//https://github.com/Godlander/objmc

isCustom = 0;
int corner = gl_VertexID % 4;
float onepixel = 1./64;
ivec2 uv = ivec2((UV0 * 64));
vec3 posoffset = vec3(0);
//if marker is correct
if (textureSize(Sampler0, 0) == vec2(64) && ivec4(texelFetch(Sampler0, ivec2(0,32), 0)*255) == ivec4(12,34,56,78)) {
    isCustom = 1;
    ivec4 meta = ivec4(texelFetch(Sampler0, ivec2(1,32), 0)*255);
    noshadow = meta.b;
    int npos = meta.r*256 + meta.g;

    isGUI = int(isgui(ProjMat));
    isHand = int(ishand(FogStart) && !bool(isGUI));

    int id = gl_VertexID;
    ivec2 xy = ivec2(32 + id % 32, id / 32);
    ivec4 face = ivec4(texelFetch(Sampler0, xy, 0)*255);
    if (face.a == 0) Pos = posoffset = vec3(0);
    ivec2 index = ivec2(((face.r>>4)<<8)+face.g, ((face.r%32)<<8)+face.b+npos);
    xy = ivec2(index.x % 64, 33 + int(index.x/64));
    posoffset = texelFetch(Sampler0, xy, 0).rgb;
    xy = ivec2(index.y % 64, 33 + int(index.y/64));
    texCoord = texelFetch(Sampler0, xy, 0).rg;

    posoffset = posoffset * IViewRotMat;
    //final pos and uv
    Pos += posoffset;
    texCoord = (texCoord)/64.
                //make sure that faces with same uv beginning/ending renders
                + vec2(onepixel * 0.0001 * corner, onepixel * 0.0001 * ((corner + 1) % 4));
}
//debug
//else {
//    posoffset = vec3(gl_VertexID % 4 - 2, gl_VertexID % 4 / 2 * 2, -(gl_VertexID % 4) + 2 * 2);
//    Pos += posoffset;
//    vertexColor = vec4(1.0,0.0,0.0,1.0);
//}
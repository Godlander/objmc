//objmc
//https://github.com/Godlander/objmc

isCustom = 0;
int corner = gl_VertexID % 4;
float onepixel = 1./64;
ivec2 uv = ivec2((UV0 * 64));
vec3 posoffset = vec3(0);
//if marker is correct
ivec4 marker = ivec4(texelFetch(Sampler0, ivec2(0,32), 0)*255);
if (textureSize(Sampler0, 0) == vec2(64) && (marker == ivec4(12,34,56,78) || marker == ivec4(13,33,56,78))) {
    isCustom = 1;
    ivec4 metan = ivec4(texelFetch(Sampler0, ivec2(1,32), 0)*255);
    int nfaces = ((metan.r>>4)<<8)+metan.g;
    int npos   = ((metan.r%32)<<8)+metan.b;
    int nvertices = nfaces * 4;
    ivec4 metad = ivec4(texelFetch(Sampler0, ivec2(2,32), 0)*255);
    float scale = metad.g;
    noshadow = metad.r;

    isGUI = int(isgui(ProjMat));
    isHand = int(ishand(FogStart) && !bool(isGUI));

    int eid = (gl_VertexID/48) % ((nfaces+11)/12);
    int vid = (eid * 48) + (gl_VertexID % 48);
    ivec4 face = ivec4(texelFetch(Sampler0, hid(vid), 0)*255);
    if (vid > nvertices) Pos = posoffset = vec3(0);
    int pid = ((face.r>>4)<<8)+face.g + nvertices;
    int uid = ((face.r%32)<<8)+face.b + nvertices+npos;
    posoffset = texelFetch(Sampler0, hid(pid), 0).rgb;
    texCoord = texelFetch(Sampler0, hid(uid), 0).rg;

    posoffset = (posoffset - vec3(0.5)) * scale * IViewRotMat;
    //final pos and uv
    Pos += posoffset;
    texCoord = clamp(vec2(texCoord.x, 1-texCoord.y)/2., 0.0001, 0.4999)
                //make sure that faces with same uv beginning/ending renders
                + onepixel*vec2(0.0001*corner, 0.0001*((corner + 1) % 4));
}
//debug
//else {
//    posoffset = vec3(gl_VertexID % 4 - 2, gl_VertexID % 4 / 2 * 2, -(gl_VertexID % 4) + 2 * 2);
//    Pos += posoffset;
//    vertexColor = vec4(1.0,0.0,0.0,1.0);
//}
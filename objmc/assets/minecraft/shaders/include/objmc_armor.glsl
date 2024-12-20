
isCustom = 0;
Pos = Position;
bool render = true;
bool flip = false;
int headerheight = 0;
bool compression = false;
ivec2 atlasSize = textureSize(Sampler0, 0);
vec2 onepixel = 1./atlasSize;
isGUI = int(isgui(ProjMat));

ivec4 t[8];

int id = gl_VertexID % 72;
face = (id / 4);
int body = face / 6;
int corner = id % 4;
int fid = (gl_VertexID / 72);
int vid = fid * 4 + corner;
uv0 = uv1 = uv2 = vec3(0);
pos0 = pos1 = pos2 = vec4(0);

ivec4 marker = ivec4(texelFetch(Sampler0, ivec2(0), 0)*255);
if (marker == ivec4(12,34,56,78) || marker == ivec4(12,34,56,79)) {
    compression = marker.a == 79;
    isCustom = 1;

    for (int i = 1; i < 8; i++) {
        t[i] = getmeta(ivec2(0), i);
    }
    //1: texsize
    ivec2 size = ivec2(t[1].r*256 + t[1].g, t[1].b*256 + t[1].a);
    //2: nvertices
    int nvertices = t[2].r*16777216 + t[2].g*65536 + t[2].b*256 + t[2].a;
    if (fid >= nvertices / 4) render = false;
    //3: nobjs, ntexs
    int nframes = max(t[3].r*65536 + t[3].g*256 + t[3].b, 1);
    int ntextures = max(t[3].a, 1);
    //5: data heights
    int vph = t[5].r*256 + t[5].g;
    int vth = t[5].b*256 + t[5].a;
    //6: noshadow, autorotate, visibility, colorbehavior
    noshadow = getb(t[6].r, 7, 1);

    switch (corner) {
        case 0: uv0 = vec3(UV0, 1); pos0 = vec4(Position, 1); break;
        case 1: uv1 = vec3(UV0, 1); pos1 = vec4(Position, 1); break;
        case 2: uv2 = vec3(UV0, 1); pos2 = vec4(Position, 1); break;
    }

    vec4 color = texture(Sampler0, uv);
    float yaw = -atan(Normal.x, Normal.z);
    float pitch = -atan(Normal.y, length(Normal.xz));
    vec3 rotation = vec3(pitch, yaw, 0);

    //to origin
    if (face == 15) {
        if (Normal.y < 0) flip = true;
        else render = false;
    }
    vec3 dir = directions[(corner + int(offset[face].w)) % 4];
    vec3 posoffset = dir * offset[face].xyz;
    if (flip) posoffset.xy *= -1;
    Pos += rotate(rotation) * posoffset;

    //calculate height offsets
    headerheight = 1 + int(ceil(nvertices*0.25/size.x));
    int height = headerheight + (size.y * ntextures);
    //read data
    ivec2 index = getvert(ivec2(0), size.x, height+vph+vth, vid, compression);
    posoffset = getpos(ivec2(0), size.x, height, index.x);

    posoffset += vec3(0, -0.4, -0.4);
    posoffset.z *= -1;

    uv = getuv(ivec2(0), size.x, height+vph, index.y);
    uv = (vec2(0, headerheight) + uv*size) / atlasSize
        //make sure that faces with same uv beginning/ending renders
        + vec2(onepixel.x*0.0001*corner,onepixel.y*0.0001*((corner+1)%4));
    //posoffset = dir * vec3(0.2,0.3,0) + vec3(0, 0, 0.4) + fid * 0.5;

    //rotate top/bottom faces
    if (face == 12) rotation.x += PI/2;
    else if (face == 13) rotation.x -= PI/2;
    else if (flip) posoffset.yz *= -1;

    Pos += rotate(rotation) * posoffset;

    if (!(
        ((face == 0 || ((face & 1) == 1)) && (abs(Normal.y) < SQ2))
    )) render = false;
    if (body != 2) render = false;
}
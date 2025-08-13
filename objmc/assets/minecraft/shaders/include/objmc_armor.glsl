
isCustom = 0;
Pos = Position;
bool render = true;
bool flip = false;
ivec2 atlasSize = textureSize(Sampler0, 0);
vec2 onepixel = 1./atlasSize;
vec3 posoffset = vec3(0);
float scale = 1;
vec3 rotation = vec3(0);
int headerheight = 0;
bool compression = false;

pos0 = pos1 = pos2 = vec4(0);
ivec4 t[8];

int id = gl_VertexID % 72;
face = (id / 4);
int body = face / 6;
int corner = id % 4;

ivec4 marker = ivec4(texelFetch(Sampler0, ivec2(0), 0)*255);
if (marker == ivec4(12,34,56,78) || marker == ivec4(12,34,56,79)) {
    compression = marker.a == 79;
    isCustom = 1;

    switch (corner) {
        case 0: pos0 = vec4(Position, 1); break;
        case 1: pos1 = vec4(Position, 1); break;
        case 2: pos2 = vec4(Position, 1); break;
    }

    for (int i = 1; i < 8; i++) {
        t[i] = getmeta(ivec2(0), i);
    }
    //1: texsize
    ivec2 size = ivec2(t[1].r*256 + t[1].g, t[1].b*256 + t[1].a);
    //2: nvertices
    int nvertices = t[2].r*16777216 + t[2].g*65536 + t[2].b*256 + t[2].a;
    //3: nobjs, ntexs
    int nframes = max(t[3].r*65536 + t[3].g*256 + t[3].b, 1);
    int ntextures = max(t[3].a, 1);
    //4: duration, autoplay, easing
    float duration = max(t[4].r*65536 + t[4].g*256 + t[4].b, 1);
    bool autoplay = getb(t[4].a, 6);
    ivec2 easing = ivec2(getb(t[4].a, 4, 2), getb(t[4].a, 2, 2));
    //5: data heights
    int vph = t[5].r*256 + t[5].g;
    int vth = t[5].b*256 + t[5].a;
    //6: noshadow, autorotate, visibility, colorbehavior
    noshadow = getb(t[6].r, 7, 1);
    bvec3 visibility = bvec3(getb(t[6].r, 4), getb(t[6].r, 3), getb(t[6].r, 2));
    int colorbehavior = getb(t[6].r, 0, 1)*256 + t[6].g;

    //time in ticks
    float time = GameTime * 24000;
    int tcolor = 0;

    //face rotation
    float yaw = -atan(Normal.x, Normal.z);
    float pitch = -atan(Normal.y, length(Normal.xz));
    vec3 Rot = vec3(pitch, yaw, 0);
    //back face flips when upside down
    if (face == 15) {
        if (Normal.y < 0) flip = true;
        else render = false;
    }
    //to origin
    posoffset = partsize(0, body, face % 6, corner);
    if (flip) posoffset.xy *= -1;
    Pos += rotate(Rot) * posoffset;

    isGUI = int(isgui(ProjMat));
    if (((isGUI == 0) && visibility.x) || (bool(isGUI) && visibility.z)) {
        //colorbehavior
        if (colorbehavior == 219) { //animation frames 0-8388607
            tcolor = (int(Color.r*255)*65536)%32768 + int(Color.g*255)*256 + int(Color.b*255);
            //interpolation disabled past 8388608, suso's idea to define starting tick with color
            autoplay = (Color.r <= 0.5);
        } else {
            //bits from colorbehavior
            vec3 accuracy = vec3(255./256.);
            vec3 accuracy2 = vec3(255./256.);
            vec2 tscale = vec2(0, 255./256.);
            vec2 thue = vec2(0, 255./256.);
            switch ((colorbehavior>>6)&7) { //first 3 bits, r
                //time
                case 3: tcolor = tcolor*256 + int(Color.r*255); break;
                //scale
                case 4: tscale.x = Color.r*255; tscale.y *= 256; break;
                //hue
                case 5: thue.x = Color.r*255; thue.y *= 256; break;
                //hurt tint
                case 6: if (Color.r != 0) overlayColor = vec4(1,0.7,0.7,1); break;
            }
            switch ((colorbehavior>>3)&7) { //second 3 bits, g
                //time
                case 3: tcolor = tcolor*256 + int(Color.g*255); break;
                //scale
                case 4: tscale.x = tscale.x*256 + Color.g*255; tscale.y *= 256; break;
                //hue
                case 5: thue.x = thue.x*256 + Color.g*255; thue.y *= 256; break;
                //hurt tint
                case 6: if (Color.g != 0) overlayColor = vec4(1,0.7,0.7,1); break;
            }
            switch (colorbehavior&7) { //third 3 bits, b
                //time
                case 3: tcolor = tcolor*256 + int(Color.b*255); break;
                //scale
                case 4: tscale.x = tscale.x*256 + Color.b*255; tscale.y *= 256; break;
                //hue
                case 5: thue.x = thue.x*256 + Color.b*255; thue.y *= 256; break;
                //hurt tint
                case 6: if (Color.b != 0) overlayColor = vec4(1,0.7,0.7,1); break;
            }
            if (tscale.x > 0) scale = tscale.x/tscale.y;
            if (thue.x > 0) overlayColor = vec4(hrgb(thue.x/thue.y),1);
        }
        time = autoplay ? time + duration - mod(tcolor, duration) : tcolor;
        int frame = int(time * nframes / duration) % nframes;
        //relative vertex id from unique face uv
        int fid = (gl_VertexID / 72);
        int vid = (fid * 4 + corner) % nvertices;
        vid += frame * nvertices;
        //calculate height offsets
        headerheight = 1 + int(ceil(nvertices*0.25/size.x));
        int height = headerheight + (size.y * ntextures);
        //read data
        ivec2 index = getvert(ivec2(0), size.x, height+vph+vth, vid, compression);
        posoffset = getpos(ivec2(0), size.x, height, index.x);
        if (nframes > 1) {
            int nids = (nframes * nvertices);
            //next frame
            vid = (vid+nvertices) % nids;
            index = getvert(ivec2(0), size.x, height+vph+vth, vid, compression);
            vec3 posoffset2 = getpos(ivec2(0), size.x, height, index.x);
            //interpolate
            transition = fract(time * nframes / duration);
            switch (easing.x) { //easing
                case 1: //linear
                    posoffset = mix(posoffset, posoffset2, transition);
                    break;
                case 2: //in-out cubic
                    transition = transition < 0.5 ? 4 * transition * transition * transition : 1 - pow(-2 * transition + 2, 3) * 0.5;
                    posoffset = mix(posoffset, posoffset2, transition);
                    break;
                case 3: //4-point bezier
                    //third point
                    vid = (vid+nvertices) % nids;
                    index = getvert(ivec2(0), size.x, height+vph+vth, vid, compression);
                    vec3 posoffset3 = getpos(ivec2(0), size.x, height, index.x);
                    //fourth point
                    vid = (vid+nvertices) % nids;
                    index = getvert(ivec2(0), size.x, height+vph+vth, vid, compression);
                    vec3 posoffset4 = getpos(ivec2(0), size.x, height, index.x);
                    //bezier
                    posoffset = bezier(posoffset, posoffset2, posoffset3, posoffset4, transition);
                    break;
            }
        }

        uv = getuv(ivec2(0), size.x, height+vph, index.y);
        uv = (vec2(0, headerheight) + uv*size) / atlasSize
            //make sure that faces with same uv beginning/ending renders
            + vec2(onepixel.x*0.0001*corner,onepixel.y*0.0001*((corner+1)%4));

        //rotate top/bottom faces
        if (face == 12) Rot.x += PI/2;
        else if (face == 13) Rot.x -= PI/2;
        else if (flip) posoffset.yz *= -1;

        Pos += rotate(Rot) * posoffset;

    }

    //discard faces that arnt used to calculate rotation
    if (!(
        ((face == 0 || ((face & 1) == 1)) && (abs(Normal.y) < SQ2))
    )) render = false;
    if (body != PART_CHEST) render = false;
    if (isGUI == 1) render = false;
}
//objmc
//https://github.com/Godlander/objmc

isCustom = 0;
int corner = gl_VertexID % 4;
ivec2 atlasSize = textureSize(Sampler0, 0);
vec2 onepixel = 1./atlasSize;
ivec2 uv = ivec2((UV0 * atlasSize));
vec3 posoffset = vec3(0);
vec3 rotation = vec3(0);
int headerheight = 0;
ivec4 t[8];
//read uv offset
t[0] = ivec4(texelFetch(Sampler0, uv, 0) * 255);
ivec2 uvoffset = ivec2(t[0].r*256 + t[0].g, t[0].b*256 + t[0].a);
//find and read topleft pixel
ivec2 topleft = uv - uvoffset;
//if topleft marker is correct
if (ivec4(texelFetch(Sampler0, topleft, 0)*255) == ivec4(12,34,56,78)) {
    isCustom = 1;
    // header
    //| 2^16x2   | 2^32      | 2^24 + 2^8   | 2^24    + \1 2^1  + 2^2   + 2^2 \2| 2^16x2       | 2^1     + 2^2       + 2^3    \2 + 2^8        \16|
    //| tex size | nvertices | nobjs, ntexs | duration, autoplay, easing, interp| data heights | noshadow, autorotate, visibility, colorbehavior |
    for (int i = 1; i < 8; i++) {
        t[i] = getmeta(topleft, i);
    }
    //1: texsize
    ivec2 size = ivec2(t[1].r*256 + t[1].g, t[1].b*256 + t[1].a);
    //2: nvertices
    int nvertices = t[2].r*16777216 + t[2].g*65536 + t[2].b*256 + t[2].a;
    //3: nobjs, ntexs
    int nframes = max(t[3].r*65536 + t[3].g*256 + t[3].b, 1);
    int ntextures = max(t[3].a, 1);
    //4: duration, autoplay, easing
    int duration = max(t[4].r*65536 + t[4].g*256 + t[4].b, 1);
    bool autoplay = getb(t[4].a, 6);
    ivec2 easing = ivec2(getb(t[4].a, 4, 2), getb(t[4].a, 2, 2));
    //5: data heights
    int vph = t[5].r*256 + t[5].g;
    int vth = t[5].b*256 + t[5].a;
    //6: noshadow, autorotate, visibility, colorbehavior
    noshadow = getb(t[6].r, 8, 1);
    vec2 autorotate = vec2(getb(t[6].r, 6, 1), getb(t[6].r, 5, 1));
    bvec3 visibility = bvec3(getb(t[6].r, 4), getb(t[6].r, 3), getb(t[6].r, 2));
    int colorbehavior = t[6].g;

    //time in ticks
    float time = GameTime * 24000;
    int tcolor = 0;

#ifdef BLOCK
    if (!visibility.x) { //world
        Pos = vec3(0); posoffset = vec3(0);
    } else {
#endif
#ifdef ENTITY
    isGUI = int(isgui(ProjMat));
    isHand = int(ishand(FogStart) && !bool(isGUI));
    if (((isGUI + isHand == 0) && visibility.x) || (bool(isHand) && visibility.y) || (bool(isGUI) && visibility.z)) {
        //colorbehavior
        overlayColor = vec4(1);
        if (colorbehavior == 243) { //animation frames 0-8388607
            tcolor = (int(Color.r*255)*65536)%32768 + int(Color.g*255)*256 + int(Color.b*255);
            //interpolation disabled past 8388608, suso's idea to define starting tick with color
            autoplay = (Color.r <= 0.5);
        } else {
            //bits from colorbehavior
            vec3 accuracy = vec3(255./256.);
            switch ((colorbehavior/64)%4) { //first byte of color
                case 0: rotation.x += Color.r*255; accuracy.r *= 256; break;
                case 1: rotation.y += Color.r*255; accuracy.g *= 256; break;
                case 2: rotation.z += Color.r*255; accuracy.b *= 256; break;
                case 3: tcolor = tcolor * 256 + int(Color.r*255); break;
            }
            switch ((colorbehavior/16)%4) { //second byte of color
                case 0: rotation.x += Color.g*255; accuracy.r *= 256; break;
                case 1: rotation.y += Color.g*255; accuracy.g *= 256; break;
                case 2: rotation.z += Color.g*255; accuracy.b *= 256; break;
                case 3: tcolor = tcolor * 256 + int(Color.g*255); break;
            }
            switch (colorbehavior%16) { //third byte of color
                case 0: rotation.x += Color.b*255; accuracy.r *= 256; break;
                case 1: rotation.y += Color.b*255; accuracy.g *= 256; break;
                case 2: rotation.z += Color.b*255; accuracy.b *= 256; break;
                case 3: tcolor = tcolor * 256 + int(Color.b*255); break;
                case 4: if (Color.b > 0) overlayColor = vec4(hrgb(Color.b),1); break;
            }
            rotation = rotation/accuracy * 2*PI;
        }
#endif
        time = autoplay ? time + duration - mod(tcolor, duration) : tcolor;
        int frame = int(time * nframes / duration) % nframes;
        //relative vertex id from unique face uv
        int id = (((uvoffset.y-1) * size.x) + uvoffset.x) * 4 + corner;
        id += frame * nvertices;
        //calculate height offsets
        headerheight = 1 + int(ceil(nvertices*0.25/size.x));
        int height = headerheight + (size.y);
        //read data
        ivec2 index = getvert(topleft, size.x, height+vph+vth, id);
        posoffset = getpos(topleft, size.x, height, index.x);
        texCoord = getuv(topleft, size.x, height+vph, index.y) * size;
        if (nframes > 1) {
            int nids = (nframes * nvertices);
            //next frame
            id = (id+nvertices) % nids;
            index = getvert(topleft, size.x, height+vph+vth, id);
            vec3 posoffset2 = getpos(topleft, size.x, height, index.x);
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
                    id = (id+nvertices) % nids;
                    index = getvert(topleft, size.x, height+vph+vth, id);
                    vec3 posoffset3 = getpos(topleft, size.x, height, index.x);
                    //fourth point
                    id = (id+nvertices) % nids;
                    index = getvert(topleft, size.x, height+vph+vth, id);
                    vec3 posoffset4 = getpos(topleft, size.x, height, index.x);
                    //bezier
                    posoffset = bezier(posoffset, posoffset2, posoffset3, posoffset4, transition);
                    break;
            }
        }
//custom entity rotation
#ifdef ENTITY
        if (isHand + isGUI == 0) {
            if (any(greaterThan(autorotate,vec2(0)))) {
                //normal estimated rotation calculation from The Der Discohund
                vec3 local = IViewRotMat * Normal;
                float yaw = -atan(local.x, local.z);
                float pitch = -atan(local.y, length(local.xz));
                posoffset = rotate(vec3(vec2(pitch,yaw)*autorotate,0) + rotation) * posoffset * IViewRotMat;
            }
            //pure color rotation
            else {
                posoffset = rotate(rotation) * posoffset * IViewRotMat;
            }
        }
    }
#endif
#ifdef BLOCK
    }
#endif
    //final pos and uv
    Pos += posoffset;
    texCoord = (vec2(topleft.x, topleft.y+headerheight) + texCoord)/atlasSize
                //make sure that faces with same uv beginning/ending renders
                + vec2(onepixel.x * 0.0001 * corner, onepixel.y * 0.0001 * ((corner + 1) % 4));
}
//debug
//else {
//    posoffset = vec3(gl_VertexID % 4 - 2, gl_VertexID % 4 / 2 * 2, -(gl_VertexID % 4) + 2 * 2);
//    Pos += posoffset;
//    vertexColor = vec4(1.0,0.0,0.0,1.0);
//}
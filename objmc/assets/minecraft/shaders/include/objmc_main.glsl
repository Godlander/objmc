//objmc
//https://github.com/Godlander/objmc

isCustom = 0;
int corner = gl_VertexID % 4;
ivec2 atlasSize = textureSize(Sampler0, 0);
vec2 onepixel = 1./atlasSize;
ivec2 uv = ivec2((UV0 * atlasSize));
vec3 posoffset = vec3(0);
vec3 rotation = vec3(0);
//read uv offset
ivec4 metauvoffset = ivec4(texelFetch(Sampler0, uv, 0) * 255);
ivec2 uvoffset = ivec2(metauvoffset.r*256 + metauvoffset.g,
                       metauvoffset.b+1); //no alpha due to optifine, max number of faces greatly limited (probably still a couple million more than needed)
//find and read topleft pixel
ivec2 topleft = uv - uvoffset;
//if topleft marker is correct
if (ivec4(texelFetch(Sampler0, topleft, 0)*255) == ivec4(12,34,56,78)) {
    isCustom = 1;
    //grab meta
    ivec4 meta = getmeta(topleft, 1);
    vec2 autorotate = vec2(getb(meta.r, 6), getb(meta.r, 5));
    noshadow = getb(meta.r, 7);
    //size
    ivec4 metasize = getmeta(topleft, 2);
    ivec2 size = ivec2(metasize.r*256 + metasize.g,
                       metasize.b*256 + metasize.a-128+geta(meta.a,6));
    //nvertices
    ivec4 metanvertices = getmeta(topleft, 3);
    int nvertices = metanvertices.r*16777216 + metanvertices.g*65536 + metanvertices.b*256 + metanvertices.a-128+geta(meta.a,5);
    //frames
    ivec4 metaanim = getmeta(topleft, 4);
    int nframes = clamp(metaanim.r, 1,255);
    int ntextures = clamp(metaanim.g, 1,255);
    float duration = float(metaanim.b + 1);
    bool autoplay = bool(getb(metaanim.a, 6));
    int easing = metaanim.a & 7;
    //data heights
    ivec4 metaheight = getmeta(topleft, 5);
    int vph = metaheight.r*256 + metaheight.g;
    int vth = metaheight.b*256 + metaheight.a-128+geta(meta.a,4);
    //time in ticks
    float time = GameTime * 24000;
    int tcolor = 0;
//colorbehavior
#ifdef ENTITY
    overlayColor = vec4(1);
    int colorbehavior = meta.b;
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
    time = autoplay ? time + (nframes*duration) - mod(tcolor, nframes*duration) : tcolor;
    int frame = int(time/duration) % nframes;
    //relative vertex id from unique face uv
    int id = (((uvoffset.y-1) * size.x) + uvoffset.x) * 4 + corner;
    id += frame * nvertices;
    //calculate height offsets
    int headerheight = 1 + int(ceil(nvertices*0.25/size.x));
    int height = headerheight + (size.y);
    //read data
    ivec2 index = getvert(topleft, size.x, height+vph+vth, id);
    posoffset = getpos(topleft, size.x, height, index.x);
    texCoord = getuv(topleft, size.x, height+vph, index.y) * size;
    if (nframes > 1 && easing > 0) {
        int nids = (nframes * nvertices);
        //next frame
        id = (id+nvertices) % nids;
        index = getvert(topleft, size.x, height+vph+vth, id);
        vec3 posoffset2 = getpos(topleft, size.x, height, index.x);
        //interpolate
        transition = fract(time/duration);
        switch (easing) { //easing
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
    isGUI = int(isgui(ProjMat));
    isHand = int(ishand(FogStart));
    if (any(greaterThan(autorotate,vec2(0))) && isGUI == 0) {
        //normal estimated rotation calculation from The Der Discohund
        vec3 local = IViewRotMat * Normal;
        float yaw = -atan(local.x, local.z);
        float pitch = -atan(local.y, length(local.xz));
        posoffset = rotate(vec3(vec2(pitch,yaw)*autorotate,0) + rotation) * posoffset * IViewRotMat;
    }
    //pure color rotation
    else if (isHand == 0) {
        posoffset = rotate(rotation) * posoffset * IViewRotMat;
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
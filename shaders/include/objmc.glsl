//objmc
//https://github.com/Godlander/objmc

//some basic data
int corner = gl_VertexID % 4;
ivec2 atlasSize = textureSize(Sampler0, 0);
vec2 onepixel = 1./atlasSize;
ivec2 uv = ivec2((UV0 * atlasSize));
vec3 posoffset = vec3(0);
vec3 rotation = vec3(0);
bool isCustom = false;
bool autorotate = false;
//read uv offset
ivec4 metauvoffset = ivec4(texelFetch(Sampler0, uv, 0) * 255);
ivec2 uvoffset = ivec2(metauvoffset.r*256 + metauvoffset.g,
                       metauvoffset.b*256 + metauvoffset.a);
//find and read topleft pixel
ivec2 topleft = uv - uvoffset;
ivec4 markerpix = ivec4(texelFetch(Sampler0, topleft, 0) * 255);
//if marker is correct at topleft
if (markerpix == ivec4(12,34,56,0)) {
    isCustom = true;
    //grab metadata: marker, size, nvertices, frames
    //size
    ivec4 metasize = ivec4(texelFetch(Sampler0, topleft + ivec2(1,0), 0) * 255);
    ivec2 size = ivec2(metasize.r*256 + metasize.g,
                       metasize.b*256 + metasize.a);
    //nvertices
    ivec4 metanvertices = ivec4(texelFetch(Sampler0, topleft + ivec2(2,0), 0) * 255);
    int nvertices = metanvertices.r*16777216 + metanvertices.g*65536 + metanvertices.b*256 + metanvertices.a;
    //frames
    ivec4 metaframes = ivec4(texelFetch(Sampler0, topleft + ivec2(3,0), 0) * 255);
    int nframes = max(metaframes.r, 1);
    int ntextures = max(metaframes.g, 1);
    float duration = float(metaframes.b + 1);
    //time in ticks
    float time = GameTime * 24000;

    //rotate
    ivec4 metarot = ivec4(texelFetch(Sampler0, topleft + ivec2(4,0), 0) * 255);
    autorotate = (metarot.r > 0);

    //colorbehavior
#ifdef ENTITY
    bool autoplay = (metarot.g > 0);
    int tcolor = 0;
    if (metaframes.a == 63) { //animation frames 0-8388607
        tcolor = (int(Color.r*255)*65536)%32768 + int(Color.g*255)*256 + int(Color.b*255);
        //interpolation enabled past 8388608, suso's idea to define starting tick with color
        autoplay = (Color.r > 0.5);
    } else {
        //bits from colorbehavior
        int rb = (metaframes.a/16)%4;
        int gb = (metaframes.a/4)%4;
        int bb = metaframes.a%4;
        vec3 accuracy = vec3(255./256.);
        switch (rb) {
            case 0: rotation.x += Color.r*255; accuracy.r *= 256; break;
            case 1: rotation.y += Color.r*255; accuracy.g *= 256; break;
            case 2: rotation.z += Color.r*255; accuracy.b *= 256; break;
            case 3: tcolor = tcolor * 256 + int(Color.r*255); break;
        }
        switch (gb) {
            case 0: rotation.x += Color.g*255; accuracy.r *= 256; break;
            case 1: rotation.y += Color.g*255; accuracy.g *= 256; break;
            case 2: rotation.z += Color.g*255; accuracy.b *= 256; break;
            case 3: tcolor = tcolor * 256 + int(Color.g*255); break;
        }
        switch (bb) {
            case 0: rotation.x += Color.b*255; accuracy.r *= 256; break;
            case 1: rotation.y += Color.b*255; accuracy.g *= 256; break;
            case 2: rotation.z += Color.b*255; accuracy.b *= 256; break;
            case 3: tcolor = tcolor * 256 + int(Color.b*255); break;
        }
        rotation = rotation/accuracy * 2*PI;
    }
    time = autoplay ? time + (nframes*duration) - mod(tcolor, nframes*duration) : tcolor;
#endif

    int frame = int(time/duration) % nframes;

    //calculate height offsets
    int headerheight = 1 + int(ceil(nvertices*0.25/size.x));
    int yoffset = headerheight + (ntextures * size.y);
    //relative vertex id from unique face uv
    int id = (((uvoffset.y-1) * size.x) + uvoffset.x) * 4 + corner;
    id += frame * nvertices;
    //read data
    //meta = rgba: textureid, easing, scale?, unused
    //position = xyz: rgb, rgb, rgb
    //normal = xyz: aaa of the prev pixels
    //uv = rg,ba
    vec4 datameta = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0);
    vec4 datax = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0);
    vec4 datay = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0);
    vec4 dataz = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0);
    vec4 datauv = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 4), 0);
    //position
    posoffset = vec3(
        ((datax.r*65536)+(datax.g*256)+(datax.b))/256,
        ((datay.r*65536)+(datay.g*256)+(datay.b))/256,
        ((dataz.r*65536)+(dataz.g*256)+(dataz.b))/256
    ) - 128.5;
    //normal
    normal = vec3(datax.a + int(datax.a == 0), datay.a + int(datay.a == 0), dataz.a + int(dataz.a == 0));
    //uv
    vec2 texuv1 = vec2(
        ((datauv.r*256) + datauv.g)/256 * (size.x-(size.x/256.)),
        ((datauv.b*256) + datauv.a)/256 * (size.y-(size.y/256.))
    );

    int easing = int(datameta.g * 255);
    if (nframes > 1) {
        //next frame
        id = (id + nvertices) % (nframes * nvertices);
        vec4 datameta2 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0);
        vec4 datax2 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0);
        vec4 datay2 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0);
        vec4 dataz2 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0);
        vec4 datauv2 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 4), 0);
        //position
        vec3 posoffset2 = vec3(
            ((datax2.r*65536)+(datax2.g*256)+(datax2.b))/256,
            ((datay2.r*65536)+(datay2.g*256)+(datay2.b))/256,
            ((dataz2.r*65536)+(dataz2.g*256)+(dataz2.b))/256
        ) - 128.5;
        //normal
        vec3 norm2 = vec3(datax2.a + int(datax2.a == 0), datay2.a + int(datay2.a == 0), dataz2.a + int(dataz2.a == 0));
        //uv
        //vec2 texuv2 = vec2(
        //    ((datauv.r*256) + datauv.g)/atlasSize.x/256*size.x,
        //    ((datauv.b*256) + datauv.a)/atlasSize.y/256*size.y
        //);
        //texCoord02 = (vec2(topleft.x, topleft.y+headerheight)/atlasSize) + texuv2;

        transition = fract(time/duration);
        switch (easing) {
            case 1: //linear
                posoffset = mix(posoffset, posoffset2, transition);
                normal = mix(normal, norm2, transition);
                break;
            case 2: //in-out cubic
                transition = transition < 0.5 ? 4 * transition * transition * transition : 1 - pow(-2 * transition + 2, 3) * 0.5;
                posoffset = mix(posoffset, posoffset2, transition);
                normal = mix(normal, norm2, transition);
                break;
            case 3: //4-point bezier
                //third point
                id = (id + nvertices) % (nframes * nvertices);
                vec4 datameta3 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0);
                vec4 datax3 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0);
                vec4 datay3 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0);
                vec4 dataz3 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0);
                vec3 posoffset3 = vec3(
                    ((datax3.r*65536)+(datax3.g*256)+(datax3.b))/256,
                    ((datay3.r*65536)+(datay3.g*256)+(datay3.b))/256,
                    ((dataz3.r*65536)+(dataz3.g*256)+(dataz3.b))/256
                ) - 128.5;
                vec3 norm3 = vec3(datax3.a + int(datax3.a == 0), datay3.a + int(datay3.a == 0), dataz3.a + int(dataz3.a == 0));
                //fourth point
                id = (id + nvertices) % (nframes * nvertices);
                vec4 datameta4 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0);
                vec4 datax4 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0);
                vec4 datay4 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0);
                vec4 dataz4 = texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0);
                vec3 posoffset4 = vec3(
                    ((datax4.r*65536)+(datax4.g*256)+(datax4.b))/256,
                    ((datay4.r*65536)+(datay4.g*256)+(datay4.b))/256,
                    ((dataz4.r*65536)+(dataz4.g*256)+(dataz4.b))/256
                ) - 128.5;
                vec3 norm4 = vec3(datax4.a + int(datax4.a == 0), datay4.a + int(datay4.a == 0), dataz4.a + int(dataz4.a == 0));
                //bezier
                posoffset = bezier(posoffset, posoffset2, posoffset3, posoffset4, transition);
                normal = bezier(normal, norm2, norm3, norm4, transition);
                break;
        }
    }
    //normalize normal
    normal = normalize(normal);

    //real uv
                //align uv to pixel
    texCoord0 = (vec2(topleft.x, topleft.y+headerheight) + texuv1)/atlasSize
                //make sure that faces with same uv beginning/ending renders
                + vec2(onepixel.x * 0.0001 * corner, onepixel.y * 0.0001 * ((corner + 1) % 4));
}
//debug
//else {
//    posoffset = vec3(gl_VertexID % 4 - 2, gl_VertexID % 4 / 2 * 2, -(gl_VertexID % 4) + 2 * 2);
//    vertexColor = vec4(1.0,0.0,0.0,1.0);
//}
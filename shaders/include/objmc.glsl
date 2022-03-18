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
                       metauvoffset.b+1); //no alpha due to optifine, number of faces greatly limited (but still probably a couple million more than needed)
//find and read topleft pixel
ivec2 topleft = uv - uvoffset;
ivec4 markerpix = ivec4(texelFetch(Sampler0, topleft, 0) * 255);
//if marker is correct at topleft
if (markerpix == ivec4(12,34,56,78)) {
    isCustom = true;
    //grab metadata: marker, behavior&alpha, size, nvertices, frames
    //behavior and alpha
    ivec4 metaba = ivec4(texelFetch(Sampler0, topleft + ivec2(1,0), 0) * 255);
    //size
    ivec4 metasize = ivec4(texelFetch(Sampler0, topleft + ivec2(2,0), 0) * 255);
    ivec2 size = ivec2(metasize.r*256 + metasize.g,
                       metasize.b*256 + metasize.a-128+(((metaba.a>>6)&1)<<7));
    //nvertices
    ivec4 metanvertices = ivec4(texelFetch(Sampler0, topleft + ivec2(3,0), 0) * 255);
    int nvertices = metanvertices.r*16777216 + metanvertices.g*65536 + metanvertices.b*256 + metanvertices.a-128+(((metaba.a>>5)&1)<<7);
    //frames
    ivec4 metaframes = ivec4(texelFetch(Sampler0, topleft + ivec2(4,0), 0) * 255);
    int nframes = max(metaframes.r, 1);
    int ntextures = max(metaframes.g, 1);
    float duration = float(metaframes.b + 1);
    //time in ticks
    float time = GameTime * 24000;

//colorbehavior
#ifdef ENTITY
    autorotate = (metaba.r > 0);
    bool autoplay = (metaba.g > 0);
    int tcolor = 0;
    if (metaba.b == 63) { //animation frames 0-8388607
        tcolor = (int(Color.r*255)*65536)%32768 + int(Color.g*255)*256 + int(Color.b*255);
        //interpolation enabled past 8388608, suso's idea to define starting tick with color
        autoplay = (Color.r > 0.5);
    } else {
        //bits from colorbehavior
        int rb = (metaba.b/16)%4;
        int gb = (metaba.b/4)%4;
        int bb = metaba.b%4;
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

    //calculate height offsets
    int headerheight = 1 + int(ceil(nvertices*0.25/size.x));
    int yoffset = headerheight + (ntextures * size.y);
    //relative vertex id from unique face uv
    int id = (((uvoffset.y-1) * size.x) + uvoffset.x) * 4 + corner;
    //frame offset
    int frame = int(time/duration) % nframes;
    id += frame * nvertices;
    //read data
    //meta = rgba: textureid, easing, scale?, unused
    //position = xyz: rgb, rgb, rgb 3 pixels
    //normal = xyz: aaa of prev 3 pixels, with first bit in meta pixel
    //uv = rg,ba of next two pixels, with first bit of alpha in meta pixel
    ivec4 datameta = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0) * 255);
    ivec4 datax = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0) * 255);
    ivec4 datay = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0) * 255);
    ivec4 dataz = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0) * 255);
    ivec4 datauv = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 4), 0) * 255);
    //position
    posoffset = vec3(
        ((datax.r*65536)+(datax.g*256)+(datax.b))/256./255.,
        ((datay.r*65536)+(datay.g*256)+(datay.b))/256./255.,
        ((dataz.r*65536)+(dataz.g*256)+(dataz.b))/256./255.
    ) - vec3(128.5, 128.0, 128.5);
    //normal
    normal = vec3(
        (datax.a-128+(((datameta.a>>3)&1)<<7))/255.,
        (datay.a-128+(((datameta.a>>2)&1)<<7))/255.,
        (dataz.a-128+(((datameta.a>>1)&1)<<7))/255.
    );
    //uv
    vec2 texuv1 = vec2(
        ((datauv.r*256) + datauv.g)/255. * (size.x-(size.x/256.))/256.,
        ((datauv.b*256) + (datauv.a-128+((datameta.a&1)<<7)))/255. * (size.y-(size.y/256.))/256.
    );

    if (nframes > 1) {
        //next frame
        id = (id + nvertices) % (nframes * nvertices);
        ivec4 datameta2 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0) * 255);
        ivec4 datax2 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0) * 255);
        ivec4 datay2 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0) * 255);
        ivec4 dataz2 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0) * 255);
        ivec4 datauv2 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 4), 0) * 255);
        //position
        vec3 posoffset2 = vec3(
            ((datax2.r*65536)+(datax2.g*256)+(datax2.b))/256./255.,
            ((datay2.r*65536)+(datay2.g*256)+(datay2.b))/256./255.,
            ((dataz2.r*65536)+(dataz2.g*256)+(dataz2.b))/256./255.
        ) - vec3(128.5, 128.0, 128.5);
        //normal
        vec3 norm2 = vec3(
            (datax2.a-128+(((datameta2.a>>3)&1)<<7))/255.,
            (datay2.a-128+(((datameta2.a>>2)&1)<<7))/255.,
            (dataz2.a-128+(((datameta2.a>>1)&1)<<7))/255.
        );
        //uv
        //vec2 texuv2 = vec2(
        //    ((datauv2.r*256) + datauv2.g)/256 * (size.x-(size.x/256.)),
        //    ((datauv2.b*256) + datauv2.a & ((datameta.a&1)<<7))/256 * (size.y-(size.y/256.))
        //);
        //texCoord02 = (vec2(topleft.x, topleft.y+headerheight)/atlasSize) + texuv2;

        transition = fract(time/duration);
        switch (datameta.g) { //easing
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
                ivec4 datameta3 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0) * 255);
                ivec4 datax3 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0) * 255);
                ivec4 datay3 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0) * 255);
                ivec4 dataz3 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0) * 255);
                //position
                vec3 posoffset3 = vec3(
                    ((datax3.r*65536)+(datax3.g*256)+(datax3.b))/256./255.,
                    ((datay3.r*65536)+(datay3.g*256)+(datay3.b))/256./255.,
                    ((dataz3.r*65536)+(dataz3.g*256)+(dataz3.b))/256./255.
                ) - vec3(128.5, 128.0, 128.5);
                //normal
                vec3 norm3 = vec3(
                    (datax3.a-128+(((datameta3.a>>3)&1)<<7))/255.,
                    (datay3.a-128+(((datameta3.a>>2)&1)<<7))/255.,
                    (dataz3.a-128+(((datameta3.a>>1)&1)<<7))/255.
                );
                //fourth point
                id = (id + nvertices) % (nframes * nvertices);
                ivec4 datameta4 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 0), 0) * 255);
                ivec4 datax4 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 1), 0) * 255);
                ivec4 datay4 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 2), 0) * 255);
                ivec4 dataz4 = ivec4(texelFetch(Sampler0, getp(topleft, size, yoffset, id, 3), 0) * 255);
                vec3 posoffset4 = vec3(
                    ((datax4.r*65536)+(datax4.g*256)+(datax4.b))/256./255.,
                    ((datay4.r*65536)+(datay4.g*256)+(datay4.b))/256./255.,
                    ((dataz4.r*65536)+(dataz4.g*256)+(dataz4.b))/256./255.
                ) - vec3(128.5, 128.0, 128.5);
                vec3 norm4 = vec3(
                    (datax4.a-128+(((datameta4.a>>3)&1)<<7))/255.,
                    (datay4.a-128+(((datameta4.a>>2)&1)<<7))/255.,
                    (dataz4.a-128+(((datameta4.a>>1)&1)<<7))/255.
                );
                //bezier
                posoffset = bezier(posoffset, posoffset2, posoffset3, posoffset4, transition);
                normal = bezier(normal, norm2, norm3, norm4, transition);
                break;
        }
    }
    //normalize normal
    normal = normalize(normal);

//entity rotation/lighting rendering
#ifdef ENTITY
    bool isGUI = isgui(ProjMat);
    bool isHand = ishand(FogStart);
    //flip shading in gui bcos light goes the other way
    if (isGUI) {normal.xz = -normal.xz;}
    //normal estimated rotation matrix calculation from The Der Discohund
    else if (autorotate) {
        normal = inverse(IViewRotMat) * normal;
        vec3 localZ = IViewRotMat * Normal;
        vec3 localX = normalize(cross(vec3(0, 1, 0), localZ));
        vec3 localY = cross(localZ, localX);
        mat3 localRot = mat3(localX, localY, localZ);
        posoffset = inverse(IViewRotMat) * rotate(rotation) * localRot * posoffset;
    }
    //pure color rotation
    else if (!isHand) {
        normal = inverse(IViewRotMat) * normal;
        posoffset = inverse(IViewRotMat) * rotate(rotation) * posoffset;
    }
    //custom shading
    vertexColor = minecraft_mix_light(Light0_Direction, Light1_Direction, normal, vec4(1));
#endif

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
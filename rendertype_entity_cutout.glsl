#version 440

#moj_import <light.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;
in vec3 Normal;

uniform sampler2D Sampler0;
uniform sampler2D Sampler2;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform mat3 IViewRotMat;
uniform float GameTime;

uniform vec3 Light0_Direction;
uniform vec3 Light1_Direction;

out float vertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
out vec4 normal;

ivec2 getp(ivec2 tl, ivec2 size, int y, int index, int offset) {
    int i = (index * 5) + offset;
    return tl + ivec2(i % size.x, int(i / size.x) + y);
}

void main() {
    //default
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);
    vertexDistance = length((ModelViewMat * vec4(Position, 1.0)).xyz);
    vertexColor = Color * minecraft_sample_lightmap(Sampler2, UV2);
    normal = ProjMat * ModelViewMat * vec4(Normal, 0.0);
    texCoord0 = UV0;

    //some basic data
    int corner = gl_VertexID % 4;
    ivec2 atlasSize = textureSize(Sampler0, 0);
    vec2 onepixel = 1./atlasSize;
    ivec2 uv = ivec2((UV0 * atlasSize));
    vec3 posoffset = vec3(0.0);
    //read uv offset
    vec4 metauvoffset = texelFetch(Sampler0, uv, 0) * 255;
    ivec2 uvoffset = ivec2(int(metauvoffset.r*256) + int(metauvoffset.g),
                           int(metauvoffset.b*256) + int(metauvoffset.a));
    //find and read topleft pixel
    ivec2 topleft = uv - uvoffset;
    vec4 markerpix = texelFetch(Sampler0, topleft, 0);
    //if marker is correct at topleft
    if (floor(markerpix * 255) == vec4(12,34,56,0)) {
///*
        //grab metadata: marker, size, nvertices, nframes
        //size
        vec4 metasize = texelFetch(Sampler0, topleft + ivec2(1,0), 0) * 255;
        ivec2 size = ivec2(int(metasize.r)*256 + int(metasize.g), int(metasize.b)*256 + int(metasize.a));
        //nvertices
        vec4 metanvertices = texelFetch(Sampler0, topleft + ivec2(2,0), 0) * 255;
        int nvertices = int(metanvertices.r)*16777216 + int(metanvertices.g)*65536 + int(metanvertices.b)*256 + int(metanvertices.a);
        //nframes
        vec4 metanframes = texelFetch(Sampler0, topleft + ivec2(3,0), 0) * 255;
        int nframes = int(metanframes.a);

        //calculate height offsets
        int headerheight = 1 + int((nvertices/4./size.x)+0.9999);
        int yoffset = headerheight + (size.y * nframes);
        //relative vertex id from unique face uv
        int id = (((uvoffset.y-1) * size.y) + uvoffset.x) * 4 + corner;

        //read data
        //meta = rgba: scale, hasnormal, easing, unused
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
            ((datax.r*255*256)+(datax.g*256)+(datax.b))/256,
            ((datay.r*255*256)+(datay.g*256)+(datay.b))/256,
            ((dataz.r*255*256)+(dataz.g*256)+(dataz.b))/256
        ) - vec3(2.36, 1.5, 2.36);
        //normal
        vec3 norm = vec3(datax.a, datay.a, dataz.a);
        //uv
        vec2 texuv = vec2(
            ((datauv.r*256) + datauv.g)/atlasSize.x/256*size.x,
            ((datauv.b*256) + datauv.a)/atlasSize.y/256*size.y
        );
//*/
        //real uv
        texCoord0 = (vec2(topleft.x, topleft.y+headerheight)/atlasSize) + texuv;
        //shading from normal
        normal = vec4(normalize(norm), 0.0);
        vertexColor = vec4(vec3(max(dot(norm * IViewRotMat, Light0_Direction), 0.0)), 1.0);
        vertexColor *= vec4(vec3(max(dot(norm * IViewRotMat, Light1_Direction), 0.0)), 1.0);
        vertexColor += 0.4;
        vertexColor *= minecraft_sample_lightmap(Sampler2, UV2);
    }
    gl_Position = ProjMat * ModelViewMat * (vec4(Position + (inverse(IViewRotMat) * posoffset), 1.0));
}
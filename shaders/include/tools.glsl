//objmc
//https://github.com/Godlander/objmc

bool isgui(mat4 ProjMat) {
    return ProjMat[3][2] == -2.0;
}

ivec2 getp(ivec2 topleft, ivec2 size, int yoffset, int index, int offset) {
    int i = (index * 5) + offset;
    return topleft + ivec2(i % size.x, int(i / size.x) + yoffset);
}
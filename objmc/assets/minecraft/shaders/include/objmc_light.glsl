//objmc
//https://github.com/Godlander/objmc

//default lighting
if (isCustom == 0) {color *= vertexColor;}
//custom lighting
else if (noshadow == 0) {
    //normal from position derivatives
    vec3 normal = normalize(cross(dFdx(Pos), dFdy(Pos)));

    //block lighting
    #ifdef BLOCK
    color *= vec4(vec3(clamp(dot(normal, vec3(0.2,1,0)) * 0.5 + 0.6, 0.1,1)), 1.0);
    #endif

    //entity lighting
    #ifdef ENTITY
    //flip normal for gui
    if (isGUI == 1) normal.xz = -normal.xz;
    color *= minecraft_mix_light(Light0_Direction, Light1_Direction, normal, overlayColor);
    #endif
}
color *= lightColor * ColorModulator;
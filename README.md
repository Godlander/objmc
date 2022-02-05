# usage:

make sure Python and Pillow is installed, and place the script in the same directory as the input obj and texture files.

after editing the script with your inputs, run `python convert.py` in command line to generate the model and texture output to go in a resourcepack.

place the shaders in the correct location in the resourcepack, and any model generated with this tool should display properly.

make sure your minecraft version is vanilla 1.18.1. the shader will not work with older versions, and any mods that change rendering (Optifine, Sodium, etc) will likely be incompatible with core shaders.

### script inputs

`objs`: array of string names of obj files in the same folder to read. these must have same number of vertices if used in same animation.

`frames`: array of strings of digits defining which index of the obj to use as each frame.

`texs`: array of one single name of the texture file.

### script output

`output`: array of two string file names: the json model, and the texture.

### advanced/animation:

`duration`: integer duration of frames in ticks.

`easing`: interpolation method shader uses inbetween frames. 0: none, 1: linear, 2: cubic

for custom entity model rotation and controllable animation to work, the model has to be a Potion item (can use `CustomModelData`).

the `CustomPotionColor` R,G,B values defines the X,Y,Z rotation of the model or the animation time, depending on what `colorbehavior` is set to in the Python script as you exported the texture.

`autorotate` can be used to make shader estimate rotation from Normals instead of defining it by color. due to inaccuracy this will be jittery and look bad when closeup. but for far away things it looks ok, and allows color to be used for other input like controlling animation.

# samples:

![teapot](https://user-images.githubusercontent.com/16228717/151483908-2238f6f9-44c7-434b-a411-f9959bf86a3e.gif)

![cat](https://user-images.githubusercontent.com/16228717/148311540-503cf422-b6c7-4c95-b4b4-fca1e136dbfe.png)

![cube](https://user-images.githubusercontent.com/16228717/148442834-78e49a63-c5f8-4668-a822-dcd11d215618.png)

![robo](https://user-images.githubusercontent.com/16228717/148869708-310e7ec4-7d89-40e8-8fc6-38d2e6116cb7.png)

![ring](https://user-images.githubusercontent.com/16228717/149825494-cd51146e-38ed-48a5-a47a-0c2fce678d1a.gif)

![image](https://user-images.githubusercontent.com/16228717/149994828-d285f81d-b213-4057-bfbf-288c02891011.png)

# random notes about the tool

### general output format:

this is just a reference, actual format may change as i add/change stuff

![image](https://user-images.githubusercontent.com/16228717/148311479-0cade68e-dab8-491b-83fb-f7d22c78bd1b.png)

### flipped uv

the uv ends up being upside down for some reason when exporting from Blockbench. idk why, so i just flip the texture while encoding to compensate.

this doesnt seem to happen through Blender tho

### versioning

due to me changing stuff, different versions of the objmc shader may only work with the script texture/model outputs of that specific version. if stuff breaks make sure to double check that you have the latest version of both the shader as well as the script output.

### gltf animation to obj per frame

Blockbench exports animations to gltf format, which objmc doesn't support

you can import gltf format into blender and then export as waveform .obj, check the animation checkbox when exporting to generate .obj files per frame of the animation.

by default blender outputs a lot more frames than you will likely need, especially since objmc shader does interpolation between the frames. you can change the time stretching and frame range in blender to be lower to potentially decrease file size by a lot

![image](https://user-images.githubusercontent.com/16228717/151484572-927dd40b-bd5d-4046-bb09-2cdf7ae23cf9.png)


### vertex id

Minecraft's `gl_VertexID` isn't per model, so it's difficult to find the relative id of a vertex in a model unless you have a constant number of vertices

i thought up a trick to assign each face a unique pixel uv, then encoding the offset of the pixel from top left (relative 0,0 in the texture, some random place in the atlas)

with the offset data i am able to calculate the relative face id, and `gl_VertexID % 4` gives the corner.

![image](https://user-images.githubusercontent.com/16228717/148311858-3bd76267-f80f-4ad6-84c3-3b5f6760bcf4.png)

### preserving rgb

basically anything to do with images in js does alpha premultiplying, which ruins rgb values when alpha is anything less than 255. afaik only way to not suffer this is to directly interact with the raw file instead of as an image. so if you wanted to send an image with alpha to someone over discord or something, don't send it as an image. instead, you can zip it and send the zip to preserve data, or just change the file extension so discord treats it as some unknown file.

### questions

feel free to contact me on any of the linked social media icons in my github profile readme.

# contributors:

**DartCat25** - Helped me get started

**Dominexus** - Help with spline math

**Onnowhere** - Help with formatting decisions

**Suso** - Idea for controlled interpolated animation

**The Der Discohund** - Help with matrix operations

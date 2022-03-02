# usage:
make sure Python and Pillow is installed, and place the script in the same directory as the input obj and texture files.

after editing the script with your inputs, run `python convert.py` in command line to generate the model and texture output to go in a resourcepack.

place the shaders in the correct location in the resourcepack, and any model generated with this tool should display properly.

make sure your minecraft version is vanilla 1.18.2. the shader will not work with older versions, and any mods that change rendering (Optifine, Sodium, etc) will likely be incompatible with objmc core shaders.

### script inputs
`objs`: array of string names of obj files in the same folder to read. these must have same number of vertices if used in same animation.

`frames`: array of strings of digits defining which index of the obj to use as each frame.

`texs`: array of one single name of the texture file. the minimum size is 8x8, but a larger texture is recommended if model has a lot of vertices or is animated.

### script output
`output`: array of two string file names: the json model, and the texture.

### advanced/animation:
`offset` and `scale`: just adds & multiplies vertex positions before encoding, so you dont have to re-export the model.

`duration`: integer duration of each frame in ticks.

`easing`: interpolation method shader uses inbetween frames. 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier

`flipuv`: if your model renders but doesn't look right, try toggling this. see [#flipped-uv](#flipped-uv).

*for custom entity model rotation and controllable animation to work, the model has to be an item with overlay color, like Potion or dyed Leather Armor (can use `CustomModelData`).*

`colorbehavior`: the overlay color of the item r,g,b defines the x,y,z rotation of the model or the animation time, depending on what this is set to in the Python script as you exported the texture.

`autorotate` can be used to make shader estimate rotation from Normals instead of defining it by color. due to inaccuracy this will be jittery and look bad when closeup. but for far away things it looks ok, and allows color to be used for other input like controlling animation.

`autoplay` will make the animation continuously play, color can still be used to define the starting frame. `colorbehavior = 'aaa'` will override this.

# samples:
![teapot](https://user-images.githubusercontent.com/16228717/151483908-2238f6f9-44c7-434b-a411-f9959bf86a3e.gif)

![cat](https://user-images.githubusercontent.com/16228717/148311540-503cf422-b6c7-4c95-b4b4-fca1e136dbfe.png)

![cube](https://user-images.githubusercontent.com/16228717/148442834-78e49a63-c5f8-4668-a822-dcd11d215618.png)

![robo](https://user-images.githubusercontent.com/16228717/148869708-310e7ec4-7d89-40e8-8fc6-38d2e6116cb7.png)

![room](https://user-images.githubusercontent.com/16228717/155235807-250932d3-0ffd-43ca-92c8-3112df12a64e.png)

# faqs / random notes about the tool

### general output format
this is just a reference, actual format may change as i add/change stuff

![image](https://user-images.githubusercontent.com/16228717/148311479-0cade68e-dab8-491b-83fb-f7d22c78bd1b.png)

### model not rendering
most of the time this is due to an error in your resourcepack. make sure the shaders are in the correct place, double check the file paths for model and texture (by default model will point to the root textures folder, not textures/block or textures/items), try using latest version of objmc script and shader if you have an older version.

### flipped uv
the uv ends up being upside down for some reason when exporting from Blockbench. idk why, so i just flip the texture while encoding to compensate.

this doesnt seem to happen through Blender tho.

### preserving rgb
basically anything to do with images in js does alpha premultiplying, which ruins rgb values when alpha is anything less than 255. afaik only way to not suffer this is to directly interact with the raw file instead of as an image. so if you wanted to send an image with alpha to someone over discord or something, don't send it as an image. instead, you can change the file extension so discord treats it as some unknown file, or zip it and send the zip to preserve data.

### versioning
due to me changing stuff, different versions of the objmc shader may only work with the script texture/model outputs of that specific version.

but also due to me changing stuff a lot i'm too lazy to try to give this a proper versioning system.

if stuff breaks make sure to double check that you have the latest version of both the shader as well as the script output.

### multiple textures
there is no support for stitching multiple textures. you will have to use another program like blender to bake them onto one texture along with the neccesary uv changes on the model itself.

### gltf animation to obj per frame
Blockbench exports animations to gltf format, which objmc doesn't support

you can import gltf format into blender and then export as waveform .obj, check the animation checkbox when exporting to generate .obj files per frame of the animation.

by default blender outputs a lot more frames than you will likely need, especially since objmc shader does interpolation between the frames. you can change the time stretching and frame range in blender to be lower to potentially decrease file size by a lot

![image](https://user-images.githubusercontent.com/16228717/151484572-927dd40b-bd5d-4046-bb09-2cdf7ae23cf9.png)

in the sample teapot animation, i only exported every 5th frame, and the animation still looks good enough

### vertex id
Minecraft's `gl_VertexID` isn't per model, so it's difficult to find the relative id of a vertex in a model unless you have a constant number of vertices

i came up with a method to assign each face a unique uv pointing to a pixel in the 'header' of the texture, then encoding the offset of the pixel from top left (relative 0,0 in the texture, some random place in the atlas) as color of the pixel. this also lets vertex know where top left corner of the texture is in the atlas.

with the offset data i am able to calculate the relative face id, and `gl_VertexID % 4` gives the corner.

![image](https://user-images.githubusercontent.com/16228717/148311858-3bd76267-f80f-4ad6-84c3-3b5f6760bcf4.png)

in the image, the first 6 faces are selected, and their uv is shown highlighted in blockbench uv editor

### head Pose
function to convert head Pose to Potion color rgb
```mcfunction
execute store result score r temp run data get entity @s Pose.Head[0] 0.708333333
execute store result score g temp run data get entity @s Pose.Head[1] 0.708333333
execute store result score b temp run data get entity @s Pose.Head[2] 0.708333333

scoreboard players add r temp 256
scoreboard players operation r temp %= 256 const
scoreboard players add g temp 256
scoreboard players operation g temp %= 256 const
scoreboard players add b temp 256
scoreboard players operation b temp %= 256 const

scoreboard players operation rgb temp = r temp
scoreboard players operation rgb temp *= 256 const
scoreboard players operation rgb temp += g temp
scoreboard players operation rgb temp *= 256 const
scoreboard players operation rgb temp += b temp

execute store result entity @s ArmorItems[3].tag.CustomPotionColor int 1 run scoreboard players get rgb temp
```

### questions
feel free to contact me on any of the linked social media icons in my github profile readme.

# contributors:
**DartCat25** - Helped me get started

**The Der Discohund** - Help with matrix operations

**Onnowhere** - Help with formatting decisions

**Suso** - Idea for controlled interpolated animation

**Dominexus** - Help with spline math

**Barf Creations** - Help replicating Minecraft's jank Pose rotation matrix

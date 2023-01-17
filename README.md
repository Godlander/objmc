i cannot guarantee modded compatibility. core shaders are a vanilla resourcepack feature, if a mod breaks a vanilla feature i cant do anything.

# usage:
make sure Python and Pillow is installed, and place the script in the same directory as the input obj and texture files.

either edit the script with your inputs, or run `python objmc.py` with correct arguments in command line to generate the model and texture outputs that go in a resourcepack.

running the script without any arguments will open a gui with slightly more limited options.

![image](https://user-images.githubusercontent.com/16228717/181353217-5a7af1e3-cb9b-44a2-8fe1-18b12d14c441.png)

place the model and texture output generated with this tool in the correct location in the resourcepack along with the shaders folder, and should display properly.

make sure your minecraft version is 1.18.1+ as the shader will not work with lower versions.

### script inputs
`objs`: array of string names of obj files in the same folder to read. these must have same number of vertices if used in same animation.

`frames`: array of strings of digits defining which index of the obj to use as each frame.

`texs`: array of one single name of the texture file. the minimum size is 8x8, but a larger texture is recommended if model has a lot of vertices or is animated.

### script output
`output`: array of two string file names: the json model, and the texture.

### advanced:
`offset` and `scale`: just adds & multiplies vertex positions before encoding, so you dont have to re-export the model.

`duration`: integer duration of each frame in ticks.

`noshadow`: disable shading the model based on face normals.

`easing`: interpolation method shader uses inbetween frames. 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier.

`flipuv`: if your model renders but doesn't look right, try toggling this. see [#flipped-uv](#flipped-uv).

*for custom entity model rotation and controllable animation to work, the model has to be an item with overlay color, like Potion or dyed Leather Armor (can use `CustomModelData`).*

`colorbehavior`: defines the behavior of each byte of the overlay color of the item r,g,b. x: pitch rotation, y: yaw rotation, z: roll rotation, t: animation time offset, o: overlay color hue.

*example: `xto` defines 1 byte of red color as yaw rotation, the next byte of blue color as animation time offset , and the last byte of green being overlay color hue.*

`autorotate`: tells the shader to estimate rotation from Normals instead of defining it by color. due to byte inaccuracy this will be a little jittery. allows color to be used for other inputs like controlling animation.

`autoplay`: make the animation continuously play, color can still be used to define the starting frame. `colorbehavior = 'ttt'` will override this.

`visibility`: 3 bit number, defines where a model is visible. 1: in gui, 2: in first person hand, 4: in world. (7 would mean visible everywhere.) models with limited visibility can be joined together allowing for different models to show up in different places.

`join`: used by itself to combine generated models. `--join model1.json model2.json` will combine the two or more models into one. the textures still need to be placed in the right paths for all of the models.

The script can be run with arguments to each of these. Example:

```py
python objmc.py --objs cube.obj --texs cube.png --autorotate --flipuv --out potion.json texture.png
```



# samples:

https://user-images.githubusercontent.com/16228717/177398816-cf919f1d-8de1-4346-9024-068c48f47cbf.mp4

![teapot](https://user-images.githubusercontent.com/16228717/151483908-2238f6f9-44c7-434b-a411-f9959bf86a3e.gif)

![cat](https://user-images.githubusercontent.com/16228717/148311540-503cf422-b6c7-4c95-b4b4-fca1e136dbfe.png)

![cube](https://user-images.githubusercontent.com/16228717/148442834-78e49a63-c5f8-4668-a822-dcd11d215618.png)

![robo](https://user-images.githubusercontent.com/16228717/148869708-310e7ec4-7d89-40e8-8fc6-38d2e6116cb7.png)

![room](https://user-images.githubusercontent.com/16228717/155235807-250932d3-0ffd-43ca-92c8-3112df12a64e.png)

# faqs / random notes about the tool

### general output format
this is just a reference, actual format may change as i add/change stuff.

![image](https://user-images.githubusercontent.com/16228717/148311479-0cade68e-dab8-491b-83fb-f7d22c78bd1b.png)

### modded compatibility
item/entity models mostly work with both optifine and sodium.

the main difference is that pixels in texture with alpha < 0.1 (25.6) are simply discarded and become rgba(0,0,0,0).

to circumvent this i shift the first bit of all alpha values onto some other pixel. if the first bit is always 1 then alpha is guaranteed to be >= 0.5 (128)

placed block models may not work, entity models will render fine.

sodium users might expect incompatibility in the future:

![image](https://user-images.githubusercontent.com/16228717/161360296-c5883d7c-c33f-4aa0-bc25-e1360f2f2eca.png)

### performance
objmc models do not run much extra calculation. mostly a few extra texture fetches, but there should not be a noticeable performance difference to default minecraft.

if you make a model with 6 faces, you can expect it to perform similarly to a normal cube model.

thus, performance optimization is largely on the user to optimize the face count of the input model.

a zombie has a model with 6 elements each with 6 faces. a objmc entity model with 20k faces should expect similar performance to rendering 556 NoAI zombies on the screen. similarly, a objmc block model with 20k faces should expect similar performance to rendering 3333 blocks on screen, *without any culling*.

### model not rendering
most of the time this is due to an error in your resourcepack. make sure the shaders are in the correct place, double check the file paths for model and texture (by default model will point to the root textures folder, not textures/block or textures/items), try using latest version of objmc script and shader if you have an older version.

### flipped uv
the uv ends up being upside down sometimes for some reason when exporting from Blockbench. idk why, so i just flip the texture while encoding to compensate.

this doesnt seem to happen through Blender tho.

### controlling animation

any bits declared as `t` in `colorbehavior` will act as a time offset in ticks from 0 if `autoplay` is off, or from the current tick if `autoplay` is on.

to calculate the offset for a frame while using `autoplay`, you can use this formula:

```
((([/time query gametime] % 24000) - starting frame) % total duration)
```

if `colorbehavior` is set to `ttt`, autoplay is automatically on. instead, numbers past 8388608 define the paused frame to display (8388608 + paused frame to show).

### spawner models
you use spawners as a block that uses the entity renderer but isn't an entity. they are considerably laggier than normal blocks, but still better than entities, and don't suffer unloading nearly as much.
```mcfunction
setblock ~ ~ ~ minecraft:spawner{MaxNearbyEntities:0,RequiredPlayerRange:0,SpawnData:{entity:{id:"minecraft:armor_stand",ShowArms:0b,Small:1b,Invisible:1b,Pose:{Head:[30f,0f,0f]},ArmorItems:[{},{},{},{id:"minecraft:potion",Count:1b,tag:{CustomModelData:1,CustomPotionColor:0}}]}}}
```

### multiple textures
there is no support for stitching multiple textures. you will have to use another program like blender to bake them onto one texture along with the neccesary uv changes on the model itself.

https://github.com/Grim-es/material-combiner-addon is a blender addon that can combine multiple textures into an atlas.

### gltf animation to obj per frame
Blockbench exports animations to gltf format, which objmc doesn't support.

you can import gltf format into blender and then export as waveform .obj, check the animation checkbox when exporting to generate .obj files per frame of the animation.

by default blender outputs a lot more frames than you will likely need, especially since objmc shader does interpolation between the frames. you can change the time stretching and frame range in blender to be lower to potentially decrease file size by a lot.

![image](https://user-images.githubusercontent.com/16228717/151484572-927dd40b-bd5d-4046-bb09-2cdf7ae23cf9.png)

in the sample teapot animation, i only exported every 5th frame, and the animation still looks good enough.

### model unloading

block models unload when its more than 1 subchunk away directly behind the player. that means objmc can be used in 16x16x16 block sized subchunks if a map is entirely modeled.

entity models stay loaded in front of the player just as well as blocks but unloads instantly if their hitbox is not on screen.

*leashed entities become linked, and unrender when both of their hitboxes are no longer on screen.*

spawner models also unload 1 subchunk away behind but unload 8 subchunks away in front of the player, basically making render distance 8 regardless of real setting.

### items with overlay color

these items have custom rgb tint overlay that can be used to pass data:

`potion`, `splash_potion`, `lingering_potion`, `leather_helmet`, `leather_chestplate`, `leather_leggings`, `leather_boots`, `leather_horse_armor`, `firework_star`, `filled_map`

### vertex count limits

there appears to be a hard vertex count limit per chunk in Minecraft for blocks, and exceeding that instantly crashes the game, regardless of whether your computer can handle rendering that many faces, with a crash message similar to this:
```
java.lang.IllegalArgumentException: newLimit > capacity: (151999848 > 37748736)
```
this limit seems dependent on hardware. for me, it is `37748736`. keep in mind that for block models all vertices are located in the one placed block, not where they appear in the rendered model.

however, entity renderer has no such limit, and entity models can go over millions of faces regardless of whether your computer can handle rendering that many.

### versioning
due to me changing stuff, different versions of the objmc shader may only work with the script texture/model outputs of that specific version.

but also due to me changing stuff a lot i'm too lazy to try to give this a proper versioning system.

if stuff breaks make sure to double check that you have the latest version of both the shader as well as the script output.

### animation deformation
with linear interpolation, vertices travel in a straight line from one point to the next. if a rectangle with 4 vertices is to rotate about its center, the area of the rectangle would not be preserved, and the shape would deform to look smaller in the middle between keyframes.

one solution is to simply add more frames, but that can increase texture size by a lot. instead, bezier interpolation can approximate curved motion better with less keyframes.

### preserving rgb
basically anything to do with images in js does alpha premultiplying, which ruins rgb values when alpha is anything less than 255. afaik only way to not suffer this is to directly interact with the raw file instead of as an image. so if you wanted to send an image with alpha to someone over discord or something, don't send it as an image. instead, you can change the file extension so discord treats it as some unknown file, or zip it and send the zip to preserve data.

### vertex id
Minecraft's `gl_VertexID` isn't per model, so it's difficult to find the relative id of a vertex in a model unless you have a constant number of vertices.

i came up with a method to assign each face a unique uv pointing to a pixel in the 'header' of the texture, then encoding the offset of the pixel from top left (relative 0,0 in the texture, some random place in the atlas) as color of the pixel. this also lets vertex know where top left corner of the texture is in the atlas.

with the offset data i am able to calculate the relative face id, and `gl_VertexID % 4` gives the corner.

![image](https://user-images.githubusercontent.com/16228717/148311858-3bd76267-f80f-4ad6-84c3-3b5f6760bcf4.png)

in the image, the first 6 faces are selected, and their uv is shown highlighted in blockbench uv editor.

### head Pose
function to convert armorstand head Pose to potion color rgb for colorbehavior xyz
```mcfunction
execute store result score r temp run data get entity @s Pose.Head[0] 0.708333333
execute store result score g temp run data get entity @s Pose.Head[1] 0.708333333
execute store result score b temp run data get entity @s Pose.Head[2] 0.708333333

scoreboard players operation r temp %= 256 const
scoreboard players operation g temp %= 256 const
scoreboard players operation b temp %= 256 const

scoreboard players operation rgb temp = r temp
scoreboard players operation rgb temp *= 256 const
scoreboard players operation rgb temp += g temp
scoreboard players operation rgb temp *= 256 const
scoreboard players operation rgb temp += b temp

execute store result entity @s ArmorItems[3].tag.CustomPotionColor int 1 run scoreboard players get rgb temp
```

### questions
feel free to contact me on discord @Godlander#1020 or https://discord.gg/2s6th9SvZd

# contributors:
**DartCat25** - Helped me get started

**The Der Discohund** - Help with matrix operations

**Onnowhere** - Help with formatting decisions and testing

**Suso** - Idea for controlled interpolated animation

**Dominexis** - Help with spline math

**Barf Creations** - Help replicating Minecraft's jank Pose rotation matrix

**kumitatepazuru** - Adding command line arguments for the script

**Daminator** - Showing me tkinter (this is so painful why)

**thebbq** - Help with edge case hardware inconsistency debugging

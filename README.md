## usage:

make sure Python and Pillow is installed, and place the script in the same directory as the input obj and texture files.

place the shaders in the correct location in a resourcepack, and any model generated with this tool should display properly.

### script inputs

`objs`: array of string names of obj files in the same folder to read. these must have same number of vertices if used in same animation.

`frames`: array of strings of digits defining which index of the obj to use as each frame.

`texs`: array of one single name of the texture file.

`duration`: integer duration of frames in ticks.

### script output

`output`: array of two string file names: the json model, and the texture.

## samples:

![image](https://user-images.githubusercontent.com/16228717/148311540-503cf422-b6c7-4c95-b4b4-fca1e136dbfe.png)

![image](https://user-images.githubusercontent.com/16228717/148442834-78e49a63-c5f8-4668-a822-dcd11d215618.png)

![image](https://user-images.githubusercontent.com/16228717/148869708-310e7ec4-7d89-40e8-8fc6-38d2e6116cb7.png)

![animate](https://user-images.githubusercontent.com/16228717/149825494-cd51146e-38ed-48a5-a47a-0c2fce678d1a.gif)

![image](https://user-images.githubusercontent.com/16228717/149994828-d285f81d-b213-4057-bfbf-288c02891011.png)

## random notes about the tool

### general output format:

![image](https://user-images.githubusercontent.com/16228717/148311479-0cade68e-dab8-491b-83fb-f7d22c78bd1b.png)

### flipped uv

the texture ends up being read upside down for some reason. idk why, so i just flip the texture while encoding to compensate

### vertex id

Minecraft's `gl_VertexID` isn't per model, so it's difficult to find the relative id of a vertex in a model unless you have a constant number of vertices

i thought up a trick to assign each face a unique pixel uv, then encoding the offset of the pixel from top left (relative 0,0 in the texture, some random place in the atlas)

with the offset data i am able to calculate the relative face id, and `gl_VertexID % 4` gives the corner.

![image](https://user-images.githubusercontent.com/16228717/148311858-3bd76267-f80f-4ad6-84c3-3b5f6760bcf4.png)

### preserving rgb

basically anything to do with images in js does alpha premultiplying, which ruins rgb values when alpha is anything less than 255. afaik only way to not suffer this is to directly interact with the raw file instead of as an image. so if you wanted to send an image with alpha to someone over discord or something, don't send it as an image. instead, you can zip it and send the zip to preserve data, or just change the file extension so discord treats it as some unknown file.

### questions

feel free to contact me on any of the linked social media icons in my github profile readme.

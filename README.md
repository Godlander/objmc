### samples:

![image](https://user-images.githubusercontent.com/16228717/148311540-503cf422-b6c7-4c95-b4b4-fca1e136dbfe.png)

![image](https://user-images.githubusercontent.com/16228717/148442834-78e49a63-c5f8-4668-a822-dcd11d215618.png)

![image](https://user-images.githubusercontent.com/16228717/148311579-0c09d71e-8358-463f-85ac-297295c02696.png)

## random notes about the tool

### general output format:

(animation not supported yet but planned)

![image](https://user-images.githubusercontent.com/16228717/148311479-0cade68e-dab8-491b-83fb-f7d22c78bd1b.png)

### vertex id

Minecraft's `gl_VertexID` isn't per model, so it's difficult to find the relative id of a vertex in a model unless you have a constant number of vertices

i thought up a trick to assign each face a unique pixel uv, then encoding the offset of the pixel from top left (relative 0,0 in the texture, some random place in the atlas)

with the offset data i am able to calculate the relative face id, and `gl_VertexID % 4` gives the corner.

![image](https://user-images.githubusercontent.com/16228717/148311858-3bd76267-f80f-4ad6-84c3-3b5f6760bcf4.png)

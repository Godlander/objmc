from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NamedTuple


@dataclass
class Args:
    """
    Represents the arguments required to generate a Minecraft model.

    Args:
        objs (List[Path]): A list of paths to the model files.
        texs (List[Path]): A list of paths to the texture files.
        out (List[str]): A list of output file names for the generated model.
        offset (Tuple[float, float, float]): A tuple representing the position offset of the model.
        scale (float): A float representing the scaling factor of the model.
        duration (int): An integer representing the duration of the animation in ticks.
        easing (Literal[0, 1, 2, 3]): An integer literal representing the type of animation easing.
        interpolation (Literal[0, 1]): An integer literal representing the type of texture interpolation.
        colorbehavior (str): A string representing the behavior of the RGB color values.
        autorotate (Literal[0, 1, 2, 3]): An integer literal representing the type of auto-rotation.
        autoplay (bool): A boolean representing whether the animation should auto-play.
        flipuv (bool): A boolean representing whether the UV coordinates should be flipped.
        noshadow (bool): A boolean representing whether the model should have shadows.
        visibility (int): An integer representing the visibility of the model.
        nopow (bool): A boolean representing whether the texture files should have power-of-two dimensions.
        join (List[str]): A list of model names to join together.
    """

    objs: list[Path] = [""]

    # texture animations not supported yet
    texs: list[Path] = [""]

    # Output json & png
    out: list[str] = ["potion.json", "block/out.png"]

    # Position & Scaling
    # just adds & multiplies vertex positions before encoding, so you dont have to re export the model
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: float = 1.0

    # Duration of the animation in ticks
    duration: int = 0

    # Animation Easing
    # 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier
    easing: Literal[0, 1, 2, 3] = 3

    # Texture Interpolation
    # 0: none, 1: fade
    interpolation: Literal[0, 1] = 1

    # Color Behavior
    # defines the behavior of 3 bytes of rgb to rotation and animation frames,
    # any 3 chars of 'x', 'y', 'z', 't', 'o' is valid
    # 'xyz' = rotate, 't' = animation, 'o' = overlay hue
    # multiple rotation bytes increase accuracy on that axis
    # for 'ttt', autoplay is automatically on. numbers past 8388608 define paused frame to display (suso's idea)
    # auto-play color can be calculated by: ((([time query gametime] % 24000) - starting frame) % total duration)
    colorbehavior: str = "xyz"

    # Auto Rotate
    # attempt to estimate rotation with Normals, added to colorbehavior rotation.
    # one axis is ok but both is jittery. For display purposes color defined rotation is better.
    # 0: none, 1: yaw, 2: pitch, 3: both
    autorotate: Literal[0, 1, 2, 3] = 1

    # Auto Play
    # always interpolate frames, colorbehavior='aaa' overrides this.
    autoplay: bool = False

    # Flip uv
    # if your model renders but textures are not right try toggling this
    # i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
    flipuv: bool = False

    # No Shadow
    # disable face normal shading (lightmap color still applies)
    # can be used for models with lighting baked into the texture
    noshadow: bool = False

    # Visibility
    # determins where the model is visible
    # 3 bits for: world, hand, gui
    visibility: int = 7

    # No power of two textures
    # i guess saves a bit of space maybe
    # makes it not optifine compatible
    nopow: bool = True

    # Joining multiple models
    join: list[str] = []


class Position(NamedTuple):
    x: float
    y: float
    z: float


class UV(NamedTuple):
    u: float
    v: float


class Vertex(NamedTuple):
    pos: Position
    uv: UV


class VertexIndices(NamedTuple):
    pos: int
    uv: int


@dataclass
class ObjFormat:
    vertices: list[Position]
    uvs: list[UV]
    faces: list[list[VertexIndices]]

    @classmethod
    def parse(cls, content: str):
        vertices = []
        uvs = []
        faces = []

        # TODO: throw errors for invalid OBJ files, like missing vertices
        # ex: ValueError -> float("tacos")
        for line in content.splitlines():
            if line.startswith("v "):
                cleaned = line[2:].split()  # remove leading + double
                vertices.append(Vertex(*(float(num) for num in cleaned)))

            elif line.startswith("vt "):
                cleaned = line[3:].split()
                uvs.append(UV(*(float(num) for num in cleaned)))

            elif line.startswith("f "):
                face_vertices = line[1:].split(" ")
                vertex_indicies = []
                for vertex in face_vertices:
                    splitted = vertex.split("/")
                    assert len(splitted) in (2, 3)  # TODO
                    pos = int(splitted[0]) - 1
                    uv = int(splitted[1]) - 1

                    vertex_indicies.append(VertexIndices(pos, uv))

                faces.append(vertex_indicies)

        # TODO: handle error
        # if nfaces > 0 and len(d["faces"]) != nfaces:
        # print(col.err+"mismatched obj face count"+col.end)
        
        return cls(vertices, uvs, faces)


count = [0,0]
mem = {"positions":{},"uvs":{}}
data = {"positions":[],"uvs":[],"vertices":[]}
def readobj(name, nfaces):
  obj = open(name, "r", encoding="utf-8")
  d = {"positions":[],"uvs":[],"faces":[]}
  for line in obj:
    if line.startswith("v "):
      d["positions"].append(tuple([float(i) for i in " ".join(line.split()).split(" ")[1:]]))
    if line.startswith("vt "):
      d["uvs"].append(tuple([float(i) for i in " ".join(line.split()).split(" ")[1:]]))
    if line.startswith("f "):
      d["faces"].append(tuple([[int(i)-1 for i in vert.split("/")] for vert in " ".join(line.split()).split(" ")[1:]]))
  obj.close()
  if nfaces > 0 and len(d["faces"]) != nfaces:
    print(col.err+"mismatched obj face count"+col.end)
    exit()
  return d
#index vertices
def indexvert(o, vert):
  global count
  global mem
  global data
  v = []
  pos = o["positions"][vert[0]]
  uv = o["uvs"][vert[1]]
  posh = ','.join([str(i) for i in pos])
  uvh =','.join([str(i) for i in uv])
  try:
    v.append(mem["positions"][posh])
  except:
    mem["positions"][posh] = count[0]
    data["positions"].append(pos)
    v.append(count[0])
    count[0] += 1
  try:
    v.append(mem["uvs"][uvh])
  except:
    mem["uvs"][uvh] = count[1]
    data["uvs"].append(uv)
    v.append(count[1])
    count[1] += 1
  data["vertices"].append(v)
#index obj
def indexobj(o, frame, nframes, nfaces):
  for face in range(0, len(o["faces"])):
    if face % 1000 == 0:
      print("\Reading obj ", frame+1, " of ", nframes, "...", "{:>15.2f}".format((frame*nfaces+face)*100/(nframes*nfaces)), "%\033[K", sep="", end="\r")
    face = o["faces"][face]
    for vert in face:
      indexvert(o, vert)
    if len(face) == 3:
      indexvert(o, face[1])      indexvert(o, face[1])
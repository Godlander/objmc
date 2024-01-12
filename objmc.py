import os, sys, math, json
from dataclasses import dataclass
from typing import Literal
from argparse import ArgumentParser
from PIL import Image, ImageOps
from obj import *

@dataclass
class Args:
    """
    arguments required to generate objmc model
    Args:
        objs (List[Path]): list of paths to the model files
        texs (List[Path]): list of paths to the texture files
        out (List[str]): list of output file names for the generated model
        offset (Tuple[float, float, float]): tuple representing the position offset of the model
        scale (float): float representing the scaling factor of the model
        duration (int): integer representing the duration of the animation in ticks
        easing (Literal[0, 1, 2, 3]): integer literal representing the type of animation easing
        interpolation (Literal[0, 1]): integer literal representing the type of texture interpolation
        colorbehavior (str): string representing the behavior of the RGB color values
        autorotate (Literal[0, 1, 2, 3]): integer literal representing the type of auto-rotation
        autoplay (bool): boolean representing whether the animation should auto-play
        flipuv (bool): boolean representing whether the UV coordinates should be flipped
        noshadow (bool): boolean representing whether the model should have shadows
        visibility (int): integer representing the visibility of the model
        nopow (bool): boolean representing whether the texture files should have power-of-two dimensions
        join (List[str]): list of model names to join together
    """

    objs = [""]

    # texture animations not supported yet
    texs = [""]

    # output json & png
    out = ["potion.json", "block/out.png"]

    # position & scaling
    # just adds & multiplies vertex positions before encoding, so you dont have to re export the model
    offset = (0.0, 0.0, 0.0)
    scale = 1.0

    # duration of the animation in ticks
    duration = 0

    # animation easing
    # 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier
    easing: Literal[0, 1, 2, 3] = 3

    # texture interpolation
    # 0: none, 1: fade
    interpolation: Literal[0, 1] = 1

    # color behavior
    # defines the behavior of 3 bytes of rgb to rotation and animation frames,
    # any 3 chars of 'x', 'y', 'z', 't', 'o' is valid
    # 'xyz' = rotate, 't' = animation, 'o' = overlay hue
    # multiple rotation bytes increase accuracy on that axis
    # for 'ttt', autoplay is automatically on. numbers past 8388608 define paused frame to display (suso's idea)
    # auto-play color can be calculated by: ((([time query gametime] % 24000) - starting frame) % total duration)
    colorbehavior = ('pitch', 'yaw', 'roll')

    # auto rotate
    # attempt to estimate rotation with Normals, added to colorbehavior rotation.
    # one axis is ok but both is jittery. For display purposes color defined rotation is better.
    # 0: none, 1: yaw, 2: pitch, 3: both
    autorotate: Literal[0, 1, 2, 3] = 1

    # auto play
    # always interpolate frames, colorbehavior='aaa' overrides this.
    autoplay = False

    # flip uv
    # if your model renders but textures are not right try toggling this
    # i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
    flipuv = False

    # no shadow
    # disable face normal shading (lightmap color still applies)
    # can be used for models with lighting baked into the texture
    noshadow = False

    # visibility
    # determins where the model is visible
    # 3 bits for: world, hand, gui
    visibility = 7

    # no power of two textures
    # i guess saves a bit of space maybe
    nopow = True

    # Joining multiple models
    join = [""]



class ArgumentParserError(Exception): pass
class ThrowingArgumentParser(ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
def args():
    parser = ThrowingArgumentParser(
        description=(
            "python script to convert .OBJ files into Minecraft, "
            "rendering them in game with a core shader.\n"
            "Github: https://github.com/Godlander/objmc"
        )
    )
    args = Args()
    parser.add_argument("--objs", help="List of object files", nargs="*", default=args.objs)
    parser.add_argument("--texs", help="Specify a texture file", nargs="*", default=args.texs)
    parser.add_argument("--out", type=str, help="Output json and png", nargs=2, default=args.out)
    parser.add_argument("--offset", type=float, help="Offset of model in xyz", nargs=3, default=args.offset)
    parser.add_argument("--scale", type=float, help="Scale of model", default=args.scale)
    parser.add_argument("--duration", type=int, help="Duration of the animation in ticks", default=args.duration)
    parser.add_argument("--easing", type=int, help="Animation easing, 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier", default=args.easing)
    parser.add_argument("--interpolation", type=int, help="Texture interpolation, 0: none, 1: fade", default=args.interpolation)
    parser.add_argument("--colorbehavior", type=str, help=( "Item color overlay behavior, \"xyz\": rotate" ", 't': animation time offset, 'o': overlay hue" ), default=args)
    parser.add_argument("--autorotate", type=int, help=( "Attempt to estimate rotation with Normals" "0: off, 1: yaw, 2: pitch, 3: both" ), default=args.autorotate)
    parser.add_argument("--autoplay", action="store_true", dest="autoplay", help='Always interpolate animation, colorbehavior="ttt" overrides this', default=args.autoplay)
    parser.add_argument("--visibility", type=int, help="Determines where the model is visible", default=args.visibility)
    parser.add_argument("--flipuv", action="store_true", dest="flipuv", help="Invert the texture to compensate for flipped UV")
    parser.add_argument("--noshadow", action="store_true", dest="noshadow", help="Disable shadows from face normals")
    parser.add_argument("--nopow", action="store_true", dest="nopow", help="Disable power of two textures")
    parser.add_argument("--join", nargs="*", dest="join", help="Joins multiple json models into one")
    args = parser.parse_args(namespace=Args)

    #file extension optional
    if (args.out[0][-5:] != ".json"):
        args.out[0] += ".json"
    if (args.out[1][-4:] != ".png"):
        args.out[1] += ".png"

    return args

class col:
    head = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    warn = '\033[93mWarning: '
    err = '\033[91mError: '
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'
    r = "%\033[K"
def quit():
    sys.exit()
def exit():
    print("Press any key to exit...")
    os.system('pause >nul')
    sys.exit()

def objmc(args: Args):
    ntextures = len(args.texs)
    nframes = len(args.objs)

    #input error checking
    if ntextures < 1 or nframes < 1:
        print(col.err+"must have a obj and a texture"+col.end)
        exit()
    duration = args.duration
    if duration == 0:
        duration = nframes
    if duration < 1 or duration > 65536:
        print(col.err+"duration must be between 1 and 65536"+col.end)
        exit()
    tex = Image.open(args.texs[0])
    x,y = tex.size
    if x < 8:
        print(col.err+"minimum texture size is 8x8"+col.end)
        exit()

    print("\n"+col.cyan+"objmc start "+col.end)
    #read obj
    print("Reading obj 1 of ", nframes, "...", "{:>15.2f}".format(0), col.r, sep="", end="\r")
    o = Obj(args.objs[0])
    nfaces = len(o.faces)
    objs = Objs()
    objs.add(o)
    if nframes > 1:
        for frame in range(1, nframes):
            o = Obj(args.objs[frame])
            assert len(o.faces) == nfaces
            objs.add(o)

    nvertices = nfaces*4
    texheight = ntextures * y
    uvheight = math.ceil(nfaces/x)
    vpheight = math.ceil(len(objs.positions)*3/x)
    vtheight = math.ceil(len(objs.uvs)*2/x)
    vheight = math.ceil(len(objs.vertices)*2/x)
    #make height power of 2
    ty = 1 + uvheight + texheight + vpheight + vtheight + vheight
    if not args.nopow:
     ty = 1<<(ty - 1).bit_length()
    if (ty > 4096 and x < 4096) or (ty > 8*x):
        print(col.warn+"output height may be too high, consider increasing width of input texture or reducing number of frames to bring the output texture closer to a square."+col.end)

    #parse color behavior
    cbarr = ['pitch', 'yaw', 'roll', 'time', 'scale', 'overlay']
    ca = [cbarr.index(i) for i in args.colorbehavior]
    cb = ((ca[0]<<6) + (ca[1]<<3) + (ca[2]))

    #initial info
    print(col.r, end="\r")
    print("faces: ", nfaces, ", verts: ", nvertices, ", tex: ", (x,y), ", flipuv: ", args.flipuv, sep="")
    if nframes > 1 or ntextures > 1:
        print("objs: ", nframes, ", easing: ", args.easing, sep="")
        print("texs: ", ntextures, ", interpolation: ", args.interpolation, sep="")
        print("duration: ", duration,"t", ", ", duration/20, "s, autoplay: ", args.autoplay, sep="")
    print("uvhead: ", uvheight, ", vph: ", vpheight, ", vth: ", vtheight, ", vh: ", vheight, ", total: ", ty, sep="")
    print("colorbehavior: ", " ".join(args.colorbehavior), " (", cb, ")", ", autorotate: ", args.autorotate, sep="")
    print("offset: ", args.offset, ", scale: ", args.scale, ", noshadow: ", args.noshadow, sep="")
    print("visible:", " world" if args.visibility & 4 > 0 else "", " hand" if args.visibility & 2 > 0 else "", " gui" if args.visibility & 1 > 0 else "", sep="")
    print("Creating Files...", end="\r")
    #write to json model
    model = open(args.out[0], "w")
    #create out image with correct dimensions
    out = Image.new("RGBA", (x, int(ty)), (0,0,0,0))

    # header
    #| 2^32   | 2^16x2   | 2^32      | 2^24 + 2^8   | 2^24    + \1 2^1  + 2^2   + 2^2  \2| 2^16x2       | 2^1     + 2^2       + 2^3    \1 + 2^1 + 2^8   \16|
    #| marker | tex size | nvertices | nobjs, ntexs | duration, autoplay, easing, interp | data heights | noshadow, autorotate, visibility, colorbehavior    |
    #0: marker
    out.putpixel((0,0), (12,34,56,78))
    #1: texsize
    out.putpixel((1,0), (int(x/256), x%256, int(y/256), y%256))
    #2: nvertices
    out.putpixel((2,0), (int(nvertices/16777216)%256, int(nvertices/65536)%256, int(nvertices/256)%256, nvertices%256))
    #3: nobjs, ntexs
    out.putpixel((3,0), (int(nframes/65536)%256, int(nframes/256)%256, nframes%256, ntextures))
    #4: duration, autoplay, easing
    out.putpixel((4,0), (int(duration/65536)%256, int(duration/256)%256, duration%256, 128+(int(args.autoplay)<<6)+(args.easing<<4)+(args.interpolation<<2)))
    #5: data heights
    out.putpixel((5,0), (int(vpheight/256)%256, int(vpheight)%256, int(vtheight/256)%256, vtheight%256))
    #6: noshadow, autorotate, visibility, colorbehavior
    out.putpixel((6,0), ((int(args.noshadow)<<7)+(args.autorotate<<5)+(args.visibility<<2) + int(cb/256), cb%256, 255))

    #actual texture
    for i in range (0,len(args.texs)):
        tex = Image.open(args.texs[i])
        nx,ny = tex.size
        if nx != x or ny != y:
            print(col.err+"mismatched texture sizes"+col.end)
            exit()
        if args.flipuv:
            out.paste(tex, (0,1+uvheight+(i*y)))
        else:
            out.paste(ImageOps.flip(tex), (0,1+uvheight+(i*y)))

    #unique pixel uv per face with color pointing to topleft
    def getheader(out, faceid, x, y):
        posx = faceid%x
        posy = math.floor(faceid/x)+1
        out.putpixel((posx, posy), (int(posx/256)%256, posx%256, int(posy/256)%256, posy%256))
        return [(posx+0.1)*16/x, (posy+0.1)*16/y, (posx+0.9)*16/x, (posy+0.9)*16/y]
    #generate json model elements and uv header
    global js
    js = {
        "textures": {
            "0": args.out[1].split('.')[0]
        },
        "elements": [],
        "display": {
            "thirdperson_righthand": {
                "rotation": [85, 0, 0]
            },
            "thirdperson_lefthand": {
                "rotation": [85, 0, 0]
            }
        }
    }
    for i in range(0, nfaces):
        js["elements"].append({
            "from":[8,0,8],
            "to":[8.000001,0.000001,8.000001],
            "faces":{
                "north":{"uv":getheader(out, i, x, ty),"texture":"#0","tintindex":0}
            }
        })

    print("Writing json model...\033[K", end="\r")
    model.write(json.dumps(js,separators=(',',':')))
    model.close()

    print("Writing position data...\033[K", end="\r")
    y = 1 + uvheight + texheight
    for i in range(0,len(objs.positions)):
        _x = 8388608+(objs.positions[i].x*65536)*args.scale + args.offset[0]*65536
        _y = 8388608+(objs.positions[i].y*65536)*args.scale + args.offset[1]*65536
        _z = 8388608+(objs.positions[i].z*65536)*args.scale + args.offset[2]*65536
        _rgb = []
        _rgb.append((int((_x/65536)%256), int((_x/256)%256), int(_x%256), 255))
        _rgb.append((int((_y/65536)%256), int((_y/256)%256), int(_y%256), 255))
        _rgb.append((int((_z/65536)%256), int((_z/256)%256), int(_z%256), 255))
        for j in range(0,3):
            p = i*3+j
            out.putpixel((p%x,y+math.floor(p/x)), _rgb[j])
    print("Writing uv data...\033[K", end="\r")
    y = 1 + uvheight + texheight + vpheight
    for i in range(0,len(objs.uvs)):
        _x = objs.uvs[i].x*65535
        _y = objs.uvs[i].y*65535
        _rgb = []
        _rgb.append((int((_x/65536)%256), int((_x/256)%256), int(_x%256), 255))
        _rgb.append((int((_y/65536)%256), int((_y/256)%256), int(_y%256), 255))
        for j in range(0,2):
            p = i*2+j
            out.putpixel((p%x,y+math.floor(p/x)), _rgb[j])
    print("Writing vertex data...\033[K", end="\r")
    y = 1 + uvheight + texheight + vpheight + vtheight
    for i in range(0,len(objs.vertices)):
        _pos = (objs.vertices[i].pos)
        _uv = (objs.vertices[i].uv)
        _rgb = []
        _rgb.append((int((_pos/65536)%256), int((_pos/256)%256), int(_pos%256), 255))
        _rgb.append((int((_uv /65536)%256), int((_uv /256)%256), int(_uv %256), 255))
        for j in range(0,2):
            p = i*2+j
            out.putpixel((p%x,y+math.floor(p/x)), _rgb[j])

    print("Saving image...\033[K", end="\r")
    out.save(args.out[1].split('/')[-1])
    out.close()
    print(col.green+"Complete\033[K"+col.end)

if __name__ == "__main__":
    objmc(args())
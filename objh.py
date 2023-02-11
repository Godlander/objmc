import sys
import os
os.system("title objmc output")
os.system('color')
import math
import argparse
from PIL import Image
from tkinter import Tk

#--------------------------------
#INPUT
#--------------------------------

#objs
obj = ""
#texture animations not supported yet
tex = ""

#Output json & png
output = ""

#Position & Scaling
# just adds & multiplies vertex positions before encoding, so you dont have to re export the model
offset = (0.0,0.0,0.0)
scale = 1.0

#Auto Rotate
# attempt to estimate rotation with Normals, added to colorbehavior rotation.
# one axis is ok but both is jittery. For display purposes color defined rotation is better.
# 0: none, 1: yaw, 2: pitch, 3: both
autorotate = 1

#No Shadow
# disable face normal shading (lightmap color still applies)
# can be used for models with lighting baked into the texture
noshadow = False

#--------------------------------
#argument parsing by kumitatepazuru
#respects above settings as default
class ArgumentParserError(Exception): pass
class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
parser = ThrowingArgumentParser(description="python script to convert .OBJ files into Minecraft, rendering them in game with a core shader.\nGithub: https://github.com/Godlander/objmc")
parser.add_argument("--obj", type=str, help="List of object files", default=obj)
parser.add_argument("--tex", type=str, help="Specify a texture file", default=tex)
parser.add_argument("--out", type=str, help="Output json and png", default=output)
parser.add_argument("--offset", type=float, help="Offset of model in xyz", nargs=3, default=offset)
parser.add_argument("--scale", type=float, help="Scale of model", default=scale)
parser.add_argument("--autorotate", type=int, help="Attempt to estimate rotation with Normals, 0: off, 1: yaw, 2: pitch, 3: both", default=autorotate)
parser.add_argument("--noshadow", action="store_true", dest="noshadow", help="Disable shadows from face normals")
def getargs(args):
  global obj
  global tex
  global output
  global offset
  global scale
  global autorotate
  global noshadow
  obj = args.obj
  tex = args.tex
  output = args.out
  offset = tuple(args.offset)
  scale = args.scale
  autorotate = args.autorotate
  noshadow = args.noshadow
getargs(parser.parse_args())

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
def quit():
  sys.exit()
def exit():
  print("Press any key to exit...")
  os.system('pause >nul')
  sys.exit()

#--------------------------------
count = [0,0]
mem = {"positions":{},"uvs":{}}
data = {"positions":[],"uvs":[],"vertices":[],"maxpos":0}
def readobj(name):
  obj = open(name, "r", encoding="utf-8")
  d = {"positions":[],"uvs":[],"faces":[]}
  for line in obj:
    if line.startswith("v "):
      d["positions"].append([float(i) for i in " ".join(line.split()).split(" ")[1:]])
    if line.startswith("vt "):
      d["uvs"].append([float(i) for i in " ".join(line.split()).split(" ")[1:]])
    if line.startswith("f "):
      d["faces"].append([[int(i)-1 for i in vert.split("/")] for vert in " ".join(line.split()).split(" ")[1:]])
  obj.close()
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
    for p in pos:
      if abs(p) > data["maxpos"]:
        data["maxpos"] = abs(p)
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
def indexobj(o):
  global nfaces
  nfaces = len(o["faces"])
  for face in o["faces"]:
    for vert in face:
      indexvert(o, vert)
    if len(face) == 3:
      indexvert(o, face[1])

#grab data from the list and convert to rgb
def getposition(i):
  x = 8388608+((data["positions"][i][0])*65536)*scale + offset[0]*65536
  y = 8388608+((data["positions"][i][1])*65536)*scale + offset[1]*65536
  z = 8388608+((data["positions"][i][2])*65536)*scale + offset[2]*65536
  rgb = []
  rgb.append((int((x/65536)%256), int((x/256)%256), int(x%256), 255))
  rgb.append((int((y/65536)%256), int((y/256)%256), int(y%256), 255))
  rgb.append((int((z/65536)%256), int((z/256)%256), int(z%256), 255))
  return rgb
def getuv(i):
  x = (data["uvs"][i][0])*65535
  y = (data["uvs"][i][1])*65535
  rgb = []
  rgb.append((int((x/65536)%256), int((x/256)%256), int(x%256), 255))
  rgb.append((int((y/65536)%256), int((y/256)%256), int(y%256), 255))
  return rgb
def getvert(i):
  poi = (data["vertices"][i][0])
  uvi = (data["vertices"][i][1])
  rgb = []
  rgb.append((int((poi/65536)%256), int((poi/256)%256), int(poi%256), 255))
  rgb.append((int((uvi/65536)%256), int((uvi/256)%256), int(uvi%256), 255))
  return rgb
#-------------------------------------------------------------------------

tex = Image.open(tex)
if tex.size != (32,32):
  print(col.err+"Texture size must be 32x32."+col.end)
  exit()

nfaces = 0
#load obj
indexobj(readobj(obj))
#normalize positions
print(data["positions"])
data["positions"] = [[int(127.5 + 127.5*p/data["maxpos"]) for p in v] for v in data["positions"]]
print(data["positions"])
#normalize uvs
data["uvs"] = [[int(255*v) for v in u] for u in data["uvs"]]

npos = len(data["positions"])
nuv = len(data["uvs"])
nvertices = nfaces*4
nheads = math.ceil(nfaces/12)

print("\n"+col.cyan+"objh start "+col.end)
print("%\033[K", end="\r")
print("faces: ", nfaces, ", verts: ", nvertices, ", heads: ", nheads, sep="")
print("pos: ", npos, ", uv: ", nuv, sep="")

if nvertices > 1056 or npos + nuv > 1984:
  print(col.err+"Model too complicated."+col.end)
  exit()

out = Image.new("RGBA", (64, 64), (0,0,0,0))
out.paste(tex,(0,0))
#0: marker
out.putpixel((0,32), (12,34,56,78))
#1: npos, noshadow
out.putpixel((1,32), (int(npos/256),npos%256,noshadow,255))

#encode data
id = 0
for v in data["vertices"]:
  x = 32 + id % 32
  y = int(id/32)
  out.putpixel((x,y), ((int(v[0]/256)<<4) + int(v[1]/256), v[0]%256, v[1]%256, 255))
  id += 1

id = 0
for p in data["positions"]:
  x = id % 64
  y = 33 + int(id/64)
  out.putpixel((x,y), (p[0], p[1], p[2], 255))
  id += 1
for u in data["uvs"]:
  x = id % 64
  y = 33 + int(id/64)
  out.putpixel((x,y), (u[0], u[1], 0, 255))
  id += 1

print("Saving files...\033[K", end="\r")
out.save(output)

command = "execute "
command += "positioned ~ ~2 ~"
for i in range(nheads):
  command += " summon item_display"
command += ' as @e[type=item_display,distance=..0.1,nbt={item:{id:"minecraft:air"}}] run item replace entity @s container.0 with minecraft:player_head{SkullOwner:{Id:[I;1617307098,1728332524,-1389744951,-1149641594],Properties:{textures:[{Value:"eyd0ZXh0dXJlcyc6IHsnU0tJTic6IHsndXJsJzogJ2h0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvOTVlYzdhZjJlODZlZThlODQ5NzJhOGZhNjZkMzllZTNkMzhlYjE5YjY3MzBmZDA1MmIzNzg1YjVjMmQwYzRkMid9fX0="}]}}}'
print(command)
quit()

import sys,os
os.system("title objmc output")
os.system('color')
import math,argparse,re,urllib.request,json,base64
from PIL import Image, ImageOps

#--------------------------------
#INPUT
#--------------------------------

#objs
obj = ""
#texture animations not supported yet
tex = ""

#Output json & png
output = ""

#Scale
# multiplies final size by an integer factor 1 + (0-255)
scale = 0

#Flip uv
# if your model renders but textures are not right try toggling this
# i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
flipuv = False

#No Shadow
# disable face normal shading (lightmap color still applies)
# can be used for models with lighting baked into the texture
noshadow = False

#Skin
# grabs skin data of user
skin = ""

#--------------------------------
#argument parsing by kumitatepazuru
#respects above settings as default
class ArgumentParserError(Exception): pass
class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
parser = ThrowingArgumentParser(description="python script to convert .OBJ files into Minecraft, rendering them in game with a core shader.\nGithub: https://github.com/Godlander/objmc")
parser.add_argument("--obj", type=str, help="Specify an obj file", default=obj)
parser.add_argument("--tex", type=str, help="Specify a texture file", default=tex)
parser.add_argument("--out", type=str, help="Output skin png", default=output)
parser.add_argument("--scale", type=int, help="Scale of model 1+(0-255)", default=scale)
parser.add_argument("--flipuv", action="store_true", dest="flipuv", help="Invert the texture to compensate for flipped UV")
parser.add_argument("--noshadow", action="store_true", dest="noshadow", help="Disable shadows from face normals")
parser.add_argument("--skin", type=str, help="Username to grab skin data from", default=obj)
def getargs(args):
  global obj
  global tex
  global output
  global scale
  global flipuv
  global noshadow
  global skin
  obj = args.obj
  tex = args.tex
  output = args.out
  scale = args.scale
  flipuv = args.flipuv
  noshadow = args.noshadow
  skin = args.skin
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
if skin and len(skin) <= 32:
  url = 'https://api.mojang.com/users/profiles/minecraft/'+skin
  response = urllib.request.urlopen(url)
  content = json.loads(response.read().decode('utf8'))
  uuid = content['id']

  hexArray = re.split('(........)', uuid)[1::2]
  intArray = [int(v, 16) for v in hexArray]
  intArray =  [v-2147483648*2 if 2147483647<v else v for v in intArray]
  strArray = [str(v) for v in intArray]

  url = 'https://sessionserver.mojang.com/session/minecraft/profile/'+uuid
  response = urllib.request.urlopen(url)
  content = json.loads(response.read().decode('utf8'))
  skin = content['properties'][0]['value']

  content = json.loads(base64.b64decode(skin).decode())
  skin = {k: v for k, v in content.items() if k == 'textures'}
  skin = base64.b64encode(str(skin).encode())
  skin = re.search(r'\'(.+)\'',str(skin)).group(1)

  if not obj or not tex:
    print(col.green+skin+col.end)
    exit()
else:
  skin = 'REPLACE_URL'

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

#--------------------------------

tex = Image.open(tex)
if tex.size != (32,32):
  print(col.err+"Texture size must be 32x32"+col.end)
  exit()
if scale > 255 or scale < 0:
  print(col.err+"Scale must be between 0-255"+col.end)
  exit()

nfaces = 0
#load obj
indexobj(readobj(obj))
#normalize positions
data["positions"] = [[int(127.5 + 127.5*p/data["maxpos"]) for p in v] for v in data["positions"]]
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
print("scale:", scale, ", noshadow: ", noshadow, sep="")

ndata = nvertices + npos + nuv
if ndata > 3040:
  print(col.err+"Model too complicated ("+str(ndata)+">"+"3040)"+col.end)
  exit()

out = Image.new("RGBA", (64, 64), (0,0,0,0))
if flipuv:
  out.paste(ImageOps.flip(tex), (0,0))
else:
  out.paste(tex, (0,0))

#0: marker
out.putpixel((0,32), (12,34,56,78))
#1: nfaces, npos
out.putpixel((1,32), ((int(nfaces/256)<<4) + int(npos/256), nfaces%256, npos%256, 255))
#2: noshadow, scale, reserved
out.putpixel((2,32), (noshadow, scale, 0, 255))

def coord(id):
  if id < 1056:
    x = 32 + id % 32
    y = int(id/32)
  else:
    id -= 1056
    x = id % 64
    y = 33 + int(id/64)
  return (x,y)

#encode data
id = 0
for v in data["vertices"]:
  out.putpixel(coord(id), ((int(v[0]/256)<<4) + int(v[1]/256), v[0]%256, v[1]%256, 255))
  id += 1
for p in data["positions"]:
  out.putpixel(coord(id), (p[0], p[1], p[2], 255))
  id += 1
for u in data["uvs"]:
  out.putpixel(coord(id), (u[0], u[1], 0, 255))
  id += 1

print("Saving skin...\033[K", end="\r")
out.save(output)

command = "summon area_effect_cloud ~ ~1 ~ {Passengers:["
for i in range(nheads):
  x = (i%4)       *500-1000
  y = (int(i/4)%4)*500-1000
  z = (int(i/16)) *500-1000
  command += '{id:"item_display",Tags:["objh"],transformation:{translation:['+str(x)+'f,'+str(y)+'f,'+str(z)+'f],scale:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},item:{id:"player_head",Count:1b,tag:{SkullOwner:{Id:[I;0,0,0,0],Properties:{textures:[{Value:"'+skin+'"}]}}}}},'
command += "]}"
print(col.green+command+col.end+'\n')

quit()
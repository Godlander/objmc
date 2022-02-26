import math
import json
from PIL import Image, ImageOps
import argparse
import os.path

parser = argparse.ArgumentParser(
    description='python script to convert .OBJ files into Minecraft, rendering them in game with a core shader.\nGithub: https://github.com/Godlander/objmc')

#--------------------------------
#INPUT
#--------------------------------

parser.add_argument('--objs', help='Specify a set of object files', required=True, nargs='*')
parser.add_argument('--texs', help='Specify a set of texture files', required=True, nargs='*')
parser.add_argument('--frames', help='Specify a frame', nargs='*', default=["0"])
parser.add_argument('--duration', type=int, help="Spectify a duration", default=20)
parser.add_argument('--easing', type=int, help="Spectify a easing\n0: none, 1: linear, 2: inoutcubic", default=1)
parser.add_argument("--output_texture", help="Specify the name of the texture file to output", default="catout")
parser.add_argument("--output_json", help="Specify the name of the json file to output", default="yellow_stained_glass")
args = parser.parse_args()

# texture animations not supported yet
texs = args.texs
# objs
objs = list(map(lambda n: os.path.splitext(n)[0], args.objs))

frames = args.frames

# json, png
output = [args.output_json, args.output_texture]

#--------------------------------
#ADVANCED
#(changing these only changes data on texture, no need to replace model)
#--------------------------------

#Position/Scaling
# just adds & multiplies vertex positions before encoding, so you dont have to re export the model
offset = (0,0,0)
scale = 1

#duration of each frame in ticks
duration = args.duration

#Animation Easing
# 0: none
# 1: linear
# 2: in-out cubic
# 3: 4-point bezier
easing = args.easing

#Item Color Overlay Behavior
# number of bytes to trade between rotation and animation frames,
#    r,g,b =
# 0: rotation x,y,z
# 1: rotation x,y , animation frames 0-255
# 2: rotation x   , animation frames 0-65535
# 3: animation frames 0-8388607. numbers past 8388608 defines starting frame to auto-play from with smooth interpolation (suso's idea)
#for 3, auto-play color can be calculated by: 8388608 + ((total duration + ([time query gametime] % 24000) - starting frame) % total duration)
colorbehavior = 0

#Auto Rotate
# attempt to estimate rotation with Normals, added to colorbehavior rotation.
# this is very jittery, best used for far away objects. For display purposes color defined rotation is much better.
autorotate = False

#Auto Play
# always interpolate frames, colorbehavior=3 overrides this.
autoplay = True

#Flip uv
#if your model renders but textures are not right try toggling this
#i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
flipuv = False

#--------------------------------

# file extension optional
output[0] = output[0].split(".")[0]
output[1] = output[1].split(".")[0]

# input error checking
if len(frames) == 0:
    frames.append("0")
if duration < 1 or duration > 256:
    print("Duration must be between 1 and 256")
    quit()

tex = Image.open(texs[0])
x, y = tex.size
if x < 8:
  print("Minimum texture size is 8x")
  quit()

objects = []
def readobj(name):
  obj = open(name.split(".")[0]+".obj", "r")
  d = {"positions":[],"uvs":[],"normals":[],"faces":[]}
  for line in obj:
    if line.startswith("v "):
      d["positions"].append([float(i) for i in " ".join(line.split()).split(" ")[1:]])
    if line.startswith("vt "):
      d["uvs"].append([float(i) for i in " ".join(line.split()).split(" ")[1:]])
    if line.startswith("vn "):
      d["normals"].append([float(i) for i in " ".join(line.split()).split(" ")[1:]])
    if line.startswith("f "):
      d["faces"].append([[int(i)-1 for i in vert.split("/")] for vert in " ".join(line.split()).split(" ")[1:]])
  obj.close()
  return d
#read obj
objects.append(readobj(objs[0]))
for i in range(1,len(objs)):
  objects.append(readobj(objs[i]))
  if len(objects[i]["faces"]) != len(objects[0]["faces"]):
    print("mismatched obj face count")
    quit()

#calculate heights
ntextures = len(texs)
nframes = len(frames)
nfaces = len(objects[0]["faces"])
nvertices = nfaces*4
texheight = ntextures * y
uvheight = math.ceil(nfaces/x)
#meta = rgba: scale, hasnormal, easing, unused
#position = rgb, rgb, rgb
#normal = aaa
#uv = rg,ba
dataheight = (nframes * math.ceil(((5*nvertices))/x)) + 1

ty = 1 + uvheight + texheight + dataheight

print("x: ", x, ", y: ", y,sep="")
print("faces: ", nfaces, ",vertices: ", nvertices, sep="")
print("uvheight: ", uvheight, ", texheight: ", texheight, ", dataheight: ", dataheight, ", totalheight: ", sep="")
print("frames: ", nframes, ", duration: ", duration," ticks", ", total: ", duration*nframes/20, " seconds", sep="")
#write to json model
model = open(output[0]+".json", "w")
#create out image with correct dimensions
out = Image.new("RGBA", (x, int(ty)), (0,0,0,0))

#header:
#marker pix
out.putpixel((0,0), (12,34,56,0))
#texture size
out.putpixel((1,0), (int(x/256), x%256, int(y/256), y%256))
#nvertices
out.putpixel((2,0), (int(nvertices/256/256/256)%256, int(nvertices/256/256)%256, int(nvertices/256)%256, nvertices%256))
#nframes, ntextures, duration, colorbehavior
out.putpixel((3,0), (nframes,ntextures,duration-1,colorbehavior))
#autorotate
out.putpixel((4,0), (int(autorotate), int(autoplay), 0, 255))

#actual texture
for i in range (0,len(texs)):
  tex = Image.open(texs[i])
  nx,ny = tex.size
  if nx != x or ny != y:
    print("mismatched texture sizes!")
    quit()
  if flipuv:
    out.paste(tex, (0,1+uvheight+(i*y)))
  else:
    out.paste(ImageOps.flip(tex), (0,1+uvheight+(i*y)))

#unique pixel uv per face with color pointing to topleft
def getuvpos(faceid):
  posx = faceid%x
  posy = math.floor(faceid/x)+1
  out.putpixel((posx, posy), (int(posx/256)%256, posx%256, int(posy/256)%256, posy%256))
  return [(posx+0.1)*16/x, (posy+0.1)*16/ty, (posx+0.9)*16/x, (posy+0.9)*16/ty]
#create elements for model
js = {
  "textures": {
    "layer0": output[1]
  },
  "elements": []
}
def newelement(index):
  cube = {
    "from": [8,8,8],
    "to": [8.000001,8.000001,8.000001],
    "faces": {
      "north" : {"uv": getuvpos(index), "texture": "#layer0", "tintindex": 0}
    }
  }
  js["elements"].append(cube)
#generate elements and uv header
for i in range(0, nfaces):
  newelement(i)
model.write(json.dumps(js))
model.close()

#grab data from the list and convert to rgb
def getposition(id, index):
  x = 8388608+((objects[id]["positions"][index][0])*65536)*scale + offset[0]*65536
  y = 8388608+((objects[id]["positions"][index][1])*65536)*scale + offset[1]*65536
  z = 8388608+((objects[id]["positions"][index][2])*65536)*scale + offset[2]*65536
  rgb = []
  r = int((x/256/256)%256)
  g = int((x/256)%256)
  b = int(x%256)
  rgb.append([r,g,b])
  r = int((y/256/256)%256)
  g = int((y/256)%256)
  b = int(y%256)
  rgb.append([r,g,b])
  r = int((z/256/256)%256)
  g = int((z/256)%256)
  b = int(z%256)
  rgb.append([r,g,b])
  return rgb
def getnormal(id, index):
  r = int((objects[id]["normals"][index][0]+1)*255/2)
  g = int((objects[id]["normals"][index][1]+1)*255/2)
  b = int((objects[id]["normals"][index][2]+1)*255/2)
  return [r,g,b]
def getuv(id, index):
  x = (objects[id]["uvs"][index][0])*65535
  y = (objects[id]["uvs"][index][1])*65535
  r = int(x/256)%256
  g = int(x%256)
  b = int(y/256)%256
  a = int(y%256)
  return (r,g,b,a)
def getp(frame, index, offset):
  i = ((frame)*nvertices*5)+(index*5)+offset
  xx = i%x
  yy = int(1+uvheight+y+((i/x)))
  return (xx,yy)
#meta: textureid, easing, scale?, unused
#position = rgb, rgb, rgb
#normal = aaa
#uv = rg,ba
#face:[pos,uv,norm]
def encodevert(id, frame, index, face):
  #init meta
  scale = 100
  #meta: textureid, easing, scale?, unused
  out.putpixel(getp(frame, index, 0), (0, easing, scale, 255))
  #get position and append normal
  rgb = getposition(id[0], face[0])
  if len(face) == 2:
    norm = [0,255,0]
  else:
    norm = getnormal(id[0], face[2])
  #position and normal
  for i in range(0,3):
    rgb[i].append(norm[i])
    out.putpixel(getp(frame, index, i+1), tuple(rgb[i]))
  #uv
  out.putpixel(getp(frame, index, 4), getuv(id[0], face[1]))

def encodeface(id, frame, index):
  for i in range(0,3):
    encodevert(id, frame, (index*4)+i, objects[id[0]]["faces"][index][i])
  if len(objects[id[0]]["faces"][index]) == 4:
    encodevert(id, frame, (index*4)+3, objects[id[0]]["faces"][index][3])
  else:
    encodevert(id, frame, (index*4)+3, objects[id[0]]["faces"][index][1])

#encode all the data
for frame in range(0, nframes):
  print("encoding frame",frame+1,"of",nframes,"\t\t","{:.2f}".format((frame)/nframes*100),"%")
  id = [int(i) for i in frames[frame].split(" ")]
  for i in range(0, nfaces):
    encodeface(id, frame, i)

print("Done\t\t\t\t 100.00 %")
print("Saving...")
out.save(output[1]+".png")
out.close()
quit()
import argparse
import math
import json
from PIL import Image, ImageOps

#--------------------------------
#INPUT
#--------------------------------

import os, time
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames

Tk().withdraw()

path = os.getcwd()


#objs
objs = ["input/frame01.obj", "input/frame02.obj"]
objs = askopenfilenames(initialdir=path, filetypes=[('.obj','.obj')], title='Please select all .obj frames')
if len(objs) == 0:
  print("Canceled")
  time.sleep(1)
  exit()


#texture animations not supported yet
texs = ["input/texture.png"]
texs = askopenfilenames(initialdir=path, filetypes=[('.png','.png')], title='Please select all needed textures')
if len(texs) == 0:
  print("Canceled")
  time.sleep(1)
  exit()


#Manual display for frames
frames = ["0", "1"]
#Generated display for frames
frames = []
for i in range(0,len(objs)):
  frames.append(str(i))


#json, png
output = ["output/output.json", "output/output.png"]

def output_folder(name,export):
  dirpath = askdirectory(initialdir=path, title='Please select a directory for export the '+export)
  if not os.path.isdir(dirpath):
    print("Canceled")
    time.sleep(1)
    exit()
  else:
    return dirpath+"/"+name

name = input('Output name : ')
output = [output_folder(name+".json","models"), output_folder(name+".png","textures")]

#--------------------------------
#ADVANCED
#(changing these only changes data on texture, no need to replace model)
#--------------------------------

#Position/Scaling
# just adds & multiplies vertex positions before encoding, so you dont have to re export the model
offset = (0,0,0)
scale = 1

#duration of each frame in ticks
duration = 3

#Animation Easing
# 0: none
# 1: linear
# 2: in-out cubic
# 3: 4-point bezier
easing = 3

#Item Color Overlay Behavior
# defines the behavior of 3 bytes of rgb to rotation and animation frames,
# any 3 chars of 'x', 'y', 'z', 'a' is valid
# 'xyz' = rotate, 'a' = animation
# multiple rotation bytes increase accuracy on that axis
# for 'aaa', animation frames 0-8388607 are not autoplay. numbers past 8388608 defines starting frame to auto-play from with smooth interpolation (suso's idea)
# auto-play color can be calculated by: 8388608 + ((total duration + ([time query gametime] % 24000) - starting frame) % total duration)
colorbehavior = 'xyz'

#Auto Rotate
# attempt to estimate rotation with Normals, added to colorbehavior rotation.
# this is very jittery, best used for far away objects. For display purposes color defined rotation is much better.
autorotate = False

#Auto Play
# always interpolate frames, colorbehavior='aaa' overrides this.
autoplay = False

#Flip uv
#if your model renders but textures are not right try toggling this
#i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
flipuv = False

#--------------------------------
#argument parsing by kumitatepazuru
#respects above settings as default
parser = argparse.ArgumentParser(description='python script to convert .OBJ files into Minecraft, rendering them in game with a core shader.\nGithub: https://github.com/Godlander/objmc')
parser.add_argument('--objs', help='List of object files', nargs='*', default=objs)
parser.add_argument('--texs', help='Specify a texture file', nargs='*', default=texs)
parser.add_argument('--frames', help='List of obj indexes as keyframes', nargs='*', default=frames)
parser.add_argument('--out', type=str, help='Output json and png', nargs=2, default=output)
parser.add_argument('--offset', nargs=3, type=float, default=offset, help='Offset of model in xyz')
parser.add_argument('--scale', type=float, default=scale, help='Scale of model')
parser.add_argument('--duration', type=int, help="Duration of each frame in ticks", default=duration)
parser.add_argument('--easing', type=int, help="Animation easing, 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier", default=easing)
parser.add_argument('--colorbehavior', type=str, help="Item color overlay behavior, 'xyz' = rotate, 'a' = animation", default=colorbehavior)
parser.add_argument('--autorotate', action='store_true', help="Attempt to estimate rotation with Normals")
parser.add_argument('--autoplay', action='store_true', help="Always interpolate frames, colorbehavior='aaa' overrides this.")
parser.add_argument("--flipuv", action='store_true', help="Invert the texture to compensate for flipped UV")
args = parser.parse_args()
objs = args.objs
texs = args.texs
frames = args.frames
output = args.out
offset = args.offset
scale = args.scale
duration = args.duration
easing = args.easing
colorbehavior = args.colorbehavior
autorotate = args.autorotate != autorotate
autoplay = args.autoplay != autoplay
flipuv = args.flipuv != flipuv
#--------------------------------

NP = 5

#file extension optional
output[0] = output[0].replace("."+output[0].split(".")[-1],"")
output[1] = output[1].replace("."+output[1].split(".")[-1],"")

#input error checking
if len(frames) == 0:
  frames.append("0")
if duration < 1 or duration > 256:
  print("Duration must be between 1 and 256")
  quit()

tex = Image.open(texs[0])
x,y = tex.size
if x < 8:
  print("Minimum texture size is 8x")
  quit()

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
  if 'nfaces' in globals() and len(d["faces"]) != nfaces:
    print("\nerror: mismatched obj face count")
    quit()
  return d
#read obj
o = readobj(objs[0])

#calculate heights
ntextures = len(texs)
nframes = len(frames)
nfaces = len(o["faces"])
nvertices = nfaces*4
texheight = ntextures * y
uvheight = math.ceil(nfaces/x)
#meta = rgba: scale, hasnormal, easing, unused
#position = rgb, rgb, rgb
#normal = aaa
#uv = rg,ba
dataheight = (nframes * math.ceil(((NP*nvertices))/x)) + 1

#make height power of 2
ty = 1 + uvheight + texheight + dataheight
ty2 = 2
while ty2 < ty:
  ty2 *= 2
ty = ty2

#initial info
print("\nobjmc start-------------------")
print("faces: ", nfaces, ", vertices: ", nvertices, sep="")
print("uvheight: ", uvheight, ", texheight: ", texheight, ", dataheight: ", dataheight, ", totalheight: ", ty, sep="")
print("colorbehavior: ", colorbehavior, ", flipuv: ", flipuv, ", autorotate: ", autorotate, ", autoplay: ", autoplay, sep="")
if nframes > 1:
  print("frames: ", nframes, ", duration: ", duration," ticks", ", total: ", duration*nframes/20, " seconds", ", easing: ", easing, sep="")

#write to json model
model = open(output[0]+".json", "w")
#create out image with correct dimensions
out = Image.new("RGBA", (x, int(ty)), (0,0,0,0))

#parse color behavior
cb = 0
for i in range(3):
  cb*=4
  if colorbehavior[i] == 'x':
    cb += 0
  if colorbehavior[i] == 'y':
    cb += 1
  if colorbehavior[i] == 'z':
    cb += 2
  if colorbehavior[i] == 'a':
    cb += 3

#header:
#0: marker pix
out.putpixel((0,0), (12,34,56,78))
#1: autorotate, autoplay, colorbehavior, alpha bits for texsize and nvertices
alpha = 128 + (int(y%256>127)<<6) + (int(nvertices%256>127)<<5)
out.putpixel((1,0), (int(autorotate), int(autoplay), cb, alpha))
#2: texture size
out.putpixel((2,0), (int(x/256), x%256, int(y/256), 128+y%128))
#3: nvertices
out.putpixel((3,0), (int(nvertices/256/256/256)%256, int(nvertices/256/256)%256, int(nvertices/256)%256, 128+nvertices%128))
#4: nframes, ntextures, duration
out.putpixel((4,0), (nframes,ntextures,duration-1, 255))

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
  out.putpixel((posx, posy), (int(posx/256)%256, posx%256, (posy-1)%256, 255))
  return [(posx+0.1)*16/x, (posy+0.1)*16/ty, (posx+0.9)*16/x, (posy+0.9)*16/ty]
#create elements for model
js = {
  "textures": {
    "0": output[1].split("textures/")[-1]
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
def newelement(index):
  cube = {
    "from":[8,0,8],
    "to":[8.000001,0.000001,8.000001],
    "faces":{
      "north":{"uv":getuvpos(index),"texture":"#0","tintindex":0}
    }
  }
  js["elements"].append(cube)
#generate elements and uv header
for i in range(0, nfaces):
  newelement(i)

print("\rwriting json model", end='...')
model.write(json.dumps(js,separators=(',', ':')))
model.close()

#grab data from the list and convert to rgb
def getposition(obj, index):
  x = 8388608+((obj["positions"][index][0])*65536)*scale + offset[0]*65536
  y = 8388608+((obj["positions"][index][1])*65536)*scale + offset[1]*65536
  z = 8388608+((obj["positions"][index][2])*65536)*scale + offset[2]*65536
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
def getnormal(obj, index):
  r = int((obj["normals"][index][0]+1)*255/2)
  g = int((obj["normals"][index][1]+1)*255/2)
  b = int((obj["normals"][index][2]+1)*255/2)
  return [r,g,b]
def getuv(obj, index):
  x = (obj["uvs"][index][0])*65535
  y = (obj["uvs"][index][1])*65535
  r = int(x/256)%256
  g = int(x%256)
  b = int(y/256)%256
  a = int(y%256)
  return [r,g,b,a]
def getp(frame, index, offset):
  i = ((frame)*nvertices*NP)+(index*NP)+offset
  xx = i%x
  yy = int(1+uvheight+y+((i/x)))
  return (xx,yy)
#meta: textureid, easing, scale?, alpha bits
#position = rgb, rgb, rgb
#normal = aaa
#uv = rg,ba
def encodevert(obj, frame, index, face):
  #face:[pos,uv,norm]
  #init meta
  scale = 100
  alpha = 128
  #position and normal
  pos = getposition(obj, face[0])
  if len(face) == 2:
    norm = (0,255,0,255)
  else:
    norm = getnormal(obj, face[2])
  for i in range(0,3):
    alpha += int(norm[i]%256>127)<<(3-i) #move first bit of alpha
    na = 128+norm[i]%128
    out.putpixel(getp(frame, index, i+1), (pos[i][0],pos[i][1],pos[i][2],na))
  #uv
  uv = getuv(obj, face[1])
  alpha += int(uv[3]%256>127) #move first bit of alpha
  out.putpixel(getp(frame, index, 4), (uv[0],uv[1],uv[2],128+uv[3]%128))
  #meta: textureid, easing, scale?, alpha
  out.putpixel(getp(frame, index, 0), (0, easing, scale, alpha))

def encodeface(obj, frame, index):
  for i in range(0,3):
    encodevert(obj, frame, (index*4)+i, obj["faces"][index][i])
  if len(obj["faces"][index]) == 4:
    encodevert(obj, frame, (index*4)+3, obj["faces"][index][3])
  else:
    encodevert(obj, frame, (index*4)+3, obj["faces"][index][1])

#encode all the data
for frame in range(0, nframes):
  if frame % int(math.ceil(nframes/10)) == 0:
    print("\rencoding frame",frame+1,"of",nframes, end='...')
    print("\r\t\t\t\t\t","{:.2f}".format((frame+1)/nframes*100),"%", end='')
  obj = readobj(objs[int(frames[frame])])
  if len(obj["faces"]) != nfaces:
    print("mismatched obj face count")
    quit()
  for i in range(0, nfaces):
    encodeface(obj, frame, i)

print("\rDone                                     100.00 %")
print("Saving...")
out.save(output[1]+".png")
out.close()
quit()

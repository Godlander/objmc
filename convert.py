import argparse
import math
import json
import sys
import os
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as tkst
import tkinter.filedialog as tkfd
from PIL import Image, ImageOps

#--------------------------------
#INPUT
#--------------------------------

#objs
objs = ["cube.obj"]
#texture animations not supported yet
texs = ["cube.png"]

frames = ["0"]

#json, png
output = ["potion.json", "out.png"]

#--------------------------------
#ADVANCED
#(changing these only changes data on texture, no need to replace model)
#--------------------------------

#Position/Scaling
# just adds & multiplies vertex positions before encoding, so you dont have to re export the model
offset = (0,0,0)
scale = 1

#duration of each frame in ticks
duration = 20

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
#gui if no args
path = os.getcwd()
def settext(box,text):
  box.configure(state='normal')
  box.delete('1.0',tk.END)
  box.insert('1.0',text)
  box.configure(state='disabled')
def opentex():
  f = tkfd.askopenfilename(initialdir=path,title='Select Texture File',filetypes=[("Image File", ".png .jpg .jpeg .bmp")])
  global texs
  texs = [f.replace("\\","\\\\")]
  settext(texlist, os.path.basename(f))
def openobjs():
  f = tkfd.askopenfilenames(initialdir=path,title='Select Obj Files',filetypes=[("Obj Files", ".obj")])
  global objs, frames
  objs = list(f)
  frames = []
  for i in range(len(f)):
    frames.append(str(i))
  f = [os.path.basename(f) for f in f]
  settext(objlist, "\n".join(f))
def isnumber(s):
  return (s.isdigit() or s == "")
def start():
  if len(objs) == 0 or len(texs) == 0:
    print("No files selected")
    return
class Number(tk.Entry):
  def __init__(self, master=None, **kwargs):
    self.var = kwargs.pop('textvariable', None)
    self.var.set(str(duration))
    tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
    self.old_value = ''
    self.var.trace('w', self.check)
    self.get, self.set = self.var.get, self.var.set
  def check(self, *args):
    if self.get().isdigit() or self.get() == '':
      self.old_value = self.get()
    else:
      self.set(self.old_value)
if not len(sys.argv) > 1:
  print("No arguments given, starting gui")
  window = tk.Tk()
  window.title("objmc")
  window.geometry("400x300")
  window.minsize(400,300)
  window.rowconfigure(0,pad=7)
  window.rowconfigure(1,weight=1)
  window.rowconfigure(2,pad=7)
  window.columnconfigure(0,weight=1)
  window.columnconfigure(1,weight=1)
  #obj list
  tk.Button(window, text='Select Objs', command=openobjs).grid(column=0, row=0, sticky='NEW')
  objlist = tkst.ScrolledText(window, height=500)
  objlist.grid(column=0, row=1, sticky='NEW', padx=5)
  settext(objlist, "\n".join(objs))
  #tex list
  tk.Button(window, text='Select Texture', command=opentex).grid(column=1, row=0, sticky='NEW')
  texlist = tk.Text(window, height=1)
  texlist.grid(column=1, row=1, sticky='NEW', padx=5)
  settext(texlist, texs[0])
  flipuv = tk.BooleanVar()
  tk.Checkbutton(window, text="Flip UV", variable=flipuv).grid(column=1, row=1, sticky='NE')
  #start quit buttons
  qq = tk.BooleanVar()
  qq.set(True)
  def start():
    qq.set(False)
    window.destroy()
  buttonquit = tk.Button(window, text="Cancel", command=quit).grid(column=0, row=2, padx=5)
  buttonstart = tk.Button(window, text="Start", command=start).grid(column=1, row=2, padx=5)
  ttk.Separator(window, orient=tk.VERTICAL).grid(column=0, row=0, rowspan=2, sticky='NSE')
  #advanced
  ttk.Separator(window, orient=tk.HORIZONTAL).grid(column=1, row=1, sticky='NEW', pady=27)
  tk.Label(window, text="Advanced").grid(column=1, row=1, sticky='NEW', pady=30)
  ttk.Separator(window, orient=tk.HORIZONTAL).grid(column=1, row=1, sticky='NEW', pady=53)
  advanced = tk.Frame(window)
  advanced.columnconfigure(0, weight=1)
  advanced.columnconfigure(1, weight=1)
  advanced.grid(column=1, row=1, sticky='NESW', pady=(60,0))
  #duration
  tk.Label(advanced, text="Frame Duration:").grid(column=0, row=0, sticky='W')
  dur = tk.StringVar()
  Number(advanced, textvariable=dur, width=5).grid(column=1, row=0, sticky='EW', padx=(0,30))
  tk.Label(advanced, text="ticks").grid(column=1, row=0, sticky='E', padx=(0,25))
  #easing
  earr = ["None","Linear","Cubic","Bezier"]
  tk.Label(advanced, text="Easing Method:").grid(column=0, row=1, sticky='W')
  easing = tk.StringVar()
  easing.set("Linear")
  ttk.Combobox(advanced, values=earr, textvariable=easing, state='readonly', width=7).grid(column=1, row=1, sticky='W')
  #autorotate
  autorotate = tk.BooleanVar()
  tk.Checkbutton(advanced, text="Auto Rotate", variable=autorotate).grid(column=0, row=2)
  autoplay = tk.BooleanVar()
  tk.Checkbutton(advanced, text="Auto Play", variable=autoplay).grid(column=1, row=2)
  #color behavior
  cblabel = tk.Label(advanced, text="Color Behavior:").grid(column=0, row=3, sticky='W')
  cbarr = ["x", "y", "z", "a"]
  cb = [tk.StringVar() for i in range(3)]
  for i in range(3):
    cb[i].set(cbarr[i])
  cb1menu = ttk.Combobox(advanced, values=cbarr, textvariable=cb[0], width=1, state='readonly').grid(column=1, row=3, sticky='W', padx=(0,0))
  cb2menu = ttk.Combobox(advanced, values=cbarr, textvariable=cb[1], width=1, state='readonly').grid(column=1, row=3, sticky='W', padx=(28,0))
  cb3menu = ttk.Combobox(advanced, values=cbarr, textvariable=cb[2], width=1, state='readonly').grid(column=1, row=3, sticky='W', padx=(56,0))
  #output
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=4, columnspan=2, sticky='EW', pady=(7,0))
  tk.Label(advanced, text="Output:").grid(column=0, row=5, columnspan=2)
  outjson = tk.StringVar()
  outpng = tk.StringVar()
  outjson.set(output[0].replace(".json", ""))
  outpng.set(output[1].replace(".png", ""))
  tk.Entry(advanced, textvariable=outjson, width=10).grid(column=0, row=6, columnspan=2, sticky='NEW', padx=(5,10))
  tk.Label(advanced, text=".json").grid(column=1, row=6, sticky='NE')
  tk.Entry(advanced, textvariable=outpng, width=10).grid(column=0, row=7, columnspan=2, sticky='NEW', padx=5)
  tk.Label(advanced, text=".png").grid(column=1, row=7, sticky='NE')

  window.mainloop()
  if qq.get():
    quit()
  if dur.get().isdigit():
    duration = max(int(dur.get()), 1)
  else:
    duration = 1
  easing = earr.index(easing.get())
  flipuv = flipuv.get()
  autorotate = autorotate.get()
  autoplay = autoplay.get()
  colorbehavior = cb[0].get() + cb[1].get() + cb[2].get()
  output = [outjson.get(), outpng.get()]
#--------------------------------

NP = 5

#file extension optional
output[0] = output[0].split(".")[0]
output[1] = output[1].split(".")[0]

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
  obj = open(name, "r")
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
    print("\nerror: mismatched obj face count, exiting...")
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
    "0": output[1]
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
    print("\rEncoding frame",frame+1,"of",nframes, end='...')
    print("\r\t\t\t\t\t","{:.2f}".format((frame+1)/nframes*100),"%", end='')
  obj = readobj(objs[int(frames[frame])])
  if len(obj["faces"]) != nfaces:
    print("mismatched obj face count")
    quit()
  for i in range(0, nfaces):
    encodeface(obj, frame, i)

print("\rSaving files...                          100.00 %")
out.save(output[1]+".png")
out.close()
print("Complete")
quit()
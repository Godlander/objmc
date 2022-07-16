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

#array of frame indexes
#defaults to [0-nframes]
frames = []

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
# for 'aaa', autoplay is automatically on. numbers past 8388608 define paused frame to display (suso's idea)
# auto-play color can be calculated by: ((([time query gametime] % 24000) - starting frame) % total duration)
colorbehavior = 'xyz'

#Auto Rotate
# attempt to estimate rotation with Normals, added to colorbehavior rotation.
# this is very jittery, best used for far away objects. For display purposes color defined rotation is much better.
autorotate = 0

#Auto Play
# always interpolate frames, colorbehavior='aaa' overrides this.
autoplay = False

#Flip uv
#if your model renders but textures are not right try toggling this
#i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
flipuv = False

#No Shadow
#disable face normal shading
#can be used for models with lighting baked into the texture
#lightmap color still applies
noshadow = False

#No power of two textures
#i guess saves a bit of space maybe
#makes it not optifine compatible
nopow = False

#--------------------------------
#argument parsing by kumitatepazuru
#respects above settings as default
parser = argparse.ArgumentParser(description='python script to convert .OBJ files into Minecraft, rendering them in game with a core shader.\nGithub: https://github.com/Godlander/objmc')
parser.add_argument('--objs', help='List of object files', nargs='*', default=objs)
parser.add_argument('--texs', help='Specify a texture file', nargs='*', default=texs)
parser.add_argument('--frames', type=int, help='List of obj indexes as keyframes', nargs='*', default=[])
parser.add_argument('--out', type=str, help='Output json and png', nargs=2, default=output)
parser.add_argument('--offset', type=float, help='Offset of model in xyz', nargs=3, default=offset)
parser.add_argument('--scale', type=float, default=scale, help='Scale of model')
parser.add_argument('--duration', type=int, help="Duration of each frame in ticks", default=duration)
parser.add_argument('--easing', type=int, help="Animation easing, 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier", default=easing)
parser.add_argument('--colorbehavior', type=str, help="Item color overlay behavior, 'xyz' = rotate, 'a' = animation time offset, 'o' = overlay hue", default=colorbehavior)
parser.add_argument('--autorotate', type=int, help="Attempt to estimate rotation with Normals, 0: off, 1: x, 2:y, 3:xy", default=autorotate)
parser.add_argument('--autoplay', action='store_true', help="Always interpolate frames, colorbehavior='aaa' overrides this.")
parser.add_argument("--flipuv", action='store_true', help="Invert the texture to compensate for flipped UV")
parser.add_argument("--noshadow", action='store_true', help="Disable shadows from face normals")
parser.add_argument("--nopow", action='store_true', help="Disable power of two textures")
args = parser.parse_args()
objs = args.objs
texs = args.texs
frames = args.frames
output = args.out
offset = tuple(args.offset)
scale = args.scale
duration = args.duration
easing = args.easing
colorbehavior = args.colorbehavior
autorotate = args.autorotate
autoplay = args.autoplay != autoplay
flipuv = args.flipuv != flipuv
noshadow = args.noshadow != noshadow
nopow = args.nopow != nopow
if not frames:
  for i in range(len(objs)):
    frames.append(i)

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
    frames.append(i)
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
def isFloat(string):
    if string == '' or string == '-':
        return True
    try:
        float(string)
        return True
    except ValueError:
        return False
class Floatbox(tk.Entry):
  def __init__(self, master=None, **kwargs):
    self.var = kwargs.pop('textvariable', None)
    self.var.set("0.0")
    tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
    self.old_value = ''
    self.var.trace('w', self.check)
    self.get, self.set = self.var.get, self.var.set
  def check(self, *args):
    if isFloat(self.get()) or self.get() == '':
      self.old_value = self.get()
    else:
      self.set(self.old_value)
if not len(sys.argv) > 1:
  print("No arguments given, starting gui")
  window = tk.Tk()
  window.title("objmc")
  window.geometry("1x1")
  window.minsize(500,400)
  window.rowconfigure(0,pad=7)
  window.rowconfigure(1,weight=1)
  window.rowconfigure(2,pad=7)
  window.columnconfigure(0,weight=8)
  window.columnconfigure(1,weight=9)
  #obj list
  tk.Button(window, text='Select Objs', command=openobjs, borderwidth=5).grid(column=0, row=0, sticky='NEW')
  objlist = tkst.ScrolledText(window, height=500)
  objlist.grid(column=0, row=1, rowspan=3, sticky='NEW', padx=5)
  settext(objlist, "\n".join(objs))
  ttk.Separator(window, orient=tk.VERTICAL).grid(column=0, row=0, rowspan=4, sticky='NSE')
  #tex list
  tk.Button(window, text='Select Texture', command=opentex, borderwidth=5).grid(column=1, row=0, sticky='NEW')
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
  buttonquit = tk.Button(window, text="Cancel", command=quit).grid(column=0, row=4, padx=5, pady=5)
  buttonstart = tk.Button(window, text="Start", command=start).grid(column=1, row=4, padx=5, pady=5)
  ttk.Separator(window, orient=tk.HORIZONTAL).grid(column=1, row=1, sticky='NEW', pady=(25,0))
  #scale and offset
  of = [tk.StringVar() for i in range(3)]
  offsetlable = tk.Label(window, text="Offset:").grid(column=1, row=1, sticky='N', padx=(0,110), pady=(32,0))
  offset1 = Floatbox(window, width=5, textvariable=of[0]).grid(column=1, row=1, sticky='N', padx=(0,30), pady=(32,0))
  offset2 = Floatbox(window, width=5, textvariable=of[1]).grid(column=1, row=1, sticky='N', padx=(40,0), pady=(32,0))
  offset3 = Floatbox(window, width=5, textvariable=of[2]).grid(column=1, row=1, sticky='N', padx=(110,0), pady=(32,0))
  scalelable = tk.Label(window, text="Scale:").grid(column=1, row=1, sticky='N', padx=(0,110), pady=(55,0))
  scale = tk.StringVar()
  scalebox = Floatbox(window, width=17, textvariable=scale).grid(column=1, row=1, sticky='N', padx=(40,0), pady=(55,0))
  scale.set("1.0")
  #noshadow
  noshadow = tk.BooleanVar()
  tk.Checkbutton(window, text="No Shadow", variable=noshadow).grid(column=1, row=1, sticky='N', pady=(77,0))
  #advanced
  ttk.Separator(window, orient=tk.HORIZONTAL).grid(column=1, row=0, sticky='NEW')
  advanced = tk.Frame(window)
  advanced.columnconfigure(0, weight=1)
  advanced.columnconfigure(1, weight=1)
  advanced.grid(column=1, row=3, sticky='NESW')
  tk.Label(advanced, text="Advanced").grid(column=0, row=0, columnspan=2, sticky='EW', pady=(0,5))
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=0, columnspan=2, sticky='NEW')
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=0, columnspan=2, sticky='NEW', pady=(25,5))
  #duration
  tk.Label(advanced, text="Frame Duration:").grid(column=0, row=1, sticky='W', padx=(5,0))
  dur = tk.StringVar()
  Number(advanced, textvariable=dur, width=5).grid(column=1, row=1, sticky='EW', padx=(0,30))
  tk.Label(advanced, text="ticks").grid(column=1, row=1, sticky='E', padx=(0,25))
  #easing
  earr = ["None","Linear","Cubic","Bezier"]
  tk.Label(advanced, text="Easing Method:").grid(column=0, row=2, sticky='W', padx=(5,0), pady=(2,0))
  easing = tk.StringVar()
  easing.set("Linear")
  ttk.Combobox(advanced, values=earr, textvariable=easing, state='readonly', width=7).grid(column=1, row=2, pady=(2,0), sticky='W')
  #autorotate
  rarr = ["Off","Yaw","Pitch","Both"]
  tk.Label(advanced, text="Auto Rotate:").grid(column=0, row=3, sticky='W', padx=(5,0), pady=(2,0))
  autorotate = tk.StringVar()
  autorotate.set("Off")
  ttk.Combobox(advanced, values=rarr, textvariable=autorotate, state='readonly', width=7,).grid(column=1, row=3, pady=(2,0), sticky='W')
  #autoplay
  autoplay = tk.BooleanVar()
  tk.Checkbutton(advanced, text="Auto Play", variable=autoplay).grid(column=0, row=4, columnspan=2, sticky='N')
  #color behavior
  cblabel = tk.Label(advanced, text="Color Behavior:").grid(column=0, row=5, sticky='W', padx=(5,0))
  cbarr = ['x', 'y', 'z', 't']
  cbarr2 = ['x', 'y', 'z', 't', 'o']
  cb = [tk.StringVar() for i in range(3)]
  for i in range(3):
    cb[i].set(cbarr[i])
  cb1menu = ttk.Combobox(advanced, values=cbarr, textvariable=cb[0], width=1, state='readonly').grid(column=1, row=5, sticky='W', padx=(0,0))
  cb2menu = ttk.Combobox(advanced, values=cbarr, textvariable=cb[1], width=1, state='readonly').grid(column=1, row=5, sticky='W', padx=(28,0))
  cb3menu = ttk.Combobox(advanced, values=cbarr2, textvariable=cb[2], width=1, state='readonly').grid(column=1, row=5, sticky='W', padx=(56,0))
  #output
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=6, columnspan=2, sticky='EW', pady=(7,0))
  tk.Label(advanced, text="Output:").grid(column=0, row=7, columnspan=2)
  outjson = tk.StringVar()
  outpng = tk.StringVar()
  outjson.set(output[0].replace(".json", ""))
  outpng.set(output[1].replace(".png", ""))
  tk.Entry(advanced, textvariable=outjson, width=10).grid(column=0, row=8, columnspan=2, sticky='NEW', padx=(5,10))
  tk.Label(advanced, text=".json").grid(column=1, row=8, sticky='NE')
  tk.Entry(advanced, textvariable=outpng, width=10).grid(column=0, row=9, columnspan=2, sticky='NEW', padx=5)
  tk.Label(advanced, text=".png").grid(column=1, row=9, sticky='NE')
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=10, columnspan=2, sticky='NEW', pady=(5,0))

  window.mainloop()
  if qq.get():
    exit()
  if dur.get().isdigit():
    duration = max(int(dur.get()), 1)
  else:
    duration = 1
  offset = (float(of[0].get()), float(of[1].get()), float(of[2].get()))
  scale = float(scale.get())
  easing = earr.index(easing.get())
  flipuv = flipuv.get()
  noshadow = noshadow.get()
  autorotate = rarr.index(autorotate.get())
  autoplay = autoplay.get()
  colorbehavior = cb[0].get() + cb[1].get() + cb[2].get()
  output = [outjson.get(), outpng.get()]
#--------------------------------
os.system('color')
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
def exit():
  print("Press any key to exit...")
  os.system('pause >nul')
  quit()

#file extension optional
output[0] = output[0].split(".")[0]
output[1] = output[1].split(".")[0]

#input error checking
if duration < 1 or duration > 256:
  print(col.err+"duration must be between 1 and 256"+col.end)
  exit()

tex = Image.open(texs[0])
x,y = tex.size
if x < 8:
  print(col.err+"minimum texture size is 8x"+col.end)
  exit()

def readobj(name):
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
  if 'nfaces' in globals() and len(d["faces"]) != nfaces:
    print(col.err+"mismatched obj face count"+col.end)
    exit()
  return d

count = [0,0]
mem = {"positions":{},"uvs":{}}
data = {"positions":[],"uvs":[],"vertices":[]}
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
def indexobj(o, frame):
  global nframes
  global nfaces
  for face in range(0, len(o["faces"])):
    if face % 1000 == 0:
      print("\Reading obj ", frame+1, " of ", nframes, "...", "{:>15.2f}".format((frame*nfaces+face)*100/(nframes*nfaces)), "%\033[K", sep="", end="\r")
    face = o["faces"][face]
    for vert in face:
      indexvert(o, vert)
    if len(face) == 3:
      indexvert(o, face[1])

ntextures = len(texs)
nframes = len(frames)

print("\n"+col.cyan+"objmc start ------------------"+col.end)
#read obj
print("Reading obj 1 of ", nframes, "...", "{:>15.2f}".format(0), "%\033[K", sep="", end="\r")
o = readobj(objs[0])
nfaces = len(o["faces"])
indexobj(o, 0)
if nframes > 1:
  for frame in range(1, nframes):
    o = readobj(objs[frames[frame]])
    indexobj(o, frame)

nvertices = nfaces*4
texheight = ntextures * y
uvheight = math.ceil(nfaces/x)
vpheight = math.ceil(len(data["positions"])*3/x)
vtheight = math.ceil(len(data["uvs"])*2/x)
vheight = math.ceil(len(data["vertices"])*2/x)
#make height power of 2
ty = 1 + uvheight + texheight + vpheight + vtheight + vheight
if not nopow:
 ty = 1<<(ty - 1).bit_length()
if (ty > 4096 and x < 4096) or (ty > 8*x):
  print(col.warn+"output height may be too high, consider increasing width of input texture or reducing number of frames to bring the output texture closer to a square."+col.end)

#initial info
print("%\033[K", end="\r")
print("faces: ", nfaces, ", verts: ", nvertices, ", tex: ", (x,y), sep="")
if nframes > 1:
  print("frames: ", nframes, ", duration: ", duration,"t", ", time: ", duration*nframes/20, "s", ", easing: ", easing, ", autoplay: ", autoplay,  sep="")
print("uvhead: ", uvheight, ", vph: ", vpheight, ", vth: ", vtheight, ", vh: ", vheight, ", total: ", ty, sep="")
print("colorbehavior: ", colorbehavior, ", flipuv: ", flipuv, ", autorotate: ", autorotate, sep="")
print("offset: ", offset, ", scale: ", scale, ", noshadow: ", noshadow, sep="")

print("Creating Files...", end="\r")
#write to json model
model = open(output[0]+".json", "w")
#create out image with correct dimensions
out = Image.new("RGBA", (x, int(ty)), (0,0,0,0))

#parse color behavior
ca = [cbarr2.index(i) for i in colorbehavior]
cb = (ca[0]<<6) + (ca[1]<<4) + (ca[2])

#first alpha bit for texture height, nvertices, vtheight
alpha = 128 + (int(y%256/128)<<6) + (int(nvertices%256/128)<<5) + (int(vtheight%256/128)<<4)
#header:
#0: marker pix
out.putpixel((0,0), (12,34,56,78))
#1: noshadow, autorotate, colorbehavior, alpha bits for texsize and nvertices
out.putpixel((1,0), ((int(noshadow)<<7) + (int(autorotate)<<5), 0, cb, alpha))
#2: texture size
out.putpixel((2,0), (int(x/256), x%256, int(y/256), 128+y%128))
#3: nvertices
out.putpixel((3,0), (int(nvertices/16777216)%256, int(nvertices/65536)%256, int(nvertices/256)%256, 128+nvertices%128))
#4: nframes, ntextures, duration, autoplay, easing
out.putpixel((4,0), (nframes,ntextures,duration-1, 128+(int(autoplay)<<6)+easing))
#5: data heights
out.putpixel((5,0), (int(vpheight/256)%256, int(vpheight)%256, int(vtheight/256)%256, 128+vtheight%128))

#actual texture
for i in range (0,len(texs)):
  tex = Image.open(texs[i])
  nx,ny = tex.size
  if nx != x or ny != y:
    print(col.err+"mismatched texture sizes"+col.end)
    exit()
  if flipuv:
    out.paste(tex, (0,1+uvheight+(i*y)))
  else:
    out.paste(ImageOps.flip(tex), (0,1+uvheight+(i*y)))

#unique pixel uv per face with color pointing to topleft
def getuvpos(faceid):
  posx = faceid%x
  posy = math.floor(faceid/x)+1
  out.putpixel((posx, posy), (int(posx/256)%256, posx%256, (posy-1)%256, 255-(int((posy-1)/256)%256)))
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

print("Writing json model...\033[K", end="\r")
model.write(json.dumps(js,separators=(',',':')))
model.close()

#grab data from the list and convert to rgb
def getposition(i):
  x = 8388608+((data["positions"][i][0])*65280)*scale + offset[0]*65280
  y = 8388608+((data["positions"][i][1])*65280)*scale + offset[1]*65280
  z = 8388608+((data["positions"][i][2])*65280)*scale + offset[2]*65280
  rgb = []
  rgb.append((int((x/65280)%256), int((x/255)%256), int(x%256), 255))
  rgb.append((int((y/65280)%256), int((y/255)%256), int(y%256), 255))
  rgb.append((int((z/65280)%256), int((z/255)%256), int(z%256), 255))
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

print("Writing position data...\033[K", end="\r")
y = 1 + uvheight + texheight
for i in range(0,len(data["positions"])):
  a = getposition(i)
  for j in range(0,3):
    p = i*3+j
    out.putpixel((p%x,y+math.floor(p/x)), a[j])
print("Writing uv data...\033[K", end="\r")
y = 1 + uvheight + texheight + vpheight
for i in range(0,len(data["uvs"])):
  a = getuv(i)
  for j in range(0,2):
    p = i*2+j
    out.putpixel((p%x,y+math.floor(p/x)), a[j])
print("Writing vertex data...\033[K", end="\r")
y = 1 + uvheight + texheight + vpheight + vtheight
for i in range(0,len(data["vertices"])):
  a = getvert(i)
  for j in range(0,2):
    p = i*2+j
    out.putpixel((p%x,y+math.floor(p/x)), a[j])

print("Saving files...\033[K", end="\r")
out.save(output[1]+".png")
out.close()
print(col.green+"Complete ---------------------"+col.end)
exit()
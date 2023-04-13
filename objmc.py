import sys
import os
os.system('mode con: cols=60 lines=30')
os.system("title objmc output")
os.system('color')
import math
import json
import argparse
from PIL import Image, ImageOps
from tkinter import ttk
import tkinter as tk
import tkinter.scrolledtext as tkst
import tkinter.filedialog as tkfd

#--------------------------------
#INPUT
#--------------------------------

#objs
objs = [""]
#textures
texs = [""]

#Output json & png
output = ["potion.json", "block/out.png"]

#Position & Scaling
# just adds & multiplies vertex positions before encoding, so you dont have to re export the model
offset = (0.0,0.0,0.0)
scale = 1.0

#Duration of the animation in ticks
duration = 20

#Animation Easing
# 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier
easing = 3

#Texture Interpolation
# 0: none, 1: linear
interpolation = 1

#Color Behavior
# defines the behavior of 3 bytes of rgb to rotation and animation frames,
# any 3 of 'pitch', 'yaw', 'roll', '
# multiple rotation bytes increase accuracy on that axis
# when all 3 are 'time', autoplay is automatically on. numbers past 8388608 define paused frame to display (suso's idea)
# auto-play color can be calculated by: ((([time query gametime] % 24000) - starting frame) % total duration)
colorbehavior = ['pitch', 'yaw', 'roll']

#Auto Rotate
# attempt to estimate rotation with Normals, added to colorbehavior rotation.
# one axis is ok but both is jittery. For display purposes color defined rotation is better.
# 0: none, 1: yaw, 2: pitch, 3: both
autorotate = 1

#Auto Play
# always interpolate frames, colorbehavior of all 'time' overrides this.
autoplay = False

#Flip uv
# if your model renders but textures are not right try toggling this
# i find that blockbench ends up flipping uv, but blender does not. dont trust me too much on this tho i have no idea what causes it.
flipuv = False

#No Shadow
# disable face normal shading (lightmap color still applies)
# can be used for models with lighting baked into the texture
noshadow = False

#Visibility
# determins where the model is visible
# 3 bits for: world, hand, gui
visibility = 7

#No power of two textures
nopow = True

#Joining multiple models
join = []
#--------------------------------
#argument parsing by kumitatepazuru
#respects above settings as default
class ArgumentParserError(Exception): pass
class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
parser = ThrowingArgumentParser(description="python script to convert .OBJ files into Minecraft, rendering them in game with a core shader.\nGithub: https://github.com/Godlander/objmc")
parser.add_argument("--objs", help="List of object files", nargs='*', default=objs)
parser.add_argument("--texs", help="Specify a texture file", nargs='*', default=texs)
parser.add_argument("--out", type=str, help="Output json and png", nargs=2, default=output)
parser.add_argument("--offset", type=float, help="Positional offset of model", nargs=3, default=offset)
parser.add_argument("--scale", type=float, help="Scale of model", default=scale)
parser.add_argument("--duration", type=int, help="Duration of the animation in ticks", default=duration)
parser.add_argument("--easing", type=int, help="Animation easing, 0: none, 1: linear, 2: in-out cubic, 3: 4-point bezier", default=easing)
parser.add_argument("--interpolation", type=int, help="Texture interpolation, 0: none, 1: fade", default=interpolation)
parser.add_argument("--colorbehavior", type=str, nargs=3, help="Item color overlay behavior: 'pitch', 'yaw', 'roll', 'time', 'scale', 'overlay'.", default=colorbehavior)
parser.add_argument("--autorotate", type=int, help="Attempt to estimate rotation with Normals, 0: off, 1: yaw, 2: pitch, 3: both", default=autorotate)
parser.add_argument("--autoplay", action="store_true", dest="autoplay", help="Always interpolate animation, colorbehavior of all 'time' overrides this")
parser.add_argument("--visibility", type=int, help="Determines where the model is visible", default=visibility)
parser.add_argument("--flipuv", action="store_true", dest="flipuv", help="Invert the texture to compensate for flipped UV")
parser.add_argument("--noshadow", action="store_true", dest="noshadow", help="Disable shadows from face normals")
parser.add_argument("--nopow", action="store_true", dest="nopow", help="Disable power of two textures")
parser.add_argument("--join", nargs='*', dest="join", help="Joins multiple json models into one")
def getargs(args):
  global objs
  global texs
  global output
  global offset
  global scale
  global duration
  global easing
  global interpolation
  global colorbehavior
  global autorotate
  global autoplay
  global visibility
  global flipuv
  global noshadow
  global nopow
  global join
  objs = args.objs
  texs = args.texs
  output = args.out
  offset = tuple(args.offset)
  scale = args.scale
  duration = args.duration
  easing = args.easing
  interpolation = args.interpolation
  colorbehavior = args.colorbehavior
  autorotate = args.autorotate
  autoplay = args.autoplay
  visibility = args.visibility
  flipuv = args.flipuv
  noshadow = args.noshadow
  nopow = args.nopow
  join = args.join
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
      indexvert(o, face[1])

#unique pixel uv per face with color pointing to topleft
def getheader(out, faceid, x, y, ty):
  posx = faceid%x
  posy = math.floor(faceid/x)+1
  out.putpixel((posx, posy), (int(posx/256)%256, posx%256, int(posy/256)%256, posy%256))
  return [(posx+0.1)*16/x, (posy+0.1)*16/ty, (posx+0.9)*16/x, (posy+0.9)*16/ty]
#create elements for model
js = {}
def newelement(out, index, x, y, ty):
  cube = {
    "from":[8,0,8],
    "to":[8.000001,0.000001,8.000001],
    "faces":{
      "north":{"uv":getheader(out, index, x, y, ty),"texture":"#0","tintindex":0}
    }
  }
  js["elements"].append(cube)

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
def strcontext(objs, texs, output, scale, offset, duration, easing, interpolation, colorbehavior, autorotate, autoplay, flipuv, noshadow, nopow):
  s = ""
  s += "--objs " + ' '.join(objs)
  s += " --texs " + ' '.join(texs)
  s += " --out " + ' '.join(output)
  s += " --offset " + ' '.join(str(i) for i in offset)
  s += " --scale " + str(scale)
  s += " --duration " + str(duration)
  s += " --easing " + str(easing)
  s += " --interpolation " + str(interpolation)
  s += " --colorbehavior " + ' '.join(colorbehavior)
  s += " --autorotate " + str(autorotate)
  if autoplay:
    s += " --autoplay"
  if flipuv:
    s += " --flipuv"
  if noshadow:
    s += " --noshadow"
  if nopow:
    s += " --nopow"
  return s
def getcontext(c):
  a = []
  try:
    a = parser.parse_args(c.split(' '))
  except:
    print(col.err+"Invalid command: "+col.end+c)
    return
  getargs(a)
  setval()
#--------------------------------
hid = 0
history = []
runtex = ""
def objmc(objs, texs, output, sc, off, duration, easing, interpolation, colorbehavior, autorotate, autoplay, flipuv, noshadow, nopow):
  global offset
  global scale
  offset = off
  scale = sc
  global count
  global mem
  global data
  count = [0,0]
  mem = {"positions":{},"uvs":{}}
  data = {"positions":[],"uvs":[],"vertices":[]}

  #file extension optional
  if (output[0][-5:] != ".json"):
   output[0] += ".json"
  if (output[1][-4:] != ".png"):
   output[1] += ".png"

  #input error checking
  if duration < 1 or duration > 256:
    print(col.err+"duration must be between 1 and 256"+col.end)
    exit()
  tex = Image.open(texs[0])
  x,y = tex.size
  if x < 8:
    print(col.err+"minimum texture size is 8x8"+col.end)
    exit()

  ntextures = len(texs)
  nframes = len(objs)

  print("\n"+col.cyan+"objmc start "+runtex+col.end)
  #read obj
  print("Reading obj 1 of ", nframes, "...", "{:>15.2f}".format(0), "%\033[K", sep="", end="\r")
  o = readobj(objs[0], 0)
  nfaces = len(o["faces"])
  indexobj(o, 0, nframes, nfaces)
  if nframes > 1:
    for frame in range(1, nframes):
      o = readobj(objs[frame], nfaces)
      indexobj(o, frame, nframes, nfaces)

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
    print(col.warn+"output height may be too high, consider increasing width of input texture or reducing number of frames to bring the output texture closer to a square."+col.  end)

  #parse color behavior
  cbarr = ['pitch', 'yaw', 'roll', 'time', 'scale', 'overlay']
  ca = [cbarr.index(i) for i in colorbehavior]
  cb = ((ca[0]<<6) + (ca[1]<<3) + (ca[2]))

  #initial info
  print("%\033[K", end="\r")
  print("faces: ", nfaces, ", verts: ", nvertices, ", tex: ", (x,y), ", flipuv: ", flipuv, sep="")
  if nframes > 1 or ntextures > 1:
    print("objs: ", nframes, ", easing: ", easing, sep="")
    print("texs: ", ntextures, ", interpolation: ", interpolation, sep="")
    print("duration: ", duration,"t", ", ", duration/20, "s, autoplay: ", autoplay, sep="")
  print("uvhead: ", uvheight, ", vph: ", vpheight, ", vth: ", vtheight, ", vh: ", vheight, ", total: ", ty, sep="")
  print("colorbehavior: ", " ".join(colorbehavior), " (", cb, ")", ", autorotate: ", autorotate, sep="")
  print("offset: ", offset, ", scale: ", scale, ", noshadow: ", noshadow, sep="")
  print("visible:", " world" if visibility & 4 > 0 else "", " hand" if visibility & 2 > 0 else "", " gui" if visibility & 1 > 0 else "", sep="")
  print("Creating Files...", end="\r")
  #write to json model
  model = open(output[0], "w")
  #create out image with correct dimensions
  out = Image.new("RGBA", (x, int(ty)), (0,0,0,0))

  # header
  #| 2^32   | 2^16x2   | 2^32      | 2^24 + 2^8   | 2^24    + \1 2^1  + 2^2   + 2^2  \2| 2^16x2       | 2^1     + 2^2       + 2^3    \1 + 2^1 + 2^8   \16|
  #| marker | tex size | nvertices | nobjs, ntexs | duration, autoplay, easing, interp | data heights | noshadow, autorotate, visibility, colorbehavior  |
  #0: marker
  out.putpixel((0,0), (12,34,56,78))
  #1: texsize
  out.putpixel((1,0), (int(x/256), x%256, int(y/256), y%256))
  #2: nvertices
  out.putpixel((2,0), (int(nvertices/16777216)%256, int(nvertices/65536)%256, int(nvertices/256)%256, nvertices%256))
  #3: nobjs, ntexs
  out.putpixel((3,0), (int(nframes/65536)%256, int(nframes/256)%256, nframes%256, ntextures))
  #4: duration, autoplay, easing
  out.putpixel((4,0), (int(duration/65536)%256, int(duration/256)%256, duration%256, 128+(int(autoplay)<<6)+(easing<<4)+(interpolation<<2)))
  #5: data heights
  out.putpixel((5,0), (int(vpheight/256)%256, int(vpheight)%256, int(vtheight/256)%256, vtheight%256))
  #6: noshadow, autorotate, visibility, colorbehavior
  out.putpixel((6,0), ((int(noshadow)<<7)+(autorotate<<5)+(visibility<<2) + int(cb/256), cb%256, 255))

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

  #generate json model elements and uv header
  global js
  js = {
    "textures": {
      "0": output[1].split('.')[0]
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
    newelement(out, i, x, y, ty)

  print("Writing json model...\033[K", end="\r")
  model.write(json.dumps(js,separators=(',',':')))
  model.close()

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
  out.save(output[1].split('/')[-1])
  out.close()
  print(col.green+"Complete\033[K"+col.end)

#--------------------------------
#gui if no args
path = os.getcwd()
def settext(box,text):
  box.configure(state='normal')
  box.delete('1.0',tk.END)
  box.insert('1.0',text)
  box.configure(state='disabled')
def opentex():
  f = tkfd.askopenfilenames(initialdir=path,title='Select Texture Files',filetypes=[("Image File", ".png .jpg .jpeg .bmp")])
  global texs
  texs = list(f)
  f = [os.path.basename(f) for f in f]
  settext(texlist, "\n".join(f))
def openobjs():
  f = tkfd.askopenfilenames(initialdir=path,title='Select Obj Files',filetypes=[("Obj Files", ".obj")])
  global objs
  objs = list(f)
  f = [os.path.basename(f) for f in f]
  settext(objlist, "\n".join(f))
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
  window = tk.Tk()
  window.title("objmc")
  ico = tk.PhotoImage(data="""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""")
  window.tk.call('wm', 'iconphoto', window._w, ico)
  window.geometry("1x1")
  window.minsize(700,450)
  window.rowconfigure(0,pad=7)
  window.rowconfigure(1,weight=1)
  window.rowconfigure(2,weight=1)
  window.rowconfigure(3,weight=1)
  window.columnconfigure(0,weight=1)
  window.columnconfigure(1,weight=1)
  #obj list
  tk.Button(window, text='Select Objs', command=openobjs, borderwidth=3).grid(column=0, row=0, padx=(5,20), pady=(5,0),sticky='NEW')
  objlist = tkst.ScrolledText(window, height=500)
  objlist.grid(column=0, row=1, rowspan=3, sticky='NEW', padx=5)
  #tex list
  tk.Button(window, text='Select Textures', command=opentex, borderwidth=3).grid(column=1, row=0, padx=(5,65), pady=(5,0), sticky='NEW')
  fu = tk.BooleanVar()
  tk.Checkbutton(window, text="Flip UV", variable=fu).grid(column=1, row=0, sticky='NES')
  texlist = tkst.ScrolledText(window, height=500)
  texlist.grid(column=1, row=1, rowspan=3, sticky='NEW', padx=5)

  #options
  ttk.Separator(window, orient=tk.VERTICAL).grid(column=1, row=0, rowspan=4, sticky='NSE')
  tk.Label(window, text="Options").grid(column=2, row=0, sticky='NESW')
  ttk.Separator(window, orient=tk.HORIZONTAL).grid(column=2, row=1, sticky='NEW')

  #basic
  basic = tk.Frame(window)
  basic.columnconfigure(0, weight=1)
  basic.columnconfigure(1, weight=1)
  basic.columnconfigure(2, weight=1)
  basic.columnconfigure(3, weight=1)
  basic.columnconfigure(4, weight=2)
  basic.grid(column=2, row=1, sticky='EW')
  #scale and offset
  of = [tk.StringVar() for i in range(3)]
  tk.Label(basic, text="Offset:").grid(column=0, row=0, sticky='E', padx=(10))
  Floatbox(basic, width=5, textvariable=of[0]).grid(column=1, row=0, sticky='NESW')
  Floatbox(basic, width=5, textvariable=of[1]).grid(column=2, row=0, sticky='NESW')
  Floatbox(basic, width=5, textvariable=of[2]).grid(column=3, row=0, sticky='NESW')
  tk.Label(basic, text="Scale:").grid(column=0, row=1, sticky='E', padx=(10))
  sc = tk.StringVar()
  Floatbox(basic, width=17, textvariable=sc).grid(column=1, row=1, columnspan=3, sticky='NESW')
  #noshadow
  ns = tk.BooleanVar()
  tk.Checkbutton(basic, text="No Shadow", variable=ns).grid(column=0, row=2, columnspan=4, padx=(20,0))
  #autorotate
  ar = tk.StringVar()
  rarr = ["Off","Yaw","Pitch","Both"]
  tk.Label(basic, text="Auto Rotate:").grid(column=0, row=3, columnspan=2, sticky='E', padx=(10))
  ttk.Combobox(basic, values=rarr, textvariable=ar, state='readonly', width=7).grid(column=2, row=3, columnspan=2, sticky='W')
  #advanced
  advanced = tk.Frame(window)
  advanced.columnconfigure(0, weight=1)
  advanced.columnconfigure(1, weight=1)
  advanced.columnconfigure(2, weight=1)
  advanced.grid(column=2, row=2, sticky='EW')
  tk.Label(advanced, text="Animation").grid(column=0, row=0, columnspan=3, sticky='EW', pady=(0,5))
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=0, columnspan=3, sticky='NEW')
  ttk.Separator(advanced, orient=tk.HORIZONTAL).grid(column=0, row=0, columnspan=3, sticky='NEW', pady=(25,5))
  #duration
  tk.Label(advanced, text="Total Duration:").grid(column=0, row=1, sticky='W', padx=(5,0))
  dur = tk.StringVar()
  Number(advanced, textvariable=dur, width=5).grid(column=2, row=1, sticky='EW', padx=(0,30))
  tk.Label(advanced, text="ticks").grid(column=2, row=1, sticky='E', padx=(0,15))
  #easing
  tk.Label(advanced, text="Position Easing:").grid(column=0, row=2, sticky='W', padx=(5,0), pady=(2,0))
  ea = tk.StringVar()
  earr = ["None","Linear","Cubic","Bezier"]
  ttk.Combobox(advanced, values=earr, textvariable=ea, state='readonly', width=8).grid(column=2, row=2, pady=(2,0), sticky='W')
  #interpolation
  tk.Label(advanced, text="Texture Interpolation:").grid(column=0, row=3, sticky='W', padx=(5,5), pady=(2,0))
  it = tk.StringVar()
  iarr = ["None","Linear"]
  ttk.Combobox(advanced, values=iarr, textvariable=it, state='readonly', width=8).grid(column=2, row=3, padx=(0,5), pady=(2,0), sticky='W')
  #autoplay
  ap = tk.BooleanVar()
  tk.Checkbutton(advanced, text="Auto Play", variable=ap).grid(column=0, row=4, columnspan=3, sticky='N')
  #color behavior
  cblabel = tk.Label(advanced, text="Color Behavior:").grid(column=0, row=5, columnspan=3)
  cbarr = ['yaw', 'pitch', 'roll', 'time', 'scale', 'overlay']
  cb = [tk.StringVar() for i in range(3)]
  ttk.Combobox(advanced, values=cbarr, textvariable=cb[0], width=7, state='readonly').grid(column=0, row=6, columnspan=3, padx=(0,125))
  ttk.Combobox(advanced, values=cbarr, textvariable=cb[1], width=7, state='readonly').grid(column=0, row=6, columnspan=3, padx=(0,0))
  ttk.Combobox(advanced, values=cbarr, textvariable=cb[2], width=7, state='readonly').grid(column=0, row=6, columnspan=3, padx=(125,0))

  #output
  outfooter = tk.Frame(window)
  outfooter.columnconfigure(0, weight=1)
  outfooter.columnconfigure(1, weight=1)
  outfooter.columnconfigure(2, weight=1)
  outfooter.grid(column=2, row=3, sticky='SEW', pady=10)
  tk.Label(outfooter, text="Output").grid(column=0, row=0, columnspan=3, sticky='EW', pady=(0,10))
  ttk.Separator(outfooter, orient=tk.HORIZONTAL).grid(column=0, row=0, columnspan=3, sticky='NEW')
  ttk.Separator(outfooter, orient=tk.HORIZONTAL).grid(column=0, row=0, columnspan=3, sticky='SEW', pady=(25,10))
  outjson = tk.StringVar()
  outpng = tk.StringVar()
  tk.Entry(outfooter, textvariable=outjson, width=10).grid(column=0, row=2, columnspan=3, padx=10, sticky='NEW')
  tk.Label(outfooter, text=".json").grid(column=2, row=2, padx=10, sticky='NE')
  tk.Entry(outfooter, textvariable=outpng, width=10).grid(column=0, row=3, columnspan=3, padx=10, sticky='NEW')
  tk.Label(outfooter, text=".png").grid(column=2, row=3, padx=10, sticky='NE')

  def setval():
    settext(objlist, "\n".join(objs))
    settext(texlist, "\n".join(texs))
    fu.set(flipuv)
    for i in range(3):
      of[i].set(str(offset[i]))
    sc.set(str(scale))
    ns.set(noshadow)
    for i in range(3):
      cb[i].set(colorbehavior[i])
    ea.set(earr[easing])
    it.set(earr[interpolation])
    ar.set(rarr[autorotate])
    ap.set(autoplay)
    outjson.set(output[0].replace(".json", ""))
    outpng.set(output[1].replace(".png", ""))
  setval()

  def gethistory():
    global history
    global hid
    if history:
      hlable.config(text=str(hid+1)+"/"+str(len(history)))
      getcontext(history[hid])
  def next():
    global hid
    global history
    if hid < len(history)-1:
      hid += 1
      gethistory()
  def prev():
    global hid
    if hid > 0:
      hid -= 1
      gethistory()
  def delhistory():
    global history
    global hid
    history.pop(hid)
    if hid >= len(history):
      hid-=1
    gethistory()
  def copyhistory():
    global history
    window.clipboard_clear()
    window.clipboard_append('\n'.join(history))
  def savehistory():
    global history
    hf = open("history.txt",'w')
    hf.write('\n'.join(history))
    hf.close()
    print("Saved "+str(len(history))+" items to history.txt")
  def loadhistory():
    global history
    global hid
    f = tkfd.askopenfilename(initialdir=path,title="Select History File")
    hf = open(f,'r')
    history = hf.read().split('\n')
    hf.close()
    hid = len(history)-1
    print("Loaded "+str(hid+1)+" items")
    gethistory()
  def pastehistory():
    global history
    global hid
    history = window.clipboard_get().split('\n')
    hid = len(history)-1
    print("Pasted "+str(hid+1)+" items")
    gethistory()

  def start():
    global history
    global hid
    if len(objs) == 0 or len(texs) == 0:
      print("No files selected")
      return
    if dur.get().isdigit():
      duration = max(int(dur.get()), 1)
    else:
      duration = 1
    offset = (float(of[0].get()), float(of[1].get()), float(of[2].get()))
    scale = float(sc.get())
    easing = earr.index(ea.get())
    flipuv = fu.get()
    noshadow = ns.get()
    autorotate = rarr.index(ar.get())
    autoplay = ap.get()
    colorbehavior = [cb[0].get(), cb[1].get(), cb[2].get()]
    output = [outjson.get(), outpng.get()]
    objmc(objs, texs, output, scale, offset, duration, easing, interpolation, colorbehavior, autorotate, autoplay, flipuv, noshadow, nopow)
    context = strcontext(objs, texs, output, scale, offset, duration, easing, interpolation, colorbehavior, autorotate, autoplay, flipuv, noshadow, nopow)
    try:
      i = history.index(context)
      history.pop(i)
      history.append(context)
    except:
      history.append(context)
    hid = len(history)
    hlable.config(text=str(hid)+"/"+str(hid))
    hid -= 1
  def runhistory():
    print("Running:")
    global runtex
    for i in range(0,len(history)):
      runtex = str(i+1)+"/"+str(len(history))
      getcontext(history[i])
      objmc(objs, texs, output, scale, offset, duration, easing, interpolation, colorbehavior, autorotate, autoplay, flipuv, noshadow, nopow)
    runtex = ""

  #start
  tk.Button(window, text="Start", command=start).grid(column=2, row=4)
  #history
  hlable = tk.Label(window, text="0/0")
  hlable.grid(column=0, row=4, sticky='W', padx=5, pady=5)
  tk.Button(window, text="←", command=prev).grid(column=0, columnspan=3, row=4, sticky='W', padx=(60,0), pady=5)
  tk.Button(window, text="→", command=next).grid(column=0, columnspan=3, row=4, sticky='W', padx=(80,0), pady=5)
  tk.Button(window, text="Save History", command=savehistory).grid(column=0, columnspan=3, row=4, padx=(0,200), pady=5)
  tk.Button(window, text="Load History", command=loadhistory).grid(column=0, columnspan=3, row=4, padx=(0,47), pady=5)
  tk.Button(window, text="Run History", command=runhistory).grid(column=0, columnspan=3, row=4, padx=(102,0), pady=5)
  ttk.Separator(window, orient=tk.HORIZONTAL).grid(column=0, row=4, columnspan=3, sticky='NEW')

  #hotkeys
  window.bind('<Return>', lambda e: start())
  window.bind('<Escape>', lambda e: quit())
  window.bind('<Control-c>', lambda e: copyhistory())
  window.bind('<Control-s>', lambda e: savehistory())
  window.bind('<Control-d>', lambda e: loadhistory())
  window.bind('<Control-v>', lambda e: pastehistory())
  window.bind('<Control-r>', lambda e: runhistory())
  window.bind('<Control-x>', lambda e: delhistory())
  window.mainloop()

elif join:
  js = {
    "textures": {},
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
  tid = 0
  out = open(output[0], "w")
  for file in join:
    model = json.load(open(file))
    temp = {}
    for key,value in model["textures"].items():
      js["textures"][str(tid)] = value
      temp[key] = tid
      tid += 1
    for element in model["elements"]:
      for key,value in element["faces"].items():
        value["texture"] = "#" + str(temp[value["texture"][1:]])
      js["elements"].append(element)
  out.write(json.dumps(js,separators=(',',':')))

else:
  objmc(objs, texs, output, scale, offset, duration, easing, interpolation, colorbehavior, autorotate, autoplay, flipuv, noshadow, nopow)
#--------------------------------
quit()

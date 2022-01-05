import math
import json
from PIL import Image, ImageOps

tex = Image.open("cat.jpg")
obj = open("cat.obj", "r")
model = open("out.json", "w")

x,y = tex.size
print(x, y)

positions = []
uvs = []
normals = []
faces = []
#read obj
for line in obj:
  if line.startswith("v "):
    positions.append([float(i) for i in line.strip().split(" ")[1:]])
  if line.startswith("vt "):
    uvs.append([float(i) for i in line.strip().split(" ")[1:]])
  if line.startswith("vn "):
    normals.append([float(i) for i in line.strip().split(" ")[1:]])
  if line.startswith("f "):
    faces.append([[int(i)-1 for i in vert.split("/")] for vert in line.strip().split(" ")[1:]])
#calculate heights
nfaces = len(faces)
nvertices = nfaces*4
uvheight = math.ceil(nfaces/x)
#meta = rgba: scale, hasnormal, easing, unused
#position = rgb, rgb, rgb
#normal = aaa
#uv = rg,ba
dataheight = math.ceil(((5*nvertices))/x)+1
ty = 1 + uvheight + y + dataheight

print("positions:", len(positions)-1, "uvs:", len(uvs)-1, "normals:", len(normals)-1, "faces:", nfaces, "vertices:", nvertices)
print("header:", 1, "uvheight:", uvheight, "texture:", y, "dataheight:", dataheight, "totalheight:", ty, "powheight:", ty)
#create out image with correct dimensions
out = Image.new("RGBA", (x, int(ty)), (0,0,0,0))

#calculate unique pixel uv per face
def getuvpos(elementindex, faceoffset):
  faceid = ((elementindex*6)+faceoffset)
  posx = faceid%x
  posy = math.floor(faceid/x)+1
  out.putpixel((posx, posy), (int(posx/256)%256, posx%256, int(posy/256)%256, posy%256))
  return [posx*16/x, posy*16/ty, (posx+1)*16/x, (posy+1)*16/ty]

#create elements for model
js = {
  "textures": {
    "1": "out"
  },
  "elements": []
}
def newelement(index):
  cube = {
    "from": [0,0,0],
    "to": [0,0,0],
    "faces": {
      "north" : {"uv": getuvpos(index, 0), "texture": "#1"},
      "east"  : {"uv": getuvpos(index, 1), "texture": "#1"},
      "south" : {"uv": getuvpos(index, 2), "texture": "#1"},
      "west"  : {"uv": getuvpos(index, 3), "texture": "#1"},
      "up"    : {"uv": getuvpos(index, 4), "texture": "#1"},
      "down"  : {"uv": getuvpos(index, 5), "texture": "#1"}
    }
  }
  js["elements"].append(cube)

#header:
#marker pix
out.putpixel((0,0), (12,34,56,0))
#texture size
out.putpixel((1,0), (int(x/256), x%256, int(y/256), y%256))
#nvertices
out.putpixel((2,0), (int(nvertices/256/256/256)%256, int(nvertices/256/256)%256, int(nvertices/256)%256, nvertices%256))
#nframes
out.putpixel((3,0), (0,0,0,math.ceil(y/x)))

#generate elements and uv header
for i in range(0, math.ceil(nfaces/6)):
  newelement(i)
model.write(json.dumps(js))
print("elements:", math.ceil(nfaces/6))

#actual texture
out.paste(ImageOps.flip(tex), (0,1+uvheight))

#grab data from the list and convert to rgb
def getposition(index):
  x = 131071+((positions[index][0])*65536)
  y = 131071+((positions[index][1])*65536)
  z = 131071+((positions[index][2])*65536)
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
def getnormal(index):
  r = int((normals[index][0]+1)*255.9/2)
  g = int((normals[index][1]+1)*255.9/2)
  b = int((normals[index][2]+1)*255.9/2)
  return [r,g,b]
def getuv(index):
  x = (uvs[index][0])*65535
  y = (uvs[index][1])*65535
  r = int(x/256)%256
  g = int(x%256)
  b = int(y/256)%256
  a = int(y%256)
  return (r,g,b,a)
def getp(index, offset):
  i = (index*5)+offset
  xx = i%x
  yy = int(1+uvheight+y+((i/x)))
  return (xx,yy)
#inverse pixel grid for uv :wtfix:
def getip(index, offset):
  i = (index*5)+offset
  xx = i%x
  yy = int(1+uvheight+y+((i/x)))
  return (xx,yy)
#meta = rgba: scale, hasnormal, easing, unused
#position = rgb, rgb, rgb
#normal = aaa
#uv = rg,ba
#face:[pos,uv,norm]
def encodevert(index, face):
  #init meta
  scale = 100
  hasnormal = 1
  easing = 0
  #get position and append normal
  rgb = getposition(face[0])
  if len(face) == 2:
    norm = [0,0,0]
    hasnormal = 0
  else:
    norm = getnormal(face[2])
  #meta
  out.putpixel(getp(index, 0), (scale, hasnormal, easing, 255))
  #position and normal
  for i in range(0,3):
    rgb[i].append(norm[i])
    out.putpixel(getp(index, i+1), tuple(rgb[i]))
  #uv
  out.putpixel(getip(index, 4), getuv(face[1]))

def encodeface(index, face):
  for i in range(0,3):
    encodevert((index*4)+i, face[i])
  if len(face) == 4:
    encodevert((index*4)+3, face[3])
  else:
    encodevert((index*4)+3, face[1])

#encode all the data
for i in range(0, nfaces):
  encodeface(i, faces[i])

out.save("out.png")

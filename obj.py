from dataclasses import dataclass

@dataclass
class Position:
    x: float
    y: float
    z: float

@dataclass
class UV:
    x: float
    y: float

@dataclass
class Vertex:
    pos: Position
    uv: UV

@dataclass
class VertexID:
    pos: int
    uv: int

class Obj:
    """
    parsed obj file

    positions: list[Position]
    uvs: list[UV]
    faces: list[list[VertexID]]
    """
    def __init__(self, filename):
        file = open(filename, "r", encoding="utf-8")
        self.parse(file)
        file.close()
    def parse(self, file):
        self.positions: list[Position] = []
        self.uvs: list[UV] = []
        self.faces: list[list[VertexID]] = []
        for line in file:
            #vertices
            if line.startswith("v "):
                cleaned = line[2:].split()
                self.positions.append(Position(*(float(num) for num in cleaned)))
            #uvs
            elif line.startswith("vt "):
                cleaned = line[3:].split()
                self.uvs.append(UV(*(float(num) for num in cleaned)))
            #faces
            elif line.startswith("f "):
                face = line[2:].split()
                verts = []
                for vert in face:
                    ids = vert.split("/")
                    pos = int(ids[0]) - 1
                    uv = int(ids[1]) - 1
                    verts.append(VertexID(pos, uv))
                self.faces.append(verts)
        return self

class Objs():
    """
    collection of indexed obj data

    positions: list[Position]
    uvs: list[UV]
    faces: list[list[VertexID]]

    add(Obj) -> Objs
    """
    def __init__(self):
        self.positions: list[Position] = []
        self.uvs: list[UV] = []
        self.vertices: list[VertexID] = []
        self.mem = {"pos":{}, "uv":{}, "vert":{}}
    def add(self, obj: Obj):
        for face in obj.faces:
            for vertid in face:
                self.indexvert(obj, vertid)
            if len(face) == 3:
                self.indexvert(obj, face[1])
        return self
    def indexvert(self, obj: Obj, vertid: VertexID):
        pos = obj.positions[vertid.pos]
        uv = obj.uvs[vertid.uv]
        posh = str(pos)
        uvh = str(uv)
        v = VertexID(0, 0)
        try:
            v.pos = self.mem['pos'][posh]
        except:
            v.pos = len(self.positions)
            self.mem["pos"][posh] = len(self.positions)
            self.positions.append(pos)
        try:
            v.uv = self.mem['uv'][uvh]
        except:
            v.uv = len(self.uvs)
            self.mem["uv"][uvh] = len(self.uvs)
            self.uvs.append(uv)

        self.vertices.append(v)
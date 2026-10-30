# 피치덱 3D 렌더 (Blender 5.x, Cycles + Metal GPU)
# 실행: /Applications/Blender.app/Contents/MacOS/Blender -b -P render3d.py -- <scene> <out.png> [samples]
#   scene: drone | sim | cctv | droptest | solution | cover | zone | fall
# 모든 모델은 기본 도형으로 직접 만든다(외부 에셋 없음). 조명은 Blender 내장 HDRI를 쓴다.
import bpy, math, sys, json, os, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
SCENE, OUT = argv[0], os.path.abspath(argv[1])
SAMPLES = int(argv[2]) if len(argv) > 2 else 192
HDRI_DIR = os.path.join(os.path.dirname(bpy.app.binary_path), "..", "Resources",
                        f"{bpy.app.version[0]}.{bpy.app.version[1]}", "datafiles", "studiolights", "world")
random.seed(7)


# ---------------------------------------------------------------- 기본 도구
def lin(hexstr):
    c = [int(hexstr.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def mat(name, color, rough=0.5, metal=0.0, emit=0.0, alpha=1.0, transmission=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*lin(color), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Alpha"].default_value = alpha
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(color), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def noisy(name, color, rough=0.8, scale=6.0, contrast=0.12, bump=0.15):
    """콘크리트·바닥처럼 얼룩과 요철이 있는 재질."""
    m = mat(name, color, rough)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = 8
    r = nt.nodes.new("ShaderNodeValToRGB")
    base = lin(color)
    r.color_ramp.elements[0].color = (*[c * (1 - contrast) for c in base], 1)
    r.color_ramp.elements[1].color = (*[min(1, c * (1 + contrast)) for c in base], 1)
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"]); nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = bump
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = scale * 12
    nt.links.new(n2.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    return m


def smooth(o):
    try:
        o.data.shade_smooth()
    except Exception:
        for p in o.data.polygons:
            p.use_smooth = True


def bevel(o, w=0.004, seg=3):
    md = o.modifiers.new("bevel", "BEVEL"); md.width = w; md.segments = seg
    md.limit_method = "ANGLE"; md.harden_normals = True
    smooth(o)


def box(loc, size, m, bev=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if bev:
        bevel(o, bev)
    return o


def cyl(loc, r, depth, m, rot=(0, 0, 0), verts=48, bev=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.data.materials.append(m)
    if bev:
        bevel(o, bev)
    else:
        smooth(o)
    return o


def rod(a, b, r, m, verts=24):
    """두 점 a→b를 잇는 원기둥."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl((a + b) / 2, r, d.length, m, verts=verts)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o


def sphere(loc, r, m, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    o = bpy.context.active_object
    o.data.materials.append(m)
    smooth(o)
    return o


def world_hdri(name, strength=1.0, rot_deg=0.0, color=None):
    w = bpy.data.worlds.new("W"); bpy.context.scene.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    if color:
        bg.inputs["Color"].default_value = (*lin(color), 1)
        bg.inputs["Strength"].default_value = strength
        return
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(HDRI_DIR, name + ".exr"))
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(rot_deg))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength


def world_sky(strength=0.35, elev=30, rot=0.0):
    """물리 기반 하늘(배경·환경광). 직사광은 따로 sun()으로 넣는다."""
    w = bpy.data.worlds.new("W"); bpy.context.scene.world = w
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False
    sky.sun_elevation = math.radians(elev)
    sky.sun_rotation = math.radians(rot)
    bg = nt.nodes.get("Background")
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength


def area_light(loc, target, power, size, color="#FFFFFF"):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.active_object
    l.data.energy = power; l.data.size = size; l.data.color = lin(color)
    aim(l, target)
    return l


def sun(rot, strength, angle=2.0):
    bpy.ops.object.light_add(type="SUN", rotation=[math.radians(a) for a in rot])
    l = bpy.context.active_object
    l.data.energy = strength; l.data.angle = math.radians(angle)
    return l


def aim(o, target):
    d = Vector(target) - o.location
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("-Z", "Y")


def camera(loc, target, lens=50, shift_y=0.0):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.active_object
    c.data.lens = lens; c.data.shift_y = shift_y
    aim(c, target)
    bpy.context.scene.camera = c
    return c


def setup_render(w, h, transparent=False):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:
        print("GPU unavailable:", e)
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            pass


def shadow_catcher(size=20):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    p = bpy.context.active_object
    p.is_shadow_catcher = True
    return p


def render():
    bpy.context.scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
    print("rendered", OUT)


ORANGE = "#FF5A1F"


# ---------------------------------------------------------------- 모델: 산업용 점검 드론 (Matrice급 실루엣)
def build_drone(z0=0.0):
    body = noisy("body", "#26292D", 0.55, 40, 0.04, 0.02)
    shell = mat("shell", "#3D4249", 0.6)
    carbon = mat("carbon", "#1A1C1F", 0.5)
    motor = mat("motor", "#33373C", 0.38, metal=0.75)
    alu = mat("alu", "#8E959C", 0.35, metal=1.0)
    prop = mat("prop", "#141517", 0.55)
    glass = mat("glass", "#0B0C0E", 0.04, coat=1.0)
    accent = mat("accent", ORANGE, 0.35)
    led = mat("led", ORANGE, 0.3, emit=12)
    H = z0 + 0.30
    box((0, 0, H), (0.17, 0.25, 0.075), body, 0.018)
    box((0, -0.01, H + 0.055), (0.12, 0.16, 0.035), shell, 0.008)
    box((0, -0.01, H + 0.075), (0.08, 0.12, 0.006), alu, 0.002)
    box((0, 0.126, H + 0.005), (0.10, 0.004, 0.03), glass, 0.001)
    for sx in (-1, 1):
        cyl((0.045 * sx, -0.07, H + 0.085), 0.004, 0.035, carbon)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        start = Vector((0, 0, H + 0.005)) + d * 0.08
        end = Vector((0, 0, H + 0.02)) + d * 0.38
        rod(start, end, 0.014, carbon)
        cyl((end.x, end.y, end.z + 0.012), 0.03, 0.045, motor, bev=0.004)
        cyl((end.x, end.y, end.z + 0.04), 0.018, 0.012, alu)
        spin = a + math.pi / 2 + random.uniform(-0.25, 0.25)
        for k in (0, 1):
            ba = spin + k * math.pi
            c = Vector((end.x, end.y, end.z + 0.048)) + Vector((math.cos(ba), math.sin(ba), 0)) * 0.11
            box(c, (0.21, 0.026, 0.004), prop, 0.0012, rot=(math.radians(6 if k else -6), 0, ba))
        sphere((end.x, end.y, end.z - 0.018), 0.008, led)
    # 착륙 다리 (좌우 역V + 스키드)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod((0.05 * sx, 0.07 * sy, H - 0.03), (0.17 * sx, 0.09 * sy, z0 + 0.018), 0.009, carbon)
        cyl((0.17 * sx, 0, z0 + 0.018), 0.011, 0.36, carbon, rot=(math.radians(90), 0, 0))
        for sy in (-1, 1):
            sphere((0.17 * sx, 0.18 * sy, z0 + 0.018), 0.012, carbon)
    # 짐벌 카메라
    cyl((0, 0.10, H - 0.05), 0.012, 0.03, alu)
    box((0, 0.105, H - 0.10), (0.075, 0.07, 0.065), body, 0.014)
    cyl((0, 0.142, H - 0.10), 0.024, 0.01, accent, rot=(math.radians(90), 0, 0))
    cyl((0, 0.146, H - 0.10), 0.019, 0.01, glass, rot=(math.radians(90), 0, 0))
    sphere((0, 0.15, H - 0.10), 0.012, glass)


# ---------------------------------------------------------------- 모델: 골조 공사 중인 건물
def build_building(o=(0, 0, 0), floors=8, w=9.0, d=6.0, fh=3.0, clay=None, glass_floors=3, top_open=2):
    ox, oy, oz = o
    concrete = clay or noisy("concrete", "#A9A9A4", 0.85, 3.0, 0.10, 0.2)
    glass = mat("bglass", "#2E3A44", 0.06, metal=0.2, coat=1.0)
    wood = noisy("form", "#B58B5A", 0.7, 8, 0.15) if not clay else clay
    steel = mat("rebar", "#6D5E52", 0.6, metal=0.7) if not clay else clay
    rail = mat("rail", "#C9CDD3", 0.4, metal=0.8) if not clay else clay
    xs = [ox - w / 2 + 0.25 + i * (w - 0.5) / 3 for i in range(4)]
    ys = [oy - d / 2 + 0.25, oy + d / 2 - 0.25]
    for f in range(floors + 1):
        box((ox, oy, oz + f * fh), (w, d, 0.28), concrete)
    for f in range(floors):
        for x in xs:
            for y in ys:
                box((x, y, oz + f * fh + fh / 2), (0.45, 0.45, fh), concrete)
        if f < glass_floors and not clay:
            for i in range(3):
                x = (xs[i] + xs[i + 1]) / 2
                box((x, ys[0] - 0.02, oz + f * fh + fh / 2 + 0.1), (xs[1] - xs[0] - 0.5, 0.04, fh - 0.6), glass)
    top = oz + floors * fh
    for x in xs:   # 최상층 기둥 철근
        for y in ys:
            box((x, y, top + 0.7), (0.45, 0.45, 1.4), concrete)
            for dx in (-0.12, 0.12):
                for dy in (-0.12, 0.12):
                    rod((x + dx, y + dy, top + 1.4), (x + dx, y + dy, top + 2.3), 0.016, steel, verts=8)
    box((ox - w / 4, oy, top + 0.9), (w / 2.4, d * 0.7, 1.6), wood)   # 거푸집
    for x in [ox - w / 2 + i * w / 8 for i in range(9)]:            # 안전난간
        rod((x, oy - d / 2 - 0.1, top + 0.14), (x, oy - d / 2 - 0.1, top + 1.2), 0.025, rail, verts=8)
    rod((ox - w / 2, oy - d / 2 - 0.1, top + 1.15), (ox + w / 2, oy - d / 2 - 0.1, top + 1.15), 0.03, rail, verts=8)
    rod((ox - w / 2, oy - d / 2 - 0.1, top + 0.65), (ox + w / 2, oy - d / 2 - 0.1, top + 0.65), 0.025, rail, verts=8)
    return top


def trajectory(p0, v0, m_dot, m_obj, steps=7, total=None, z_end=0.15, r=0.09, obj_size=(0.5, 0.18, 0.18)):
    """같은 시간 간격의 낙하 위치에 점을 찍고, 마지막 위치 근처에 물체를 둔다."""
    g = 9.81
    T = total or math.sqrt(2 * (p0[2] - z_end) / g)
    pts = []
    for i in range(steps + 1):
        t = T * i / steps
        pts.append((p0[0] + v0[0] * t, p0[1] + v0[1] * t, p0[2] - 0.5 * g * t * t))
    for p in pts[1:-1]:
        sphere(p, r, m_dot, seg=24)
    mid = pts[int(steps * 0.55)]
    box(mid, obj_size, m_obj, 0.02, rot=(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 3)))
    return pts


# ---------------------------------------------------------------- 모델: 타워크레인·작업자·현장 장비
def build_crane(base=(22, 4, 0), H=42.0, jib=20.0, counter=11.0, white=None):
    """플랫탑 타워크레인. 마스트는 1.6 m 정사각 래티스. 지브는 +x 방향. 반환: (지브 하현 높이, 트롤리 x 범위)"""
    bx, by, bz = base
    paint = white or mat("crane", "#E2E0D8", 0.55, metal=0.2)
    dark = mat("crane_dark", "#3A3F46", 0.5, metal=0.4)
    a = 0.8
    corners = [(bx - a, by - a), (bx + a, by - a), (bx + a, by + a), (bx - a, by + a)]
    for (x, y) in corners:
        rod((x, y, bz), (x, y, bz + H), 0.07, paint, 10)
    seg = 2.4
    n = int(H / seg)
    for i in range(n):
        z0, z1 = bz + i * seg, bz + (i + 1) * seg
        for k in range(4):
            (x0, y0), (x1, y1) = corners[k], corners[(k + 1) % 4]
            rod((x0, y0, z0), (x1, y1, z0), 0.035, paint, 6)
            if i % 2:
                rod((x0, y0, z0), (x1, y1, z1), 0.03, paint, 6)
            else:
                rod((x1, y1, z0), (x0, y0, z1), 0.03, paint, 6)
    top = bz + H
    box((bx, by, top + 0.6), (2.2, 2.2, 1.2), dark, 0.05)                 # 선회장치
    box((bx + 1.6, by - 1.5, top - 0.4), (1.6, 1.4, 2.0), paint, 0.08)      # 운전실
    box((bx + 2.2, by - 1.5, top - 0.3), (0.05, 1.2, 1.2), mat("cabglass", "#1E2833", 0.05, coat=1.0))
    jz = top + 1.3
    def truss(x0, x1, height, w):
        L = x1 - x0
        for sy in (-w / 2, w / 2):
            rod((x0, by + sy, jz), (x1, by + sy, jz), 0.06, paint, 8)
        rod((x0, by, jz + height), (x1, by, jz + height), 0.06, paint, 8)
        steps = int(abs(L) / 2.0)
        for i in range(steps + 1):
            x = x0 + L * i / steps
            for sy in (-w / 2, w / 2):
                rod((x, by + sy, jz), (x, by, jz + height), 0.03, paint, 6)
            rod((x, by - w / 2, jz), (x, by + w / 2, jz), 0.03, paint, 6)
    truss(bx, bx + jib, 1.4, 1.2)
    truss(bx, bx - counter, 1.0, 1.4)
    for i in range(3):                                                        # 균형추
        box((bx - counter + 1.0 + i * 1.3, by, jz - 0.9), (1.2, 2.0, 1.6), noisy("cw", "#9A9A96", 0.85, 4, 0.1), 0.03)
    return jz, dark


def hook_load(x, y, jz, load_z, dark):
    steel = mat("steelbeam", "#5E5A55", 0.5, metal=0.6)
    box((x, y, jz - 0.25), (1.0, 1.4, 0.4), dark, 0.03)                       # 트롤리
    for dy in (-0.15, 0.15):
        rod((x, y + dy, jz - 0.45), (x, y + dy, load_z + 2.2), 0.025, dark, 8)
    box((x, y, load_z + 2.0), (0.5, 0.35, 0.6), mat("hook", "#E6B800", 0.45), 0.04)
    for dx in (-1.6, 1.6):
        for dy in (-0.45, 0.45):
            rod((x, y, load_z + 1.7), (x + dx, y + dy, load_z + 0.35), 0.018, dark, 6)
    for i, (dz, dy) in enumerate([(0, -0.3), (0, 0.3), (0.3, 0)]):           # H형강 묶음
        box((x, y + dy, load_z + 0.15 + dz), (4.0, 0.28, 0.28), steel, 0.01)


def worker3d(loc, face=0.0, vest=ORANGE):
    x, y, z = loc
    r = math.radians(face)
    pants = mat("pants", "#2B2F35", 0.8)
    vestm = mat("vest", vest, 0.6, emit=0.15)
    skin = mat("skin", "#C99A78", 0.6)
    helmet = mat("helmet", "#F4F4F2", 0.3, coat=0.6)
    stripe = mat("stripe", "#D8DCE0", 0.2, metal=0.6)
    rot = lambda dx, dy: (x + dx * math.cos(r) - dy * math.sin(r), y + dx * math.sin(r) + dy * math.cos(r))
    for sx in (-0.1, 0.1):
        px, py = rot(sx, 0)
        cyl((px, py, z + 0.45), 0.075, 0.9, pants, verts=16)
        box((px + 0.05 * math.cos(r + math.pi / 2), py + 0.05 * math.sin(r + math.pi / 2), z + 0.05), (0.14, 0.26, 0.1), pants, 0.02, rot=(0, 0, r))
    tx, ty = rot(0, 0)
    box((tx, ty, z + 1.22), (0.42, 0.26, 0.62), vestm, 0.06, rot=(0, 0, r))
    box((tx, ty, z + 1.12), (0.43, 0.27, 0.05), stripe, 0.0, rot=(0, 0, r))
    for sx in (-0.27, 0.27):
        ax, ay = rot(sx, 0)
        cyl((ax, ay, z + 1.2), 0.06, 0.62, pants, verts=16)
    sphere((tx, ty, z + 1.66), 0.12, skin, 24)
    h = sphere((tx, ty, z + 1.73), 0.145, helmet, 24); h.scale.z = 0.75
    cyl((tx, ty, z + 1.69), 0.17, 0.02, helmet, verts=24)


def beacon3d(loc, h=3.0):
    x, y, z = loc
    pole = mat("pole", "#5C626B", 0.4, metal=0.6)
    rod((x, y, z), (x, y, z + h), 0.05, pole, 12)
    cyl((x, y, z + h + 0.05), 0.14, 0.1, pole, verts=24)
    o = sphere((x, y, z + h + 0.22), 0.16, mat("beacon", ORANGE, 0.2, emit=25), 24); o.scale.z = 1.3
    bpy.ops.object.light_add(type="POINT", location=(x, y, z + h + 0.25))
    l = bpy.context.active_object; l.data.energy = 300; l.data.color = lin(ORANGE); l.data.shadow_soft_size = 0.2


def edgebox3d(loc):
    x, y, z = loc
    body = mat("edge", "#26292D", 0.5)
    fin = mat("fin", "#4A4F57", 0.4, metal=0.7)
    box((x, y, z), (0.7, 0.3, 0.45), body, 0.03)
    for i in range(7):
        box((x - 0.27 + i * 0.09, y, z + 0.25), (0.04, 0.28, 0.07), fin, 0.005)
    sphere((x + 0.26, y - 0.155, z - 0.15), 0.018, mat("edgeled", ORANGE, 0.3, emit=20), 12)
    rod((x + 0.25, y, z + 0.22), (x + 0.25, y, z + 0.7), 0.012, fin, 8)


def cctv3d(loc, yaw_deg, scale=1.0):
    x, y, z = loc
    k = scale
    r = math.radians(yaw_deg)
    body = mat("cctv", "#E9EBED", 0.35, coat=0.5)
    d = Vector((math.cos(r), math.sin(r), -0.25)).normalized()
    c = Vector(loc)
    o = rod(c, c + d * 0.55 * k, 0.11 * k, body, 24)
    rod(c + d * 0.55 * k, c + d * 0.6 * k, 0.085 * k, mat("cctvlens", "#0E1012", 0.08, coat=1.0), 24)
    rod(c - d * 0.05 * k, c - d * 0.05 * k + Vector((0, 0, -0.25 * k)), 0.03 * k, body, 8)


def zone3d(x, y, load_z, half, margin, strength=1.0, ghost=False):
    """인양물 투영 + 안전반경: 반투명 사다리꼴 기둥 + 지면 표시."""
    a = 0.10 * strength
    vol = mat(f"zonevol{ghost}", ORANGE, 0.5, emit=0.6 * strength, alpha=a)
    floor = mat(f"zonefloor{ghost}", ORANGE, 0.5, emit=1.5 * strength, alpha=0.45 * strength)
    edge = mat(f"zoneedge{ghost}", ORANGE, 0.4, emit=6 * strength, alpha=min(1, strength))
    bot = half + margin
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=bot * math.sqrt(2), radius2=half * math.sqrt(2), depth=load_z,
                                    location=(x, y, load_z / 2), rotation=(0, 0, math.radians(45)))
    o = bpy.context.active_object; o.data.materials.append(vol)
    for p in o.data.polygons:
        if abs(p.normal.z) > 0.9:
            p.select = True
    box((x, y, 0.02), (2 * bot, 2 * bot, 0.02), floor)
    for (dx, dy, sx, sy) in ((0, -bot, 2 * bot, 0.12), (0, bot, 2 * bot, 0.12), (-bot, 0, 0.12, 2 * bot), (bot, 0, 0.12, 2 * bot)):
        box((x + dx, y + dy, 0.035), (sx, sy, 0.04), edge)


def alert_ring(x, y, r=0.9):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.045, location=(x, y, 0.05))
    t = bpy.context.active_object; t.data.materials.append(mat("ring2", ORANGE, 0.3, emit=12))


def site_office(loc):
    x, y, z = loc
    wallm = mat("office", "#D9DCDF", 0.6)
    box((x, y, z + 1.3), (6.0, 2.5, 2.6), wallm, 0.04)
    for i in range(3):
        box((x - 1.8 + i * 1.8, y - 1.26, z + 1.6), (1.1, 0.04, 0.8), mat("officeglass", "#24313C", 0.08, coat=1.0))
    box((x, y, z + 2.65), (6.2, 2.7, 0.1), mat("roof", "#8A9099", 0.5))


def falling_dots(p0, v0, z_end=0.3, steps=7, r=0.22, obj=True):
    g = 9.81
    T = math.sqrt(2 * (p0[2] - z_end) / g)
    dot = mat("fdot", ORANGE, 0.35, emit=4)
    pts = []
    for i in range(steps + 1):
        t = T * i / steps
        pts.append((p0[0] + v0[0] * t, p0[1] + v0[1] * t, p0[2] - 0.5 * g * t * t))
    for q in pts[1:]:
        sphere(q, r if q != pts[-1] else r * 1.5, dot, 20)
    if obj:
        m = pts[steps // 2]
        cyl((m[0] + 0.4, m[1], m[2] + 1.2), 0.07, 1.4, mat("fpipe", ORANGE, 0.4), rot=(0.4, 0.9, 0.2))
    return pts


def build_site(daylight=True):
    """솔루션·표지 공통 현장. 반환: 배지 기준점(월드 좌표)."""
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(noisy("site_ground", "#7B746A", 0.95, 0.8, 0.2, 0.4))
    top = build_building((0, 0, 0), floors=10, w=12, d=8, glass_floors=3)
    jz, dark = build_crane((22, 4, 0), H=40, jib=20, counter=11)
    hook_load(34, 4, jz, 16, dark)
    zone3d(34, 4, 16, 2.2, 1.6)
    worker3d((35.6, 2.6, 0), 200)
    alert_ring(35.6, 2.6)
    worker3d((29, -3, 0), 30)
    worker3d((9.5, -6.5, 0), 160)
    worker3d((-3, -4.6, top + 0.14), 180)
    beacon3d((30.5, -0.5, 0), 3.2)
    beacon3d((8.0, -7.5, 0), 2.8)
    site_office((15, -9, 0))
    edgebox3d((13.0, -10.4, 1.4))
    cctv3d((21.0, 3.0, 22.0), 200, scale=2.2)
    pts = falling_dots((6.3, -4.3, top + 0.5), (0.5, -0.4, 0))
    bpy.ops.object.empty_add(location=(0, 0, 0))
    D = bpy.context.active_object
    build_drone_at((-3.0, -9.0, top + 4.5), 3.0, D)
    return {"zone": (34, 4, 2.5), "fall": pts[4], "drone": (-3.0, -9.0, top + 5.4)}


def build_drone_at(loc, scale, parent):
    """드론을 원점에 만든 뒤 크기·위치를 옮긴다."""
    before = set(bpy.data.objects)
    build_drone()
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        o.parent = parent
    parent.scale = (scale, scale, scale)
    parent.location = (loc[0], loc[1], loc[2] - 0.3 * scale)


def screen_points(cam, named):
    sc = bpy.context.scene
    out = {}
    for k, v in named.items():
        p = world_to_camera_view(sc, cam, Vector(v))
        out[k] = [p.x, 1 - p.y]
    with open(OUT.replace(".png", ".json"), "w") as fh:
        json.dump(out, fh)


# ---------------------------------------------------------------- 장면
def scene_drone():
    setup_render(1800, 1120, transparent=True)
    build_drone()
    shadow_catcher()
    world_hdri("studio", 0.45, 30)
    area_light((-1.6, 1.8, 2.2), (0, 0, 0.3), 110, 1.8)
    area_light((2.0, -1.4, 1.4), (0, 0, 0.3), 70, 2.2, "#DDE6F0")
    area_light((0.0, -2.4, 0.9), (0, 0, 0.3), 45, 2.5)
    bpy.context.scene.view_settings.exposure = -0.2
    camera((1.02, 1.68, 0.74), (0.0, 0.02, 0.24), lens=55)
    render()


def scene_sim():
    setup_render(1560, 1080)
    clay = mat("clay", "#B7BCC2", 0.75)
    world_hdri(None, 1.0, color="#262A2F")
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    g = bpy.context.active_object; g.data.materials.append(mat("ground", "#23262A", 0.9))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=40, size=80, location=(0, 0, 0.01))
    grid = bpy.context.active_object
    wf = grid.modifiers.new("wf", "WIREFRAME"); wf.thickness = 0.03
    grid.data.materials.append(mat("gridline", "#5E646C", 0.6, emit=0.4))
    top = build_building((0, 0, 0), floors=8, clay=clay)
    dot_w = mat("dotw", "#E6E9EC", 0.4, emit=2.0)
    dot_o = mat("doto", ORANGE, 0.4, emit=6.0)
    obj_w = mat("objw", "#D9DCE0", 0.5)
    obj_o = mat("objo", ORANGE, 0.45, emit=0.6)
    # 오른쪽 외벽에서 바깥으로 떨어지는 궤적 (어두운 배경에 대비되게)
    for y, vx, vy, hl in [(-2.2, 1.3, -0.6, 0), (-0.4, 2.4, -0.3, 1), (1.6, 1.8, 0.2, 0), (2.6, 3.0, 0.4, 0)]:
        trajectory((4.9, y, top + 0.4), (vx, vy, 0), dot_o if hl else dot_w, obj_o if hl else obj_w, steps=8, r=0.2, obj_size=(1.1, 0.38, 0.38))
    sun((50, 10, 35), 3.0, 4)
    area_light((-14, -16, 30), (0, 0, 10), 6000, 12, "#CFDDF0")
    camera((24.0, -40.0, 19.0), (0.5, -2.0, 11.5), lens=35)
    render()


def scene_cctv():
    setup_render(1560, 1080)
    world_sky(0.3, 28)
    sun((54, 0, -28), 4.5, 1.2).data.color = lin("#FFF1DD")
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    g = bpy.context.active_object; g.data.materials.append(noisy("asphalt", "#6A6C6E", 0.92, 2.0, 0.15, 0.3))
    build_building((0, 0, 0), floors=9, w=12, d=8, glass_floors=4)
    build_building((17, 9, 0), floors=6, w=10, d=8, glass_floors=6)
    build_building((-20, 14, 0), floors=12, w=10, d=10, glass_floors=12)
    # 낙하물: 주황색 도장 강관, 모션 블러
    pipe = cyl((-1.2, -5.2, 19.0), 0.08, 1.5, mat("pipe", ORANGE, 0.35, emit=0.4), rot=(0.5, 0.9, 0.2))
    sc = bpy.context.scene
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.6
    pipe.keyframe_insert("location", frame=1); pipe.keyframe_insert("rotation_euler", frame=1)
    pipe.location.z -= 1.2; pipe.rotation_euler.x += 0.6
    pipe.keyframe_insert("location", frame=2); pipe.keyframe_insert("rotation_euler", frame=2)
    sc.frame_set(1)
    cam = camera((-15.0, -31.0, 6.5), (1.5, 0, 15.5), lens=30)
    render()
    # 낙하물 화면 좌표(합성 박스용)를 저장
    pts = []
    for f in (1, 2):
        sc.frame_set(f)
        for c in pipe.bound_box:
            p = world_to_camera_view(sc, cam, pipe.matrix_world @ Vector(c))
            pts.append((p.x, 1 - p.y))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    with open(OUT.replace(".png", ".json"), "w") as fh:
        json.dump({"bbox": [min(xs), min(ys), max(xs), max(ys)]}, fh)


def scene_droptest():
    setup_render(1560, 1080)
    world_hdri(None, 0.6, color="#E9ECEF")
    floor = noisy("floor", "#B9BBBB", 0.6, 1.5, 0.08, 0.1)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(floor)
    wall = mat("wall", "#D7D9DB", 0.9)
    box((0, 6, 8), (80, 0.2, 16), wall)
    box((-14, 0, 8), (0.2, 40, 16), wall)
    steel = mat("steel", "#3A3F46", 0.35, metal=0.7)
    # 게이트형 낙하 시험 프레임
    for x in (-1.3, 1.3):
        box((x, 0, 2.1), (0.14, 0.14, 4.2), steel, 0.01)
        box((x, 0, 0.04), (0.5, 0.5, 0.08), steel, 0.01)
    box((0, 0, 4.25), (2.9, 0.18, 0.18), steel, 0.01)
    box((0, 0, 4.05), (0.16, 0.16, 0.22), mat("release", "#1F2226", 0.4), 0.01)
    cyl((0, 0, 3.86), 0.006, 0.2, steel)
    # 측정 막대 (0.25 m 흑백 띠)
    bw, wt = mat("band_b", "#1A1A1A", 0.5), mat("band_w", "#F2F2F2", 0.5)
    for i in range(16):
        cyl((-0.55, 0.25, 0.125 + i * 0.25), 0.025, 0.25, bw if i % 2 else wt, verts=24)
    # 더미 물체 다중 노출: 같은 시간 간격 → 아래로 갈수록 간격이 벌어진다
    g, z0 = 9.81, 3.62
    T = math.sqrt(2 * (z0 - 0.16) / g)
    for i in range(6):
        t = T * i / 5
        a = 0.32 + 0.68 * (i / 5) ** 1.4
        box((0, 0, z0 - 0.5 * g * t * t), (0.16, 0.16, 0.3), mat(f"dummy{i}", ORANGE, 0.45, alpha=a), 0.015,
            rot=(0, 0, math.radians(8 * i)))
    # 착지 목표 원
    bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.02, location=(0, 0, 0.005))
    t_ = bpy.context.active_object; t_.scale.z = 0.15; t_.data.materials.append(mat("ring", ORANGE, 0.5))
    # 고속 카메라 + 삼각대
    cam_body = mat("cam", "#202326", 0.35, coat=0.4)
    box((2.9, -1.6, 1.45), (0.22, 0.32, 0.18), cam_body, 0.02, rot=(0, 0, math.radians(-30)))
    cyl((2.78, -1.42, 1.45), 0.06, 0.18, mat("lens", "#111214", 0.15, coat=1.0), rot=(math.radians(90), 0, math.radians(-30)))
    for a in (0, 120, 240):
        r = math.radians(a)
        rod((2.9, -1.6, 1.33), (2.9 + 0.45 * math.cos(r), -1.6 + 0.45 * math.sin(r), 0.0), 0.012, steel, verts=12)
    box((3.45, -1.25, 0.28), (0.62, 0.42, 0.56), mat("case", "#2B2F35", 0.55), 0.03)  # 장비 케이스
    area_light((-3, -4, 6), (0, 0, 1.8), 1800, 4)
    area_light((5, -2, 3), (0, 0, 1.8), 600, 3, "#DDE6F0")
    camera((-2.4, -6.4, 2.0), (0.75, 0, 1.95), lens=30)
    render()


def scene_solution():
    setup_render(1920, 1080)
    world_sky(0.32, 32)
    sun((50, 0, -35), 4.0, 1.2).data.color = lin("#FFF1DD")
    pts = build_site()
    bpy.context.scene.view_settings.exposure = -0.7
    cam = camera((12.0, -64.0, 7.0), (14.5, 0, 19.5), lens=28)
    render()
    screen_points(cam, pts)


def scene_cover():
    setup_render(1920, 1080)
    world_sky(0.06, 1.5, 75)
    sun((88, 0, -60), 1.2, 3).data.color = lin("#FF9A5C")
    build_site()
    for loc, tgt in [((-14, -22, 3), (2, 0, 14)), ((44, -18, 3), (30, 4, 8))]:
        area_light(loc, tgt, 9000, 6, "#FFE2B8")
    cam = camera((-34.0, -58.0, 3.0), (-6.0, 0, 21.0), lens=26)
    bpy.context.scene.view_settings.exposure = 0.3
    render()


def scene_zone():
    setup_render(1500, 1200)
    bpy.context.scene.view_settings.exposure = -0.7
    world_sky(0.32, 35)
    sun((48, 0, -30), 4.5, 1.2).data.color = lin("#FFF1DD")
    bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(noisy("zground", "#7B746A", 0.95, 0.8, 0.18, 0.4))
    jz, dark = build_crane((10, 4, 0), H=26, jib=26, counter=8)
    zone3d(21, 4, 10, 2.2, 1.6, strength=0.18, ghost=True)                 # 직전 위치(희미하게)
    hook_load(31, 4, jz, 10, dark)
    zone3d(31, 4, 10, 2.2, 1.6)
    worker3d((32.6, 1.6, 0), 210)
    alert_ring(32.6, 1.6)
    worker3d((37.5, -1.0, 0), 150)
    beacon3d((36.0, 8.5, 0), 3.2)
    cam = camera((19.0, -15.5, 11.0), (28.5, 4.0, 5.0), lens=30)
    render()


def scene_fall():
    setup_render(1350, 1500)
    bpy.context.scene.view_settings.exposure = -0.7
    world_sky(0.32, 35)
    sun((45, 0, -25), 4.5, 1.2).data.color = lin("#FFF1DD")
    bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(noisy("fground", "#7B746A", 0.95, 0.8, 0.18, 0.4))
    top = build_building((0, 0, 0), floors=10, w=12, d=8, glass_floors=3)
    worker3d((4.6, -3.6, top + 0.14), 200)
    worker3d((3.6, -6.8, 0), 200)
    g, z0, x0 = 9.81, top + 0.6, 6.4
    named = {}
    for i, t in enumerate([0, 0.5, 1.0, 1.5, 2.0, 2.47]):
        z = max(z0 - 0.5 * g * t * t, 0.35)
        a = 0.35 + 0.65 * (i / 5)
        cyl((x0 + 0.25 * t, -4.6, z), 0.16, 1.9, mat(f"ghost{i}", ORANGE, 0.4, emit=0.3, alpha=a), rot=(0.3 + 0.5 * t, 0.9, 0.2 * t))
        named[f"t{i}"] = (x0 + 0.25 * t + 1.1, -4.6, z)
    cam = camera((4.0, -78.0, 15.5), (5.0, 0, 15.5), lens=62)
    render()
    screen_points(cam, named)


bpy.ops.wm.read_factory_settings(use_empty=True)
{"drone": scene_drone, "sim": scene_sim, "cctv": scene_cctv, "droptest": scene_droptest,
 "solution": scene_solution, "cover": scene_cover, "zone": scene_zone, "fall": scene_fall}[SCENE]()

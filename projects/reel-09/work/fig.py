"""reel-09 figure rig: a simple 3D body (cm) projected orthographically and drawn with skia.

Axes: X forward, Y up, Z = the figure's left (the curling arm, nearest the camera).
yaw = 0 is a pure side view; larger yaw turns the camera toward the figure's front.
"""
import math
import numpy as np
import skia

SKIN = (232, 182, 148)
SKIN_FAR = (205, 152, 120)
SKIN_SHADE = (214, 160, 126)
SHIRT = (52, 64, 84)
SHIRT_FAR = (40, 50, 66)
SHORTS = (30, 34, 42)
SHORTS_FAR = (22, 25, 31)
HAIR = (38, 30, 26)
SHOE = (240, 240, 236)
SHOE_FAR = (210, 210, 205)
IRON = (44, 46, 52)
IRON_HI = (88, 92, 102)


def col(c, a=255):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(a))


def paint(c, a=255):
    return skia.Paint(AntiAlias=True, Color=col(c, a))


def rotx(v, a):  # rotate about X (abduction / sideways)
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    return np.array([x, c * y - s * z, s * y + c * z])


def rotz(v, a):  # rotate about Z (forward / back swing in the side plane)
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    return np.array([c * x - s * y, s * x + c * y, z])


class Cam:
    def __init__(self, yaw_deg, scale, ox, oy):
        y = math.radians(yaw_deg)
        self.right = np.array([math.cos(y), 0.0, -math.sin(y)])
        self.toward = np.array([math.sin(y), 0.0, math.cos(y)])
        self.yaw = y
        self.s, self.ox, self.oy = scale, ox, oy

    def p(self, v):
        v = np.asarray(v, float)
        return (self.ox + self.s * float(v @ self.right), self.oy - self.s * float(v[1]))

    def depth(self, v):
        return float(np.asarray(v, float) @ self.toward)


def limb_path(cam, a, b, radii, n=24):
    """Outline of a tapered limb from a to b (3D), radii: list of (t, r) control points."""
    ts = np.linspace(0, 1, n)
    rt = np.interp(ts, [t for t, _ in radii], [r for _, r in radii])
    # smooth the radius profile a little
    pa, pb = np.array(cam.p(a)), np.array(cam.p(b))
    d = pb - pa
    L = np.hypot(*d)
    if L < 1e-6:
        path = skia.Path()
        path.addCircle(pa[0], pa[1], cam.s * max(rt))
        return path
    u = d / L
    nrm = np.array([-u[1], u[0]])
    pts = [pa + d * t for t in ts]
    left = [p + nrm * cam.s * r for p, r in zip(pts, rt)]
    right = [p - nrm * cam.s * r for p, r in zip(pts, rt)]
    path = skia.Path()
    path.moveTo(*left[0])
    for q in left[1:]:
        path.lineTo(*q)
    # end cap (half circle around b)
    ang0 = math.degrees(math.atan2(nrm[1], nrm[0]))
    r1 = cam.s * rt[-1]
    path.arcTo(skia.Rect(pb[0] - r1, pb[1] - r1, pb[0] + r1, pb[1] + r1), ang0, -180, False)
    for q in reversed(right[:-1]):
        path.lineTo(*q)
    r0 = cam.s * rt[0]
    path.arcTo(skia.Rect(pa[0] - r0, pa[1] - r0, pa[0] + r0, pa[1] + r0), ang0 + 180, -180, False)
    path.close()
    return path


def ellipsoid_path(cam, c, ax, n=48):
    """Silhouette of an axis-aligned ellipsoid centre c, half axes ax=(x,y,z)."""
    # project: screen x extent from x and z axes, y extent from y
    ex = math.sqrt((ax[0] * cam.right[0]) ** 2 + (ax[2] * cam.right[2]) ** 2)
    cx, cy = cam.p(c)
    r = skia.Rect(cx - cam.s * ex, cy - cam.s * ax[1], cx + cam.s * ex, cy + cam.s * ax[1])
    path = skia.Path()
    path.addOval(r)
    return path


def disc_path(cam, c, normal, radius, n=40):
    normal = np.asarray(normal, float)
    normal /= np.linalg.norm(normal)
    t = np.array([0, 1.0, 0]) if abs(normal[1]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(normal, t)
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    path = skia.Path()
    for i in range(n):
        a = 2 * math.pi * i / n
        q = cam.p(np.asarray(c) + radius * (math.cos(a) * u + math.sin(a) * v))
        path.moveTo(*q) if i == 0 else path.lineTo(*q)
    path.close()
    return path


# torso cross sections: y, half width (z), half depth (x), centre x
TORSO = [
    (84, 14.0, 10.0, -1.5),
    (92, 15.0, 11.0, -2.0),
    (100, 13.6, 10.0, -0.8),
    (107, 12.8, 9.4, 0.0),
    (115, 13.8, 10.4, 1.0),
    (123, 15.8, 11.8, 2.0),
    (131, 17.2, 12.3, 2.2),
    (138, 17.8, 11.4, 1.5),
    (142.5, 16.6, 9.8, 0.5),
    (146, 11.0, 7.5, 0.5),
]


def torso_path(cam, y_lo=84, y_hi=145, shrug=0.0):
    ys = np.linspace(y_lo, y_hi, 40)
    T = np.array(TORSO)
    a = np.interp(ys, T[:, 0], T[:, 1])
    b = np.interp(ys, T[:, 0], T[:, 2])
    c = np.interp(ys, T[:, 0], T[:, 3])
    yy = ys + shrug * np.clip((ys - 128) / 17, 0, 1)
    e = np.sqrt((b * cam.right[0]) ** 2 + (a * cam.right[2]) ** 2)
    L, R = [], []
    for y, ee, cc in zip(yy, e, c):
        x0, sy = cam.p((cc, y, 0))
        L.append((x0 - cam.s * ee, sy))
        R.append((x0 + cam.s * ee, sy))
    path = skia.Path()
    pts = L + R[::-1]
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    path.close()
    return path


def torso_halfwidth(y):
    T = np.array(TORSO)
    return float(np.interp(y, T[:, 0], T[:, 1]))


class Pose:
    """flex: elbow angle from straight (deg). swing: upper arm forward (deg). abd: upper arm out to the side (deg,
    negative = pulled in). shrug: shoulder raise (cm). squeeze: how hard the elbow presses the ribs (0..1)."""

    def __init__(self, flex=10, swing=0, abd=4, shrug=0, squeeze=0, wrist=0):
        self.flex, self.swing, self.abd, self.shrug, self.squeeze, self.wrist = flex, swing, abd, shrug, squeeze, wrist


def arm_points(pose, side=1):
    sh = np.array([0.5, 141.0 + pose.shrug, side * 18.0])
    up = np.array([0, -29.5, 0])  # upper arm hanging
    up = rotx(up, math.radians(pose.abd) * side)  # rotx with +ang moves -y toward -z... fix sign below
    # rotx(+a) maps (0,-L,0) -> (0, -L cos a, -L sin a): toward -z. For side=+1 we want +z for abduction.
    up = np.array([up[0], up[1], -up[2]])
    up = rotz(up, math.radians(pose.swing))
    el = sh + up
    ua = up / np.linalg.norm(up)
    # forearm: starts along the upper arm, rotates forward/up about the lateral axis through the elbow
    fa = ua * 25.5
    fa = rotz(fa, math.radians(pose.flex))
    wr = el + fa
    return sh, el, wr


def hand_point(pose, side=1):
    sh, el, wr = arm_points(pose, side)
    d = (wr - el) / np.linalg.norm(wr - el)
    return wr + d * 4.0


class Figure:
    def __init__(self, cam):
        self.cam = cam

    def draw(self, cv, pose, rest=None, extra=None):
        """pose: the curling arm (side -1, screen right). rest: the other arm, hanging."""
        cam = self.cam
        rest = rest or Pose(flex=8, swing=0, abd=3, shrug=pose.shrug)
        P = paint
        self.leg(cv, -1, SKIN_FAR, SHORTS_FAR, SHOE_FAR)
        self.upper_arm(cv, pose, -1, SKIN_FAR, SHIRT_FAR)
        cv.drawPath(torso_path(cam, 84, 101), P(SHORTS))
        cv.drawPath(torso_path(cam, 97, 146, pose.shrug), P(SHIRT))
        if extra:
            extra(cv)
        self.leg(cv, 1, SKIN, SHORTS, SHOE)
        cv.drawPath(limb_path(cam, (1.5, 143 + pose.shrug * 0.3, 0), (2.5, 154, 0), [(0, 6.0), (1, 5.4)]), P(SKIN_SHADE))
        if pose.shrug > 0.3:
            a = min(1.0, pose.shrug / 3)
            pth = skia.Path()
            p0 = cam.p((1.0, 147 + pose.shrug * 0.5, -5))
            p1 = cam.p((0.5, 143 + pose.shrug, -16))
            pth.moveTo(*p0)
            pth.quadTo(*cam.p((0.6, 147.5 + pose.shrug, -11)), *p1)
            pt = skia.Paint(AntiAlias=True, Color=col((20, 26, 36), 170 * a), Style=skia.Paint.kStroke_Style,
                            StrokeWidth=cam.s * 0.9, StrokeCap=skia.Paint.kRound_Cap)
            cv.drawPath(pth, pt)
        self.head(cv, pose)
        self.lower_arm(cv, pose, -1, SKIN_FAR, dumbbell=True)
        self.upper_arm(cv, rest, 1, SKIN, SHIRT)
        self.lower_arm(cv, rest, 1, SKIN, dumbbell=False)

    def upper_arm(self, cv, pose, side, skin, shirt):
        cam = self.cam
        sh, el, wr = arm_points(pose, side)
        flexk = min(1.0, pose.flex / 120)
        bic = 4.9 + 1.0 * flexk
        cv.drawPath(limb_path(cam, sh, el, [(0, 5.9), (0.18, 5.5), (0.45, bic), (0.8, 4.5), (1, 4.0)]), paint(skin))
        cv.drawPath(limb_path(cam, sh + np.array([0, 2.0, 0]), sh + (el - sh) * 0.36, [(0, 6.9), (1, 6.2)]), paint(shirt))

    def lower_arm(self, cv, pose, side, skin, dumbbell):
        cam = self.cam
        sh, el, wr = arm_points(pose, side)
        if dumbbell:
            self.dumbbell(cv, pose, side, outer=True)
        # elbow joint cap so the forearm joins the upper arm cleanly when drawn over the torso
        ex, ey = cam.p(el)
        cv.drawCircle(ex, ey, cam.s * 4.1, paint(skin))
        cv.drawPath(limb_path(cam, el, wr, [(0, 4.2), (0.22, 4.6), (0.6, 3.5), (1, 2.8)]), paint(skin))
        hx, hy = cam.p(hand_point(pose, side))
        cv.drawCircle(hx, hy, cam.s * 4.3, paint(skin))
        if dumbbell:
            self.dumbbell(cv, pose, side, outer=False)

    def head(self, cv, pose):
        cam = self.cam
        hc = np.array([2.5, 163.0, 0])
        cv.drawPath(ellipsoid_path(cam, hc, (10.2, 12.0, 8.6)), paint(SKIN))
        # hair cap: upper back part of the head
        cv.save()
        clip = ellipsoid_path(cam, hc, (10.2, 12.0, 8.6))
        cv.clipPath(clip, skia.ClipOp.kIntersect, True)
        cv.drawPath(ellipsoid_path(cam, hc + np.array([-4.2, 5.2, 0]), (10.4, 9.0, 9.2)), paint(HAIR))
        cv.restore()
        # ear on the near side
        ep = hc + np.array([-1.0, -1.0, 8.4])
        ex, ey = cam.p(ep)
        r = cam.s
        cv.drawOval(skia.Rect(ex - 1.8 * r * max(0.35, math.cos(cam.yaw)), ey - 2.8 * r, ex + 1.8 * r * max(0.35, math.cos(cam.yaw)), ey + 2.8 * r), paint(SKIN_SHADE))
        # nose hint
        np_ = hc + np.array([10.0, -1.5, 0])
        nx, ny = cam.p(np_)
        pth = skia.Path()
        pth.moveTo(nx - 0.3 * r, ny - 2.6 * r)
        pth.lineTo(nx + 1.9 * r * math.cos(cam.yaw) + 0.3 * r, ny + 1.6 * r)
        pth.lineTo(nx - 0.2 * r, ny + 1.9 * r)
        pth.close()
        cv.drawPath(pth, paint(SKIN))

    def leg(self, cv, side, skin, shorts, shoe):
        cam = self.cam
        hip = np.array([-0.5, 92, side * 8.5])
        knee = np.array([1.5, 50, side * 9.5])
        ank = np.array([-0.5, 9, side * 9.5])
        cv.drawPath(limb_path(cam, hip, knee, [(0, 8.6), (0.5, 7.4), (1, 5.4)]), paint(skin))
        cv.drawPath(limb_path(cam, knee, ank, [(0, 5.2), (0.3, 5.6), (1, 3.4)]), paint(skin))
        # shorts leg
        mid = hip + (knee - hip) * 0.42
        cv.drawPath(limb_path(cam, hip + np.array([0, 2, 0]), mid, [(0, 9.0), (1, 8.0)]), paint(shorts))
        # shoe
        cv.drawPath(limb_path(cam, ank + np.array([-3, -5.5, 0]), ank + np.array([15, -6.5, 0]), [(0, 4.2), (1, 3.4)]), paint(shoe))

    def dumbbell(self, cv, pose, side, outer):
        cam = self.cam
        hp = hand_point(pose, side)
        axis = np.array([0, 0, 1.0 * side])  # outward along the handle
        zoff = 8.5 if outer else -8.5
        c = hp + axis * zoff
        cv.drawPath(limb_path(cam, hp, c, [(0, 1.5), (1, 1.5)]), paint(IRON))
        cv.drawPath(disc_path(cam, c, axis, 8.3), paint(IRON))
        face = c + axis * (-1.3 if not outer else 1.3)
        cv.drawPath(disc_path(cam, face, axis, 8.3), paint(IRON_HI))
        cv.drawPath(disc_path(cam, face, axis, 2.6), paint(IRON))


def new_surface(w, h, bg):
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    cv.clear(col(bg))
    return surf, cv


def to_rgb(surf):
    a = surf.makeImageSnapshot().toarray()
    return a[:, :, [2, 1, 0]].copy() if surf.imageInfo().colorType() == skia.ColorType.kBGRA_8888_ColorType else a[:, :, :3].copy()

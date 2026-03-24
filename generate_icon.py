#!/usr/bin/env python3
"""
GymApp Icon v3
Robotic arm in bicep-curl pose, gripping a blue gem dumbbell.
Red radial background. Clean vector-illustration style with 3-tone shading.
"""
import os, math
from PIL import Image, ImageDraw

# ═══ PALETTE ══════════════════════════════════════════════════════════════════
BG_EDGE  = ( 80,  8,  8)
BG_MID   = (155, 20, 20)
BG_CENT  = (205, 42, 42)

A_HL   = (218, 224, 232)   # arm highlight
A_MID  = (148, 156, 168)   # arm midtone
A_SHD  = ( 68,  74,  84)   # arm shadow
A_OUT  = ( 14,  16,  20)   # arm outline

P_HL   = (120, 190, 255)   # plate highlight
P_MID  = ( 37, 100, 238)   # plate midtone
P_SHD  = ( 18,  48, 140)   # plate shadow
P_OUT  = (  5,  15,  52)   # plate outline

BAR    = ( 50, 115, 240)   # bar

# ═══ PRIMITIVES ═══════════════════════════════════════════════════════════════

def lerp_c(a, b, t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

def cap_pts(x1,y1,x2,y2,w):
    dx,dy = x2-x1, y2-y1
    L = math.hypot(dx,dy)
    if L < 0.5: return [(x1,y1)]*4
    nx,ny = -dy/L*(w/2), dx/L*(w/2)
    return [(x1+nx,y1+ny),(x2+nx,y2+ny),(x2-nx,y2-ny),(x1-nx,y1-ny)]

def draw_cap(d, x1,y1,x2,y2, w, col):
    r = w/2
    d.polygon(cap_pts(x1,y1,x2,y2,w), fill=col)
    d.ellipse([x1-r,y1-r,x1+r,y1+r], fill=col)
    d.ellipse([x2-r,y2-r,x2+r,y2+r], fill=col)

def draw_circ(d, cx,cy,r, col):
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col)

def ell_pts(cx,cy,rx,ry, ang_off=0, N=32):
    return [(cx + rx*math.cos(math.radians(i*360/N + ang_off)),
             cy + ry*math.sin(math.radians(i*360/N + ang_off))) for i in range(N)]

def ngon(cx,cy,r,N, ang_off=0):
    return [(cx + r*math.cos(math.radians(i*360/N + ang_off)),
             cy + r*math.sin(math.radians(i*360/N + ang_off))) for i in range(N)]

# ═══ STYLED COMPONENTS ════════════════════════════════════════════════════════

def arm_seg(d, x1,y1,x2,y2, w, ow):
    """Capsule with outline → shadow → base → highlight. Light from upper-left."""
    draw_cap(d, x1,    y1,    x2,    y2,    w+ow*2, A_OUT)
    draw_cap(d, x1+ow*.5, y1+ow*.6, x2+ow*.5, y2+ow*.6, w, A_SHD)
    draw_cap(d, x1,    y1,    x2,    y2,    w,      A_MID)
    draw_cap(d, x1-ow*.28, y1-ow*.32, x2-ow*.28, y2-ow*.32,
             int(w*.50), A_HL)

def arm_joint(d, cx,cy,r, ow):
    """Round joint: outline → shadow → base → highlight + inner bolt."""
    draw_circ(d, cx,      cy,      r+ow,     A_OUT)
    draw_circ(d, cx+ow*.5, cy+ow*.6, r,       A_SHD)
    draw_circ(d, cx,      cy,      r,        A_MID)
    draw_circ(d, cx-ow*.28,cy-ow*.32, int(r*.60), A_HL)
    draw_circ(d, cx,      cy,      int(r*.26), A_OUT)
    draw_circ(d, cx,      cy,      int(r*.14), A_MID)

def arm_oval(d, cx,cy,rx,ry, ang, ow):
    """Big oval housing (bicep shell): outline → shadow → base → highlight + seam."""
    outer = ell_pts(cx,       cy,       rx+ow, ry+ow, ang)
    base  = ell_pts(cx,       cy,       rx,    ry,    ang)
    shd   = ell_pts(cx+ow*.5, cy+ow*.6, rx,    ry,    ang)
    hl    = ell_pts(cx-ow*.28,cy-ow*.32,rx*.56,ry*.56,ang)

    d.polygon(outer, fill=A_OUT)
    d.polygon(shd,   fill=A_SHD)
    d.polygon(base,  fill=A_MID)
    d.polygon(hl,    fill=A_HL)

    # Seam groove across the middle (horizontal panel line)
    seam = ell_pts(cx, cy, rx*.96, ry*.07, ang+90)
    d.polygon(seam, fill=A_OUT)
    seam2 = ell_pts(cx, cy, rx*.96, ry*.035, ang+90)
    d.polygon(seam2, fill=A_SHD)

def robotic_fist(d, cx,cy, fw,fh, ow):
    """
    Mechanical fist gripping the bar.
    4 finger knuckles on top, rectangular palm below.
    """
    kh = int(fh * .40)   # knuckle row height
    ph = fh - kh         # palm height
    kw = fw // 4         # width per knuckle

    # ── Palm ──
    py0 = cy - ph//2
    py1 = cy + ph//2
    # outline
    d.polygon([(cx-fw//2-ow, py0-ow),(cx+fw//2+ow, py0-ow),
               (cx+fw//2+ow, py1+ow),(cx-fw//2-ow, py1+ow)], fill=A_OUT)
    # shadow
    d.polygon([(cx-fw//2+ow*.5, py0+ow*.6),(cx+fw//2+ow*.5, py0+ow*.6),
               (cx+fw//2+ow*.5, py1+ow*.6),(cx-fw//2+ow*.5, py1+ow*.6)],
              fill=A_SHD)
    # base
    d.polygon([(cx-fw//2, py0),(cx+fw//2, py0),
               (cx+fw//2, py1),(cx-fw//2, py1)], fill=A_MID)
    # highlight (left-top strip)
    d.polygon([(cx-fw//2,     py0),(cx+fw//4, py0),
               (cx+fw//4,     cy-ow*2),(cx-fw//2, cy-ow*2)], fill=A_HL)

    # Knuckle divider lines on palm
    for i in range(1,4):
        lx = cx - fw//2 + i*kw
        d.line([(lx, py0+ow*2),(lx, py1-ow*2)], fill=A_OUT,
               width=max(1, ow//3))

    # ── Knuckle row (above palm) ──
    ky = cy - ph//2 - kh//2
    for i in range(4):
        kx = cx - fw//2 + kw//2 + i*kw
        kr = kw//2 - ow//2
        draw_circ(d, int(kx), int(ky), kr+ow,        A_OUT)
        draw_circ(d, int(kx)+int(ow*.5), int(ky)+int(ow*.6), kr, A_SHD)
        draw_circ(d, int(kx), int(ky), kr,            A_MID)
        draw_circ(d, int(kx-kr*.3), int(ky-kr*.3), int(kr*.46), A_HL)

def gem_plate(d, cx,cy,r, ow):
    """
    Blue gem plate: 12-gon outer ring with triangular facets radiating inward.
    3-tone shading: shadow base → mid → highlight facets.
    """
    N = 12
    step = 360 / N
    # vertices
    outer = ngon(cx, cy, r,       N, -90)
    mid   = ngon(cx, cy, r*.58,   N, -90 + step/2)  # inner ring, offset
    inner = ngon(cx, cy, r*.22,   N, -90)

    # Outline
    out_pts = ngon(cx, cy, r+ow, N, -90)
    d.polygon(out_pts, fill=P_OUT)

    # Shadow base (slightly shifted)
    shd_pts = [(cx+ow*.35 + r*math.cos(math.radians(i*step-90)),
                cy+ow*.45 + r*math.sin(math.radians(i*step-90))) for i in range(N)]
    d.polygon(shd_pts, fill=P_SHD)

    # Base fill
    d.polygon(outer, fill=P_MID)

    # Facets: each outer edge → inner ring vertex
    for i in range(N):
        o1  = outer[i]
        o2  = outer[(i+1) % N]
        m   = mid[i]
        # alternate highlight / midtone / shadow per facet group
        frac = (math.cos(math.radians(i*step - 90 - 40)) + 1) / 2  # light from upper-left
        if frac > 0.62:
            col = P_HL
        elif frac > 0.28:
            col = P_MID
        else:
            col = P_SHD
        d.polygon([o1, o2, m], fill=col)

    # Inner hex
    d.polygon(inner, fill=P_OUT)
    d.polygon(ngon(cx,cy,r*.14,N,-90), fill=P_HL)

    # Outline redraw (on top of facets, so edges are crisp)
    d.polygon(out_pts, fill=P_OUT)
    d.polygon(outer,   fill=None, outline=P_OUT)   # wire outline only? No, polygon fills
    # Just redraw thin outline ring
    for i in range(N):
        d.line([outer[i], outer[(i+1)%N]], fill=P_OUT,
               width=max(1, ow//2))

# ═══ MAIN ICON ════════════════════════════════════════════════════════════════

def create_icon(size=1024):
    s  = size
    sc = s / 1024.0
    ow = max(3, int(sc * 10))

    img  = Image.new('RGBA', (s,s), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # ── Red radial background ─────────────────────────────────────────────────
    draw.rounded_rectangle([0,0,s-1,s-1], radius=int(s*.22), fill=BG_EDGE)
    cx_, cy_ = s//2, s//2
    for i in range(30, 0, -1):
        t  = i / 30.0
        rx = int(s * .82 * t)
        col = lerp_c(BG_CENT, BG_EDGE, t ** .70)
        draw.ellipse([cx_-rx, cy_-rx, cx_+rx, cy_+rx], fill=col)
    # re-clip to rounded square
    mask_bg = Image.new('L',(s,s),0)
    ImageDraw.Draw(mask_bg).rounded_rectangle([0,0,s-1,s-1], radius=int(s*.22), fill=255)
    img.putalpha(mask_bg)
    draw = ImageDraw.Draw(img)

    # ── Layout: bicep-curl pose ───────────────────────────────────────────────
    # Dumbbell: near-horizontal at top
    DB_ANG   = -13
    DB_CX    = s * 0.497
    DB_CY    = s * 0.238
    BAR_HALF = s * 0.228
    BAR_H    = s * 0.040
    PL_R     = int(s * 0.116)

    cos_d = math.cos(math.radians(DB_ANG))
    sin_d = math.sin(math.radians(DB_ANG))

    # Fist grips bar (slightly right of center)
    FST_X  = int(DB_CX + s*.010)
    FST_Y  = int(DB_CY + s*.108)
    FST_W  = int(s*.128)
    FST_H  = int(s*.115)

    # Wrist joint (below fist)
    WR_X   = int(FST_X + s*.018)
    WR_Y   = int(FST_Y + s*.082)
    WR_R   = int(s*.062)

    # Forearm: wrist → elbow (sweeping down-right)
    EL_X   = int(s*.610)
    EL_Y   = int(s*.572)
    EL_R   = int(s*.082)
    FORE_W = int(s*.120)

    # Upper arm: elbow → shoulder (going down, slight leftward)
    SH_X   = int(s*.585)
    SH_Y   = int(s*.872)
    SH_R   = int(s*.090)
    UPP_W  = int(s*.175)   # thick — becomes the bicep body

    # Bicep oval housing (centered on upper-arm segment)
    mx = (EL_X + SH_X) // 2
    my = (EL_Y + SH_Y) // 2
    arm_ang = math.degrees(math.atan2(SH_Y-EL_Y, SH_X-EL_X))  # ≈ -80°
    BIC_CX  = mx - int(s*.020)
    BIC_CY  = my
    BIC_RX  = int(s*.200)
    BIC_RY  = int(s*.148)
    BIC_ANG = arm_ang + 5   # align loosely with upper arm

    # ── Draw: back → front ───────────────────────────────────────────────────

    # 1. Bar (behind fist, drawn first)
    bx1 = DB_CX - cos_d*BAR_HALF
    by1 = DB_CY - sin_d*BAR_HALF
    bx2 = DB_CX + cos_d*BAR_HALF
    by2 = DB_CY + sin_d*BAR_HALF
    draw_cap(draw, bx1,by1, bx2,by2, BAR_H + ow*2, P_OUT)
    draw_cap(draw, bx1,by1, bx2,by2, BAR_H, BAR)
    draw_cap(draw, bx1,by1, bx2,by2, int(BAR_H*.32), P_HL)  # bar highlight

    # 2. Bicep oval housing
    arm_oval(draw, BIC_CX, BIC_CY, BIC_RX, BIC_RY, BIC_ANG, ow)

    # 3. Shoulder joint
    arm_joint(draw, SH_X, SH_Y, SH_R, ow)

    # 4. Upper arm (on top of oval — merges into it)
    arm_seg(draw, SH_X, SH_Y, EL_X, EL_Y, UPP_W, ow)

    # 5. Elbow joint
    arm_joint(draw, EL_X, EL_Y, EL_R, ow)

    # 6. Forearm
    arm_seg(draw, EL_X, EL_Y, WR_X, WR_Y, FORE_W, ow)

    # 7. Wrist joint
    arm_joint(draw, WR_X, WR_Y, WR_R, ow)

    # 8. Robotic fist
    robotic_fist(draw, FST_X, FST_Y, FST_W, FST_H, ow)

    # 9. Plates (front-most, drawn last)
    lp_x = int(DB_CX - cos_d*(BAR_HALF + PL_R*.06))
    lp_y = int(DB_CY - sin_d*(BAR_HALF + PL_R*.06))
    rp_x = int(DB_CX + cos_d*(BAR_HALF + PL_R*.06))
    rp_y = int(DB_CY + sin_d*(BAR_HALF + PL_R*.06))
    gem_plate(draw, lp_x, lp_y, PL_R, ow)
    gem_plate(draw, rp_x, rp_y, PL_R, ow)

    # Final rounded-square clip
    mask = Image.new('L',(s,s),0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,s-1,s-1], radius=int(s*.22), fill=255)
    img.putalpha(mask)

    return img

# ═══ SIZE TABLES & OUTPUT ═════════════════════════════════════════════════════

ANDROID_SIZES = {
    'mipmap-mdpi':    48,
    'mipmap-hdpi':    72,
    'mipmap-xhdpi':   96,
    'mipmap-xxhdpi':  144,
    'mipmap-xxxhdpi': 192,
}

IOS_ICONS = [
    ('Icon-20@1x',   20), ('Icon-20@2x',  40), ('Icon-20@3x',   60),
    ('Icon-29@1x',   29), ('Icon-29@2x',  58), ('Icon-29@3x',   87),
    ('Icon-40@1x',   40), ('Icon-40@2x',  80), ('Icon-40@3x',  120),
    ('Icon-60@2x',  120), ('Icon-60@3x', 180),
    ('Icon-76@1x',   76), ('Icon-76@2x', 152),
    ('Icon-83.5@2x',167),
    ('Icon-1024',  1024),
]

def generate_all():
    base_dir = '/Users/basargorgundur/Desktop/GymApp'
    print('Rendering 1024×1024...')
    base = create_icon(1024)
    base.save(os.path.join(base_dir, 'icon_preview_1024.png'))
    print('  Saved icon_preview_1024.png')

    android_res = os.path.join(base_dir, 'android/app/src/main/res')
    print('\nAndroid:')
    for folder, sz in ANDROID_SIZES.items():
        path = os.path.join(android_res, folder)
        os.makedirs(path, exist_ok=True)
        ico = base.resize((sz, sz), Image.LANCZOS)
        ico.save(os.path.join(path, 'ic_launcher.png'))
        ico.save(os.path.join(path, 'ic_launcher_round.png'))
        print(f'  {folder}: {sz}×{sz}')

    ios_path = os.path.join(base_dir,
        'ios/GymApp/Images.xcassets/AppIcon.appiconset')
    os.makedirs(ios_path, exist_ok=True)
    print('\niOS:')
    for name, sz in IOS_ICONS:
        ico = base.resize((sz, sz), Image.LANCZOS)
        ico.save(os.path.join(ios_path, f'{name}.png'))
        print(f'  {name}: {sz}×{sz}')

    print('\nAll done!')

if __name__ == '__main__':
    generate_all()

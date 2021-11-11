"""
Signed distance drawing functions using numpy.
"""
import math

import numpy as np
from numpy import linalg as npla


def vector2_dot(a,b):
    return a[...,0]*b[...,0]+a[...,1]*b[...,1]

def vector2_dot2(a):
    return a[...,0]*a[...,0]+a[...,1]*a[...,1]

def vector2_cross(a,b):
    return a[...,0]*b[...,1]-a[...,1]*b[...,0]


def circle_faded( wh, center, fade_dists ):
    """
    returns drawn circle in [h,w,1] output range [0..1.0] float32

    wh         = [w,h]                      resolution
    center     = [x,y]                      center of circle
    fade_dists = [fade_start, fade_end]     fade values
    """
    w,h = wh

    pts = np.empty( (h,w,2), dtype=np.float32 )
    pts[...,0] = np.arange(w)[:,None]
    pts[...,1] = np.arange(h)[None,:]

    pts = pts.reshape ( (h*w, -1) )

    pts_dists = np.abs ( npla.norm(pts-center, axis=-1) )

    if fade_dists[1] == 0:
        fade_dists[1] = 1

    pts_dists = ( pts_dists - fade_dists[0] ) / fade_dists[1]

    pts_dists = np.clip( 1-pts_dists, 0, 1)

    return pts_dists.reshape ( (h,w,1) ).astype(np.float32)


def bezier( wh, A, B, C ):
    """
    returns drawn bezier in [h,w,1] output range float32,
    every pixel contains signed distance to bezier line

        wh      [w,h]       resolution
        A,B,C   points [x,y]
    """

    width,height = wh

    A = np.float32(A)
    B = np.float32(B)
    C = np.float32(C)


    pos = np.empty( (height,width,2), dtype=np.float32 )
    pos[...,0] = np.arange(width)[:,None]
    pos[...,1] = np.arange(height)[None,:]


    a = B-A
    b = A - 2.0*B + C
    c = a * 2.0
    d = A - pos

    b_dot = vector2_dot(b,b)
    if b_dot == 0.0:
        return np.zeros( (height,width), dtype=np.float32 )

    kk = 1.0 / b_dot

    kx = kk * vector2_dot(a,b)
    ky = kk * (2.0*vector2_dot(a,a)+vector2_dot(d,b))/3.0;
    kz = kk * vector2_dot(d,a);

    res = 0.0;
    sgn = 0.0;

    p = ky - kx*kx;

    p3 = p*p*p;
    q = kx*(2.0*kx*kx - 3.0*ky) + kz;
    h = q*q + 4.0*p3;

    hp_sel = h >= 0.0

    hp_p = h[hp_sel]
    hp_p = np.sqrt(hp_p)

    hp_x = ( np.stack( (hp_p,-hp_p), -1) -q[hp_sel,None] ) / 2.0
    hp_uv = np.sign(hp_x) * np.power( np.abs(hp_x), [1.0/3.0, 1.0/3.0] )
    hp_t = np.clip( hp_uv[...,0] + hp_uv[...,1] - kx, 0.0, 1.0 )

    hp_t = hp_t[...,None]
    hp_q = d[hp_sel]+(c+b*hp_t)*hp_t
    hp_res = vector2_dot2(hp_q)
    hp_sgn = vector2_cross(c+2.0*b*hp_t,hp_q)

    hl_sel = h < 0.0

    hl_q = q[hl_sel]
    hl_p = p[hl_sel]
    hl_z = np.sqrt(-hl_p)
    hl_v = np.arccos( hl_q / (hl_p*hl_z*2.0)) / 3.0

    hl_m = np.cos(hl_v)
    hl_n = np.sin(hl_v)*1.732050808;

    hl_t = np.clip( np.stack( (hl_m+hl_m,-hl_n-hl_m,hl_n-hl_m), -1)*hl_z[...,None]-kx, 0.0, 1.0 );

    hl_d = d[hl_sel]

    hl_qx = hl_d+(c+b*hl_t[...,0:1])*hl_t[...,0:1]

    hl_dx = vector2_dot2(hl_qx)
    hl_sx = vector2_cross(c+2.0*b*hl_t[...,0:1], hl_qx)

    hl_qy = hl_d+(c+b*hl_t[...,1:2])*hl_t[...,1:2]
    hl_dy = vector2_dot2(hl_qy)
    hl_sy = vector2_cross(c+2.0*b*hl_t[...,1:2],hl_qy);

    hl_dx_l_dy = hl_dx<hl_dy
    hl_dx_ge_dy = hl_dx>=hl_dy

    hl_res = np.empty_like(hl_dx)
    hl_res[hl_dx_l_dy] = hl_dx[hl_dx_l_dy]
    hl_res[hl_dx_ge_dy] = hl_dy[hl_dx_ge_dy]

    hl_sgn = np.empty_like(hl_sx)
    hl_sgn[hl_dx_l_dy] = hl_sx[hl_dx_l_dy]
    hl_sgn[hl_dx_ge_dy] = hl_sy[hl_dx_ge_dy]

    res = np.empty( (height, width), np.float32 )
    res[hp_sel] = hp_res
    res[hl_sel] = hl_res

    sgn = np.empty( (height, width), np.float32 )
    sgn[hp_sel] = hp_sgn
    sgn[hl_sel] = hl_sgn

    sgn = np.sign(sgn)
    res = np.sqrt(res)*sgn

    return res[...,None]

def random_faded(wh):
    """
    apply one of them:
     random_circle_faded
     random_bezier_split_faded
    """
    rnd = np.random.randint(2)
    if rnd == 0:
        return random_circle_faded(wh)
    elif rnd == 1:
        return random_bezier_split_faded(wh)

def random_circle_faded ( wh, rnd_state=None ):
    if rnd_state is None:
        rnd_state = np.random

    w,h = wh
    wh_max = max(w,h)
    fade_start = rnd_state.randint(wh_max)
    fade_end = fade_start + rnd_state.randint(wh_max- fade_start)

    return circle_faded (wh, [ rnd_state.randint(h), rnd_state.randint(w) ],
                             [fade_start, fade_end] )

def random_circle_faded_multi( wh, complexity=1, rnd_state=None):
    mask = random_circle_faded( wh, rnd_state=rnd_state )
    while True:
        complexity -= 1
        if complexity == 0:
            break

        opacity = random_circle_faded( wh, rnd_state=rnd_state )
        add_mask = random_circle_faded( wh, rnd_state=rnd_state )

        mask *= opacity
        mask += add_mask*(1-opacity)

        mask *= random_circle_faded( wh, rnd_state=rnd_state )
    return mask

def random_bezier_split_faded( wh ):
    width, height = wh

    degA = np.random.randint(360)
    degB = np.random.randint(360)
    degC = np.random.randint(360)

    deg_2_rad = math.pi / 180.0

    center = np.float32([width / 2.0, height / 2.0])

    radius = max(width, height)

    A = center + radius*np.float32([ math.sin( degA * deg_2_rad), math.cos( degA * deg_2_rad) ] )
    B = center + np.random.randint(radius)*np.float32([ math.sin( degB * deg_2_rad), math.cos( degB * deg_2_rad) ] )
    C = center + radius*np.float32([ math.sin( degC * deg_2_rad), math.cos( degC * deg_2_rad) ] )

    x = bezier( (width,height), A, B, C )

    x = x / (1+np.random.randint(radius)) + 0.5

    x = np.clip(x, 0, 1)
    return x

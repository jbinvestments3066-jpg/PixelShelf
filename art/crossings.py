"""Side-view crossings use a single contact surface in display coordinates."""
from stage import *


def path_height(x,left,right,bank,rise):
    u=max(0,min(1,(x-left)/(right-left)))
    return bank-round(rise*4*u*(1-u))


def footbridge(s,left,right,bank,rise,stone=False):
    # Banks end at the springers. Only the creek bed carries water marks.
    s.line((-1,bank),(left,bank),(left+3,bank+5),(left+5,52))
    s.line((right-5,52),(right-3,bank+5),(right,bank),(128,bank))
    for xx in range(left+8,right-6,13):
        s.line((xx,49+xx%2),(xx+4,49+xx%2))
    top=[(x,path_height(x,left,right,bank,rise)) for x in range(left,right+1)]
    if stone:
        intrados=[]
        for x in range(left,right+1):
            u=(x-left)/(right-left)
            intrados.append((x,round(bank+9-4*(rise+6)*u*(1-u))))
        s.poly(*top,*reversed(intrados))
        for xx in range(left+4,right,8):
            yy=path_height(xx,left,right,bank,rise)
            s.line((xx,yy+1),(xx-1,yy+2))
    else:
        s.line(*top)
        for xx in (left+1,right-1):
            s.line((xx,bank-5),(xx,bank+4),w=2)
        rope=[]
        for xx in range(left+1,right):
            u=(xx-left)/(right-left)
            rope.append((xx,bank-6+round(8*u*(1-u))))
        s.line(*rope)
        for xx in range(left+7,right-2,9):
            yy=path_height(xx,left,right,bank,rise)
            s.line((xx,rope[xx-left-1][1]),(xx,yy))


def railbed(s,y,left,right):
    # Rail head, stone approaches, two timber bents and diagonal braces below the ties.
    s.line((0,y),(127,y))
    s.line((0,y+2),(left,y+2),(left+4,y+6),(left+5,52))
    s.line((right-5,52),(right-3,y+6),(right,y+2),(127,y+2))
    s.line((left,y+2),(right,y+2))
    for xx in range(2,127,7):s.dot(xx,y+1)
    for xx in range(left+9,right-7,18):
        s.line((xx,y+3),(xx-1,51));s.line((xx+3,y+3),(xx+4,51))
        s.line((xx+4,50),(min(xx+18,right),y+3))


def tunnel(s,mouth,rail):
    # A side-on train enters the shaded near wall. The far half of the arch stays visible overhead.
    portal=[(mouth-9,rail-14),(mouth-8,rail-18),(mouth-4,rail-21),
            (mouth+1,rail-21),(mouth+5,rail-18),(mouth+6,rail-14),(mouth+6,rail+2)]
    side=[(mouth,rail+3),(mouth,rail-14),(mouth-2,rail-17),(mouth-6,rail-17),
          (mouth-9,rail-14),(mouth-8,rail-19),(mouth-4,rail-22),(mouth+3,rail-22),
          (mouth+12,rail-25),(mouth+16,rail-24),(130,rail-27),(130,54),(mouth+7,54)]
    s.poly(*side,edge=0)
    s.line(*portal)
    s.line((mouth,rail+2),(mouth,rail-14),(mouth-2,rail-17),(mouth-6,rail-17),(mouth-9,rail-14))
    s.line((mouth-4,rail-21),(mouth-4,rail-19));s.line((mouth+2,rail-21),(mouth,rail-18))
    s.line((mouth+5,rail-19),(mouth+11,rail-24),(mouth+17,rail-23),(130,rail-26))
    for dy in (-10,-5,0):s.line((mouth+1,rail+dy),(mouth+5,rail+dy-1))
    s.line((mouth+10,rail+5),(mouth+13,rail+1),(mouth+17,rail))


def locomotive(s,x,rail):
    # Wheel rims meet y=rail. Axle motion comes from distance, so a parked train holds.
    cy=rail-3
    for offset in (-44,-23):
        xx=x+offset
        s.box(xx-9,rail-13,18,8);s.line((xx-10,rail-14),(xx+9,rail-14))
        for dx in (-6,-1,4):s.box(xx+dx,rail-11,2,2,1)
        for dx in (-5,5):s.wheel(xx+dx,rail-2,2,x/2)
        s.line((xx+9,rail-5),(xx+12,rail-5))
    s.box(x-11,rail-15,8,10);s.box(x-9,rail-13,3,4,1)
    s.line((x-12,rail-16),(x-2,rail-16))
    s.box(x-3,rail-11,10,6);s.line((x+7,rail-10),(x+9,rail-8),(x+9,rail-5))
    s.box(x+3,rail-15,2,4,1);s.line((x+2,rail-16),(x+6,rail-16))
    for dx in (-7,0,7):s.wheel(x+dx,cy,3,x/3)
    s.line((x-7,cy+sin(x/3)),(x+7,cy+sin(x/3)))
    s.line((x+9,rail-6),(x+13,rail-2),(x+9,rail-2))
    for i in range(4):
        u=(s.t/8+i/4)%1
        s.line((x+4-u*18,rail-18-u*10),(x+3-u*20,rail-18-u*10))

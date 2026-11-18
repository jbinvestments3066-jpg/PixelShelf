from stage import *

def metro(s,t):
    s.city(0,32)
    s.box(4,13,17,6);s.line((7,17),(10,15),(13,17),(17,14))
    s.line((0,41),(127,41));s.line((0,44),(127,44))
    for xx in (14,54,97):
        s.line((xx,45),(xx+2,47),(xx+2,51));s.line((xx+6,45),(xx+4,47),(xx+4,51))
    front=wrap(39+t*213/120,213,10)
    for i in range(3):
        x=front-i*24
        s.poly((x-21,31),(x-2,31),(x+1,34),(x+1,38),(x-21,38))
        for dx in (-18,-13,-8):s.box(x+dx,33,2,2,1)
        s.line((x-3,33),(x-1,34));s.line((x-23,36),(x-22,36))
        for dx in (-17,-3):s.line((x+dx,39),(x+dx+2,39),w=2)
    for i in range(2):
        x=wrap(151-i*63-t*160/60);y=5+i*7+wave(t,24)
        s.poly((x-5,y),(x-2,y-2),(x+2,y-2),(x+5,y),(x+3,y+1),(x-4,y+1))


def cyber_rider(s,t):
    s.city(160*t/60,25);s.line((0,43),(127,43))
    for i in range(6):
        x=wrap(i*30-t*160/6);s.line((x,47),(x+12,47))
    x=40+19*wave(t,120);y=38
    for dx in (-9,9):s.wheel(x+dx,y,5,t*tau/2)
    s.poly((x-10,y),(x-5,y-5),(x+1,y-6),(x+8,y-2),(x+3,y),(x-2,y-1))
    s.oval(x+2,y-11,3,3,1);s.line((x+1,y-8),(x-3,y-5),(x+4,y-5),(x+7,y-7))
    # Passing tunnel mouths frame short pools of negative space.
    for when in (24,82):
        if when<t<when+9:
            xx=148-(t-when)*19
            s.poly((xx,42),(xx,6),(xx+6,2),(xx+24,2),(xx+24,5),(xx+8,5),(xx+4,10),(xx+4,42))
    for i in range(2):
        post=wrap(68+i*85-t*170/120,170,15)
        s.line((post,42),(post,8),(post+9,6),w=2);s.line((post+5,9),(post+10,8))

def rooftop(s,t):
    s.city(0,29);s.wind(6)
    s.box(-2,38,95,16);s.box(56,26,17,11);s.line((58,28),(69,28))
    for j in range(3):s.line((58,30+j*2),(60+int(t*1.5+j)%9,30+j*2))
    s.person(50,38,'cloak',1,0);s.line((51,33),(57,33+wave(t,2)))
    s.line((84,37),(84,15),(91,12));s.dot(84,13)
    x=64+48*wave(t,120);y=12+4*wave(t,30)
    s.box(x-4,y-2,8,3);s.line((x-8,y-2),(x+8,y-2))
    if 26<t<75:s.line((x,y+3),(x+8*wave(t,12),29))
    if 78<t<104:s.glow(65,21,3+2*wave(t,4))

def last_robot(s,t):
    s.city(0,26);s.ground(45);s.box(5,29,12,15);s.line((12,31),(9,36),(13,36),(10,40))
    s.line((76,45),(76,18),(88,18));s.box(84,18,9,3)
    if wave(t,8)>.25:s.line((86,24),(84,27));s.line((91,24),(93,28))
    x=track(t,(0,22),(28,60),(42,60),(65,86),(76,86),(106,22),(120,22))
    s.person(x,44,'robot',1 if t<76 else -1,1.8*sin(x*.8))
    # The supply chute dispenses the next bearing after the robot docks.
    if t<35:s.wheel(64,42,2,0)
    elif t<107:s.wheel(x+4,40,2,0)
    elif t<112:s.wheel(track(t,(107,26),(112,15)),40,2,0)
    if t>=113:
        yy=track(t,(113,32),(118,42));s.wheel(64,yy,2,0)
    s.line((59,29),(62,32),(66,32))
    if t<12 or t>106:s.line((18,36),(20,34),(22,36))

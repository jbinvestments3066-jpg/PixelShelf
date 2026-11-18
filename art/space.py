from stage import *

def lunar_explorer(s,t):
    s.stars(10);s.oval(94,10,9,7);s.line((82,13),(95,9),(106,6))
    s.ridge(32,6);s.oval(68,47,9,2);s.oval(105,39,4,1)
    s.poly((6,37),(10,25),(21,25),(25,37));s.box(12,28,5,3,1)
    for xx in (7,26):s.line((16,33),(xx,41),(xx-3,41))
    x=track(t,(0,21),(24,51),(37,51),(59,85),(73,85),(87,57),(92,57),(112,21),(120,21))
    face=1 if t<73 or t>114 else -1
    height=track(t,(0,0),(26,0),(32,11),(87,11),(92,0),(120,0))
    if height>=2:s.flag(55,41,height)
    s.person(x,41,'astronaut',face,1.7*sin(x*.7))
    if 61<t<111:s.box(x+face*5-1,36,3,3)
    elif t<61:s.oval(89,40,2,1,1)
    s.line((1,42),(27,42));s.line((49,42),(58,42));s.line((81,42),(94,42))


def black_hole_expedition(s,t):
    s.stars(23); cx,cy=84,25
    for i in range(22):
        a=tau*(i/22+t/24); r=17+i%5*3
        def arc(v):return cx+r*cos(v),cy+r*(.28*sin(v)-.24*cos(v))
        s.line(arc(a),arc(a+.18))
    # Lensed upper rim and an uninterrupted, slanted foreground accretion band.
    s.oval(cx,cy,11,11,0,0)
    s.line(*[(cx+11*cos(a*pi/24),cy-11*sin(a*pi/24)) for a in range(2,24)])
    s.line((58,33),(70,31),(86,26),(99,21),(110,17))
    s.line((68,33),(81,30),(94,25),(102,21))
    danger=swell(t,30,94); x=track(t,(0,-17),(35,33),(72,56),(84,47),(102,-17),(120,-17))
    s.ship(x,22+danger*12+2*wave(t,15),.8,1 if t<72 else -1)
    for i in range(8):
        a=i+tau*t/30;r=34+i%3*3;s.line((cx+r*cos(a),cy+r*.55*sin(a)),(cx+(r+danger*5)*cos(a+.05),cy+r*.55*sin(a+.05)))

def asteroid_runner(s,t):
    s.stars(17)
    for layer in range(2):
        for i in range(7 if not layer else 4):
            x=wrap(i*43-t*(2+layer*4)*160/120)
            y=([5,46,2,49][i] if layer else 7+(i*17)%40);r=2+layer*2+(i%3)
            a=tau*t/(30 if layer else 60)+i
            s.poly(*[(x+cos(a+j*tau/7)*r*(1+.16*(j%2)),y+sin(a+j*tau/7)*r) for j in range(7)])
            if layer:s.line((x-2,y),(x,y-2),(x+2,y-2))
        if not layer:
            evade=4*swell(t,18,28)-4*swell(t,55,67)+4*swell(t,87,98)
            x=43+15*wave(t,120);y=27+3*wave(t,40)+2*wave(t,15)+evade
            s.ship(x,y);s.line((x-13,y),(x-17-5*swell(t,71,89),y+1))

def alien_frontier(s,t):
    s.stars(8);s.moon(89,9,6);s.oval(108,14,3,3);s.ridge(39,20)
    s.ground(45)
    for x,h in [(4,13),(17,7),(94,8),(122,19)]:
        s.line((x,45),(x-2,45-h),(x+2,44-h));s.oval(x-2,44-h,4,2)
        s.line((x,41),(x+4,37),(x+5,34));s.dot(x+5,33)
    y=track(t,(0,-10),(25,19),(40,41),(77,41),(97,13),(110,-10),(120,-10))
    x=track(t,(0,36),(40,57),(77,57),(115,80))
    s.ship(x,y)
    for dx in (-7,7):s.line((x+dx,y+2),(x+dx,y+4),(x+dx+2,y+4))
    if 42<t<78:
        x=track(t,(42,137),(53,98),(67,90),(78,137));s.beast(x,44,'mouse',-1 if t<67 else 1,.52,2)
    if 25<t<40 or 78<t<97:s.line((x,y+3),(x-1,y+7+wave(t,1)*2))

from stage import *
from crossings import footbridge, path_height

def egypt(s,t):
    s.oval(24+4*wave(t,120),8,4,4);s.poly((13,35),(40,8),(66,35));s.line((40,8),(48,35))
    s.poly((54,37),(83,13),(105,37));s.line((83,13),(90,37))
    s.box(78,31,7,6)
    gap=round(5*swell(t,40,87))
    s.box(79,32,5,4-gap if gap<5 else 0,1)
    for i in range(3):s.beast(wrap(t*185/120+17-i*26,185,23),45+i%2,'camel',1,.72,4)
    s.wind(5);s.line((2,49),(36,47),(77,49),(127,46))

def jungle_temple(s,t):
    s.ridge(29,10);s.pine(4,42,22)
    footbridge(s,12,53,43,2)
    # The visible left edge of each terrace is the next riser on the path.
    for j in range(4):
        s.box(65+j*5,40-j*4,54-j*10,3)
    s.box(86,18,13,10);s.box(89,21,6,7)
    x=track(t,(0,-9),(36,44),(56,70),(77,90),(86,90),(120,-9))
    y=path_height(x,12,53,43,2)-1
    for j in range(4):
        if x>=65+j*5:y=39-j*4
    s.person(x,y,'explorer',1 if t<86 else -1,1.6*sin(x*.9))
    for i in range(3):
        if 63+i*4<t<93:s.line((97+i*4,35),(98+i*4,33),(99+i*4,35))
    for xx in (9,27,51,111,125):
        s.line((xx,-1),(xx+1,5),(xx-2+wave(t,8),9+xx%4))


def rome(s,t):
    s.oval(107,7,4,4)
    s.box(-2,16,132,19,1)
    for x in range(4,128,16):
        s.oval(x+5,29,6,8,0,0);s.box(x-1,29,12,7,0,0)
        s.dot(x+1,19,0);s.dot(x+4,18,0)
    s.line((0,19),(127,19),c=0);s.ground(46)
    x=wrap(t*199/120,199,28)
    s.beast(x+12,44,'horse',1,.85,3);s.line((x+7,39),(x-5,39))
    s.poly((x-14,35),(x-3,36),(x-6,41),(x-13,41));s.wheel(x-9,42,4,t*tau/3)
    s.oval(x-9,28,2,2,1);s.line((x-9,31),(x-10,37),w=2);s.line((x-9,32),(x-5,34),(x-2,32))
    s.line((0,36),(127,36))
    for k in (24,92):
        s.line((k,43),(k,38));s.line((k-2,37),(k+2,37));s.line((k,36),(k+wave(t,1.5),33),w=2)
    if 36<t<85:
        xx=68+14*swell(t,36,85);s.dot(xx,30);s.line((xx,32),(xx,34),w=2);s.line((xx,34),(xx+sin(xx),36))
    s.bird(wrap(t*160/60),9,3)

def vikings(s,t):
    s.ridge(29,17);s.water(38)
    shore=87
    s.line((67,33),(81,30),(112,30),(127,28))
    for k in (0,15):s.cottage(shore+k,30,11,7)
    x=wrap(72+t*192/120,192,31);y=36+wave(t,6)
    s.poly((x-24,y-7),(x-17,y-2),(x+14,y-2),(x+21,y-9),(x+24,y-9),(x+20,y+1),(x+12,y+5),(x-12,y+5))
    s.box(x-9,y-21,18,15)
    for i in (-7,-1,5):s.box(x+i,y-20,2,13,1)
    s.line((x,y-24),(x,y-2))
    for i in (-12,-6,0,6,12):
        s.oval(x+i,y,2,2);s.line((x+i,y+2),(x+i-3+3*wave(t,4),y+7))

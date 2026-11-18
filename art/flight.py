"""Locked cameras. The four sets are drawn solely in world coordinates."""
from stage import *


def mountain(s, points, folds):
    s.line(*points)
    for fold in folds:
        s.line(*fold)


def profile(s, x, y, points, fill=1):
    pts = [(x+dx, y+dy) for dx, dy in points]
    s.line(*pts, pts[0], c=0, w=3)
    s.poly(*pts, fill=fill)


def fighter(s, x, y, far=False, bank=0):
    # Three-quarter plan view. An offset canopy separates the nose and swept wings.
    if far:
        outline = [(-10,-3),(-8,-3),(-5,-1),(-2,-1),(-5,-6),(-3,-6),
                   (3,-2),(8,-1),(11,0),(5,1),(1,2),(-5,6),(-6,6),(-4,2),(-9,2),(-7,0)]
        profile(s,x,y,outline)
        s.line((x+2,y-1),(x+5,y),c=0)
    else:
        outline = [(-15,-4),(-12,-4),(-8,-1),(-5,-2),(-10,-10+bank),(-7,-9+bank),
                   (2,-3),(7,-2),(15,0),(10,1),(3,2),(-8,10-bank),(-10,10-bank),
                   (-5,3),(-10,2),(-15,5),(-13,1),(-15,0)]
        profile(s,x,y,outline)
        s.line((x-10,y),(x-4,y),c=0)
        s.line((x+1,y-1),(x+5,y-1),(x+7,y),c=0)
        s.line((x-5,y+5-bank*.5),(x-1,y+2),c=0)


def carrier_set(s):
    # The island is on the far edge of the deck. The hull has a visible waterline.
    s.poly((-4,36),(121,36),(116,40),(103,44),(14,44),(-4,39))
    s.line((0,35),(123,35));s.line((6,38),(116,38))
    for x in (25,40,55,70,85): s.line((x,41),(x+2,41))
    s.box(8,23,14,11);s.box(6,21,18,4)
    s.line((9,23),(13,23));s.line((16,23),(20,23))
    s.box(13,17,6,3);s.line((16,17),(16,9));s.line((12,12),(20,12))
    for x,y,w in [(0,48,12),(18,46,6),(40,49,14),(76,47,8),(103,49,16),(121,45,6)]:
        s.line((x,y),(x+w,y))


def deck_jet(s,x,y,gear):
    outline=[(-15,-2),(-13,-8),(-11,-8),(-8,-3),(-4,-3),
             (0,-5),(4,-5),(7,-3),(12,-2),(16,0),(10,1),(0,1),
             (-7,4),(-9,4),(-6,1),(-13,1)]
    profile(s,x,y,outline)
    s.line((x+1,y-4),(x+4,y-3),c=0);s.line((x-11,y-1),(x-6,y-1),c=0)
    if gear:
        for dx in (-6,7):
            s.line((x+dx,y+1),(x+dx,y+4));s.line((x+dx-1,y+4),(x+dx,y+4))


def carrier(s,t):
    carrier_set(s)
    x=track(t,(0,-24),(23,42),(37,68),(49,79),(64,79),(85,98),(99,150),(120,150))
    y=track(t,(0,6),(23,8),(37,31),(85,31),(101,7),(120,7))
    deck_jet(s,x,y,25<t<94)
    # A deck marshal off the landing strip signals during the ground hold.
    xx=27+track(t,(0,0),(38,0),(48,5),(66,5),(82,0),(120,0))
    s.dot(xx,29);s.line((xx,31),(xx,34))
    arm=-2 if 44<t<69 and wave(t,4)>0 else 1
    s.line((xx,31),(xx+2,31+arm));s.dot(xx-1,34)
    # A distant second sortie occupies the sky as the first clears the deck.
    if t>86:
        fighter(s,track(t,(86,-16),(120,144)),9,True)


def armored_set(s):
    mountain(s,[(0,22),(12,17),(20,18),(32,8),(49,21),(62,16),(77,22),(89,18),(105,10),(118,19),(127,16)],
             [[(28,14),(32,10),(37,16)],[(105,12),(110,19)]])
    s.line((0,40),(127,40))
    s.poly((-2,42),(38,42),(33,46),(30,52),(-2,52),edge=0)
    s.line((0,42),(38,42),(33,47),(31,51));s.line((90,51),(87,46),(84,42),(127,42))
    s.line((37,42),(85,42));s.line((38,42),(47,47),(60,43),(72,47),(84,42))
    for x in (46,72):
        s.line((x,43),(x,49));s.line((x+2,44),(x+2,49))
    for x,y in [(1,46),(19,45),(53,50),(79,50),(105,45),(117,48)]:s.line((x,y),(x+5,y))


def tank(s,x):
    profile(s,x,36,[(-13,-1),(-10,-4),(7,-4),(13,-1),(12,1),(9,3),(-9,3),(-12,1)],0)
    s.line((x-8,36),(x+9,36))
    for dx in (-8,-4,0,4,8):s.dot(x+dx,37)
    s.line((x-9,38),(x+9,38))
    phase=round(x)%4
    for dx in range(-8+phase,9,4):s.dot(x+dx,38,0)
    profile(s,x,32,[(-7,0),(-5,-5),(2,-5),(6,-2),(5,0)],1)
    s.line((x+4,29),(x+15,28),w=2);s.dot(x-3,29,0)


def armored(s,t):
    armored_set(s)
    for offset in (0,54,108):tank(s,wrap(21+t*348/120+offset,174,23))
    if 18<t<61: fighter(s,track(t,(18,-16),(61,143)),7,True)


def patrol_set(s):
    mountain(s,[(-1,45),(12,38),(21,39),(39,24),(51,35),(62,30),(76,42),(88,31),(97,35),(111,25),(129,41)],
             [[(30,34),(39,26),(43,32),(40,31)],[(105,32),(111,27),(117,35)]])
    s.line((0,49),(14,44),(28,48),(47,40),(63,48),(78,44),(92,48),(109,38),(127,46))
    s.line((1,51),(9,49));s.line((48,43),(52,46))


def patrol_positions(t):
    # Four full circuits. The formation opens up and banks above the central peak.
    distance = 195*4*t/120 + 8*wave(t,60)
    spread = 4*wave(t,40)
    for i,offset in enumerate((0,65+spread,130+spread)):
        x = wrap(81+distance+offset,195,31)
        lift = swell(x,16,86)
        y = (15-4*lift+wave(t,60),9-2*lift+wave(t,40),18-4*lift+wave(t,30))[i]
        yield x,y,i!=0


def patrol(s,t):
    patrol_set(s)
    for x,y,far in patrol_positions(t):
        fighter(s,x,y,far,round(4*swell(x,16,86)))


def extraction_set(s):
    for xx,yy in [(3,9),(14,3),(39,8),(72,5),(88,12),(105,4),(124,9)]:s.dot(xx,yy)
    mountain(s,[(0,37),(12,29),(18,30),(31,21),(46,35),(57,28),(76,37),(91,23),(100,27),(112,17),(128,33)],
             [[(26,27),(31,23),(34,28)],[(110,22),(113,20),(117,26)]])
    s.cottage(97,43,22,10);s.line((0,45),(127,45));s.line((41,47),(78,47))
    for xx in (38,81):s.dot(xx,43)


def helicopter(s,x,y,t):
    profile(s,x,y,[(-22,-7),(-20,-7),(-18,-3),(-9,-1),(-6,-4),(3,-5),
                   (8,-4),(12,0),(11,3),(8,5),(-6,5),(-10,2),(-19,-1)],0)
    s.poly((x+3,y-3),(x+7,y-3),(x+10,y),(x+4,y),fill=1)
    s.box(x-6,y-2,6,6);s.dot(x-2,y)
    s.line((x-4,y+5),(x-3,y+8));s.line((x+6,y+5),(x+7,y+8))
    s.line((x-8,y+8),(x+10,y+8),(x+12,y+7))
    s.line((x,y-5),(x,y-8));r=6+10*abs(wave(t,1.2))
    s.line((x-r,y-8),(x+r,y-8))
    a=t*tau/1.2;s.line((x-20-3*cos(a),y-4-3*sin(a)),(x-20+3*cos(a),y-4+3*sin(a)))


def extraction(s,t):
    extraction_set(s)
    x=track(t,(0,-28),(26,34),(48,61),(80,61),(119,155))
    y=track(t,(0,12),(26,16),(48,37),(80,37),(111,12))
    for i in range(3):
        q=t-(46+6*i)
        if 0<q<17:
            xx=track(q,(0,112),(17,60))
            s.dot(xx,39);s.line((xx,41),(xx,42),w=2)
            stride=round(abs(wave(xx,5)));s.line((xx,42),(xx-stride,44));s.dot(xx+1,44)
    helicopter(s,x,y,t)

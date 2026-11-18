from stage import *

def aurora(s):
    for j in range(2):
        s.line(*[(x,8+j*3+3*wave(s.t,40,x/70)+2*wave(s.t,60,x/33)) for x in range(0,133,4)])
    for x in range(6,126,13):
        y=9+3*wave(s.t,40,x/70)+2*wave(s.t,60,x/33)
        s.line((x,y),(x+2,y-3))

def bears(s,t):
    aurora(s);s.water(44)
    def surface(x):
        return track(x,(-15,35),(35,35),(48,39),(66,39),(79,35),(130,35))
    edge=[(x,surface(x)) for x in range(-1,131,2)]
    s.poly(*edge,(129,42),(98,40),(77,41),(69,44),(47,44),(34,40),(-1,41))
    for a,b in [(1,10),(24,28),(56,64),(95,102)]:s.line((a,surface(a)+2),(b,surface(b)+2))
    x=track(t,(0,28),(32,53),(70,103),(78,103),(120,28))
    for xx,k in ((x,1),(x-24,.6)):
        s.beast(xx,surface(xx)-1,'bear',1 if t<75 else -1,k,4,stride=sin(xx*.9))
    v=swell(t,36,59)
    if v>.07:s.fish(75+8*v,48-3*v,.42)


def cabin(s,t):
    s.ridge(29,15);s.ground(44);s.pine(9,43,21);s.pine(19,43,15)
    s.box(99,18,3,10);s.cottage(78,44,31,18);s.smoke(100,18)
    s.box(96,31,9,13);s.box(97,32,7,11,0,0);s.dot(103,37)
    x=track(t,(0,-10),(30,26),(60,93),(67,102),(83,102),(90,93),(120,-10))
    if x<102:
        panel=s.im.crop((101,30,111,45))
        s.person(x,43,'cloak',1 if t<72 else -1,1.6*sin(x*.9))
        s.im.paste(panel,(101,30))
    s.wind(7+round(7*swell(t,20,88)),True)


def orcas(s,t):
    for x,w in [(-3,32),(100,33)]:
        s.poly((x,12),(x+w,12),(x+w-4,17),(x+3,15))
    s.line((27,13),(99,13));s.water(23)
    for i in range(2):
        x=wrap(t*180/120+i*57+17,180,24)
        jump=swell(x,48,82)
        y=32+i*9+4*wave(t,24,i)-jump*25
        s.poly((x-15,y),(x-9,y-2),(x-3,y-4),(x+6,y-4),(x+12,y-1),(x+13,y+1),(x+7,y+4),(x-2,y+4),(x-8,y+2))
        s.poly((x-2,y-4),(x-4,y-11),(x+3,y-4),fill=1)
        s.poly((x-10,y),(x-16,y-4),(x-15,y+3),fill=1)
        s.oval(x+6,y-1,2,1,1);s.poly((x-7,y+1),(x-2,y),(x+1,y+2),(x+9,y+2),(x+4,y+4),(x-2,y+3),fill=1)
        s.line((x+2,y+2),(x-1,y+6),(x-3,y+6))
        if jump>.45:s.line((x-10,19),(x-5,18));s.dot(x+6,20)

def station(s,t):
    aurora(s);s.ridge(30,8);s.ground(45)
    s.line((0,39),(32,39));s.line((84,40),(126,40));s.cottage(4,38,21,10);s.box(89,26,28,13);s.box(94,28,8,4,1)
    s.line((106,25),(106,16));k=wave(t,24)
    s.line((106-8*k,15),(105,19),(106+8*k,12));s.line((106,17),(108,11))
    x=track(t,(0,25),(16,25),(49,91),(69,91),(103,25),(120,25))
    s.box(x-8,37,16,5);s.box(x-4,32,8,5);s.line((x-9,44),(x+9,44),(x+12,41))
    for a in (-5,0,5):s.dot(x+a,40)
    s.wind(7,True)

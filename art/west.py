from stage import *
from crossings import locomotive, railbed, tunnel

def mesa(s,x,y,w,h):
    s.poly((x,y),(x+4,y-4),(x+w*.28,y-h),(x+w*.62,y-h),(x+w*.71,y-5),(x+w,y))
    s.line((x+w*.36,y-h+2),(x+w*.33,y-5))
def cactus(s,x,y,h):
    s.line((x,y),(x,y-h),w=2);s.line((x,y-4),(x-4,y-5),(x-4,y-10));s.line((x,y-8),(x+3,y-9),(x+3,y-12))
def rider(s,x,y):
    s.line((x-4,y-10),(x+3,y-10));s.box(x-2,y-12,3,2,1)
    s.box(x-1,y-9,2,2,1);s.line((x,y-7),(x-1,y-2),w=2)
    s.line((x,y-6),(x+2,y-4),(x+5,y-5))
    s.line((x-1,y-2),(x+3,y),(x+1,y+4),(x+3,y+4))
    s.line((x+5,y-5),(x+9,y-3))

def gunslinger(s,t):
    s.moon(86,10,6);mesa(s,5,36,52,18);mesa(s,72,33,48,10);s.cottage(101,40,18,9)
    x=track(t,(0,-25),(37,48),(64,93),(86,93),(116,154),(120,154))
    s.beast(x,44,'horse',1,.83,3,sin(x*.8));rider(s,x-2,36);s.ground(47);cactus(s,12,47,16)
    s.wheel(wrap(t*160/40),46,3,t*tau/4)

def express(s,t):
    s.moon(36,8,5);mesa(s,-5,28,52,12);mesa(s,64,27,46,14)
    s.line((1,32),(12,31),(19,32));s.line((77,30),(88,29),(96,30))
    rail=39
    railbed(s,rail,19,88)
    x=wrap(24+t*196/120,196,20)
    locomotive(s,x,rail)
    tunnel(s,109,rail)


def noon(s,t):
    s.oval(62,8,5,5)
    for x,w in [(0,24),(28,17),(86,18),(107,23)]:
        s.box(x,21,w,19);s.box(x-1,18,w+2,3);s.line((x+2,26),(x+w-2,26))
        s.box(x+4,30,5,10);s.line((x+6,31),(x+6+2*wave(t,6),39))
    gap=track(t,(0,54),(36,28),(66,22),(88,22),(120,54))
    for i in (-1,1):s.person(64+gap*i,45,'cowboy',-i,sin(gap*.8))
    if 74<t<76:s.glow(54,38,3);s.line((48,38),(52,38))
    s.wheel(wrap(t*160/60),47,3,t);s.wind(5)

def canyon(s,t):
    s.stars(16);mesa(s,-9,36,61,19);mesa(s,78,33,60,13)
    s.fire(58,43);s.smoke(58,37);s.person(45,43,'cowboy',1,0)
    s.beast(87,45,'horse',-1,.87,6,stride=0)
    if 33<t<87:s.beast(11+12*swell(t,33,87),35,'mouse',1 if t<60 else -1,.55,3)
    for k in (19,91):
        if k<t<k+3:
            x=30+12*(t-k);s.line((x,5+2*(t-k)),(x+7,7+2*(t-k)))

from stage import *

def fern(s,x,y,h):
    lean=2*wave(s.t,8,x/13);s.line((x,y),(x+lean,y-h))
    for i in range(1,5):
        v=i/6;yy=y-h*v;ww=h*(1-v)*.5
        s.line((x-ww,yy-4),(x+v*lean,yy),(x+ww,yy-3))

def giants(s,t):
    s.ridge(25,12);s.ground(45)
    for i in range(2):s.bird(wrap(72+i*36+t*160/60),8+i*5,5+i,i/3)
    s.line((0,35),(32,35),(48,34),(79,35),(127,35));s.beast(wrap(70+t*174/120,174,22),34,'sauropod',1,.72,4)
    s.beast(wrap(22+t*190/120,190,30),45,'sauropod',1,1.18,6)
    for x,h in [(1,11),(16,6),(118,10)]:fern(s,x,51,h)
    if 47<t<82:
        # A calf peeks through the foreground ferns and follows the herd.
        x=track(t,(47,-17),(57,10),(64,10),(82,-17))
        s.beast(x,49,'sauropod',1 if t<64 else -1,.58,3,stride=sin(x*.8))

def rex_hunt(s,t):
    s.ridge(33,12);s.ground(46)
    x=track(t,(0,-23),(27,23),(48,44),(58,44),(68,60),(82,148),(120,148))
    prey=track(t,(0,78),(43,69),(55,70),(66,82),(76,148),(95,148),(120,78))
    s.beast(prey,45,'mouse',-1 if t<43 or t>95 else 1,.65,2,stride=sin(prey*.9));s.beast(x,45,'rex',1,1.12,stride=sin(x*.85))
    for k,h in ((2,13),(17,6),(110,8),(126,15)):fern(s,k,50,h)
    for j in range(3):s.bird(wrap(32+t*160/120+j*12),8+wave(t,10,j)*3,3,j/4)

def volcano(s,t):
    s.poly((-5,43),(20,35),(44,14),(55,16),(65,14),(84,30),(117,44))
    s.line((44,18),(33,32),(39,29));s.line((65,18),(71,25),(70,27),(82,35))
    v=swell(t,20,108)
    for i in range(13):
        z=(t/(4+i%3)+i/13)%1
        x=54+(i-6)*3*z*v;y=16-v*(12+i%5)*4*z*(1-z)
        if v>.03:s.line((x,y),(x+1,y+1))
    if v>.35:s.line((52,17),(57,22),(55,25),(55+17*v,25+12*v))
    s.smoke(51,16,4);s.beast(wrap(45+160*(.68*t/120+.32*ease((t-53)/14))),45,'rex',1,.7,3)
    fern(s,117,51,13);s.ground(48)

def shoreline(s,t):
    s.ridge(26,10);s.water(33);s.poly((-1,34),(21,34),(31,37),(42,42),(22,45),(-1,47))
    s.beast(13,38,'sauropod',1,.79,6,stride=0)
    for i in range(2):s.bird(wrap(t*160/40+i*63),9+i*4+3*wave(t,24),6,i/3)
    for a,b,x in [(24,39,84),(73,94,103)]:
        v=swell(t,a,b)
        if v>.02:
            s.line((x-14,40),(x-9,39-v*3),(x-2,39-v*7),(x+1,40-v*15),(x+6,39-v*15),w=2)
            s.line((x-20,42),(x-12,41),(x-7,42))
    fern(s,3,49,8)

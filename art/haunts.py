from stage import *

def manor(s,t):
    s.moon(99,9,7);s.ridge(45,8);s.box(36,25,48,20)
    for x,h in [(29,23),(72,29)]:
        s.box(x,45-h,12,h);s.poly((x-2,45-h),(x+6,35-h),(x+14,45-h))
    s.poly((36,25),(50,13),(68,25));s.oval(56,40,4,6)
    for i,(x,y) in enumerate([(34,29),(44,28),(62,28),(77,24),(77,35)]):
        lit=wave(t,120,i/5)>.1;s.box(x,y,3,4,int(lit))
    s.box(44,28,17,7);s.line((46,30),(59,30))
    if 35<t<76:
        xx=47+11*swell(t,35,76);s.dot(xx,30);s.line((xx,32),(xx+1,34),w=2)
    s.line((43,36),(62,36))
    for i in range(3):s.bird(wrap(60+t*160/40+i*10),11+i*3,3,i/3)
    if any(0<t-k<.35 for k in (28,81,94)):s.line((17,0),(13,9),(17,8),(11,18))

def woods(s,t):
    s.moon(28,8,5)
    for x,h in [(4,27),(21,32),(38,21),(68,28),(85,29),(110,33),(123,25)]:s.pine(x,43,h)
    x=track(t,(0,-8),(38,39),(61,49),(83,49),(116,-8),(120,-8))
    f=1 if t<83 else -1
    s.person(x,46,'explorer',f,1.7*sin(x*.8));v=wave(t,12)
    s.line((x+5*f,40),(x+38*f,29+4*v));s.line((x+5*f,40),(x+36*f,43+3*v))
    if 48<t<85:
        yy=39-9*swell(t,48,85);s.oval(87,yy,4,6);s.dot(85,yy-1);s.dot(88,yy-1)
        s.line((84,yy-4),(81,yy-9),(79,yy-11));s.line((89,yy-4),(93,yy-10))
    s.wind(5)

def graveyard(s,t):
    s.moon(24,8);s.ridge(47,11)
    s.box(72,24,27,20);s.poly((68,24),(85,14),(104,24));s.oval(85,39,5,8)
    for i in range(6):
        x=i*23+5;y=46+i%2*3;s.line((x,y),(x,y-9),w=2);s.line((x-3,y-6),(x+3,y-6))
    v=swell(t,20,92)
    if v>.03:
        x=84-24*v;y=39-17*v;s.oval(x,y,4,5,1);s.poly((x-4,y),(x-6,y+8),(x-2,y+6),(x,y+8),(x+4,y+6),(x+4,y),fill=1)
        s.dot(x-2,y,0);s.dot(x+1,y,0)
    for i in range(3):
        x=wrap(t*160/60+i*51);s.line((x,47+i),(x+6,46+i),(x+11,47+i))
    s.bird(wrap(t*160/120+38),13+4*wave(t,24),5)

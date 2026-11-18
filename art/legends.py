from stage import *
from crossings import footbridge, path_height

def dragons_kingdom(s,t):
    s.moon(110,7,4);s.ridge(39,12)
    def dragon():
        x=66+47*wave(t,120);y=11+3*wave(t,60);f=1 if cos(tau*t/120)>0 else -1
        def p(a,b):return x+f*a,y+b
        wing=3.5*wave(t,3)
        s.poly(p(-15,2),p(-8,3),p(1,-1),p(7,-4),p(10,-3),p(12,-5),p(12,-1),p(5,1),p(0,4),p(-7,5),fill=1)
        s.poly(p(-4,1),p(-9,-5-wing),p(-3,-3-wing),p(0,-6-wing),p(3,1))
        s.line(p(-1,-2),p(-5,-4-wing*.8));s.line(p(6,-2),p(9,-7),p(9,-4))
        s.line(p(-4,3),p(-3,5),p(-1,5));s.dot(*p(9,-2),0)
    s.box(31,34,43,14)
    for x,h in [(23,18),(42,21),(70,16)]:s.tower(x,48,h,12);s.flag(x+6,48-h-2,6)
    s.oval(55,44,4,6);s.fire(35,43)
    dragon()

def wandering_knight(s,t):
    s.moon(66,8,4);s.ridge(29,8)
    for x,h in [(1,24),(12,16),(107,16),(123,28)]:s.pine(x,43,h)
    footbridge(s,28,72,43,4,stone=True);s.fire(88,41)
    x=track(t,(0,-8),(35,49),(54,77),(75,77),(109,137),(120,137))
    s.person(x,path_height(x,28,72,43,4)-1,'knight',1,2*sin(x*.8))
    xx=track(t,(0,138),(54,138),(66,99),(74,99),(91,138))
    if xx<135:s.person(xx,42,'cloak',-1 if t<74 else 1,1.6*sin(xx*.8))
    s.line((2,47),(8,47));s.line((100,47),(106,47))

def siege(s,t):
    s.ridge(35,10);s.tower(88,44,24,16);s.tower(111,44,19,14);s.box(102,31,10,13);s.flag(96,18)
    for i in range(3):
        x=wrap(t*190/120+i*19,190,20);s.person(x,49,'knight',1,1.6*sin(x*.8))
    s.wheel(17,35,3,0);s.wheel(29,35,3,0);s.line((15,33),(33,33),(24,25),(19,33));s.line((7,38),(36,38),(40,40))
    for launch in [14,50,86]:
        z=(t-launch)/5
        if 0<z<1:s.oval(29+66*z,19+6*z-63*z*(1-z),2,2,1)
        if 1<z<1.45:s.glow(96,28,3+6*(z-1))
    recoil=sum(swell(t,k-2,k+3) for k in [14,50,86])
    s.line((13,28),(24,26),(35-10*recoil,23-6*recoil),w=2)
    s.ground(49)

def sword_stone(s,t):
    s.moon(80,9);s.pine(8,45,32);s.pine(116,43,27);s.pine(125,45,31)
    s.line((0,46),(127,46));s.poly((39,44),(43,36),(50,32),(62,33),(72,40),(68,45))
    s.poly((55,35),(53,17),(55,16),(58,34),fill=1);s.line((49,18),(60,17));s.line((54,16),(53,11),w=2)
    x=track(t,(0,-8),(38,46),(74,46),(105,-8),(120,-8));s.person(x,44,'cloak',1 if t<74 else -1,sin(x*.8))
    for i in range(9):
        a=i+tau*t/24;s.dot(55+32*cos(a+i)+i,28+9*sin(a))
    strength=swell(t,49,79)
    if strength>.05:s.glow(55,22,5+strength*10,t/4)

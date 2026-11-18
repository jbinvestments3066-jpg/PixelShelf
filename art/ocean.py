from stage import *

def bubbles(s,n):
    for i in range(n):
        y=54-(i*13+s.t*60/12)%60;x=(i*29+5)%127+2*wave(s.t,6,i)
        if i%3:s.dot(x,y)
        else:s.oval(x,y,1,1)

def sub(s,x,y):
    s.oval(x,y,12,5);s.box(x-3,y-7,6,3);s.line((x-1,y-8),(x-1,y-10),(x+2,y-10))
    for k in (-5,1,7):s.oval(x+k,y,1,1,1)
    s.line((x-13,y),(x-16,y));s.line((x-16,y-2),(x-16,y+2))

def abyss(s,t):
    s.ridge(51,8);bubbles(s,7)
    v=swell(t,6,111);x=37+10*wave(t,120);y=14+23*v;sub(s,x,y)
    s.line((x+13,y),(x+38,y-5));s.line((x+13,y+1),(x+35,y+8))
    if v<.6:
        for i in range(3):s.fish(wrap(55+i*13-t*160/30),7+i*4,.45,-1)
    if v>.33:
        j=85+12*wave(t,30);s.oval(j,36,8,4);s.dot(j-5,35);s.line((j-6,33),(j-10,28),(j-13,30));s.dot(j-13,31)
        for k in range(3):s.line((j+k*3,39),(j+k*3+2*wave(t,4,k),44))

def ghost_ship(s,t):
    s.moon(19,9,5);s.water(37)
    if 46<t<72:s.sailboat(108-12*swell(t,46,72),24,.39)
    x=54+24*wave(t,120);s.sailboat(x,35+2*wave(t,6))
    yy=35+2*wave(t,6)
    s.line((x-12,yy-3),(x-12,yy-17))
    s.poly((x-13,yy-16),(x-19,yy-7),(x-16,yy-8),(x-15,yy-6),(x-13,yy-8))
    s.line((x+4,yy-15),(x+9,yy-9),c=0)
    for i in range(4):
        xx=wrap(i*41+t*160/60);yy=39+i%3*4;s.line((xx,yy),(xx+8,yy-1),(xx+17,yy))
    for strike in (32,80,98):
        if strike<t<strike+.4:s.line((29,0),(22,11),(27,10),(20,20),w=2)

def kraken(s,t):
    s.moon(23,10);s.water(37)
    x=58+25*wave(t,120);s.sailboat(x,33+wave(t,8),.82)
    for k,(base,a,b) in enumerate([(22,18,72),(103,37,96),(64,67,108)]):
        amp=swell(t,a,b)
        if amp>.015:
            pts=[(base+u*10*sin(u*5+t*tau/12+k),43-amp*u*(26-k*3)) for u in [j/12 for j in range(13)]]
            s.line(*pts,w=3);s.line(*[(x-1,y) for x,y in pts[2:]],c=0)
            s.line((base-8,44),(base-3,43));s.line((base+4,44),(base+9,44))

def atlantis(s,t):
    bubbles(s,10);s.poly((38,22),(65,10),(94,22));s.box(41,22,50,3)
    for x in (44,57,74,86):
        s.box(x,26,4,17);s.box(x-2,41,8,2);s.line((x+2,29),(x+2,39))
    s.line((96,46),(114,46));s.oval(104,31,2,3,1);s.poly((102,34),(106,34),(108,42),(100,42))
    s.line((104,36),(110,35),(111,31));s.box(99,43,10,2)
    s.box(38,44,56,2);s.line((32,47),(100,47));s.line((28,49),(103,49))
    for i in range(4):s.fish(wrap(30+i*10+t*160/40),15+i%2*5+wave(t,8,i),.46)
    x=track(t,(0,-19),(35,25),(57,50),(76,50),(103,147),(120,147))
    sub(s,x,33+5*wave(t,40))
    if 50<t<77:s.glow(67,31,3+2*wave(t,6))

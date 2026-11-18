from stage import *

def gear(s,x,y,r,phase,n):
    pts=[]
    for j in range(n*4):
        a=phase+j*tau/(n*4);rad=r-(0 if j%4 in (1,2) else 2)
        pts.append((x+rad*cos(a),y+rad*sin(a)))
    s.poly(*pts);s.wheel(x,y,r-4,phase);s.oval(x,y,2,2,1)

def clockwork(s,t):
    a=t*tau/20
    gear(s,23,19,14,a,12);gear(s,46,19,10,-a*1.5,8)
    gear(s,59,29,8,a*2,6)
    # A crank pin drives a slider constrained between two fixed guides.
    pin=(23+8*cos(a),19+8*sin(a))
    y=pin[1]+(22**2-(pin[0]-23)**2)**.5
    s.line(pin,(23,y),w=2);s.oval(*pin,2,2);s.box(18,y-1,10,3,1)
    s.line((16,32),(16,51));s.line((30,32),(30,51))
    s.line((37,48),(70,48));s.line((59,38),(59,47))
    s.oval(96,15,18,11);s.oval(96,15,7,4)
    s.oval(96+17*cos(t*tau/120),15+10*sin(t*tau/120),3,3,1)
    x=96+9*wave(t,6);s.line((96,25),(x,44));s.oval(x,45,4,4,1)


def assembly(s,t):
    s.box(-1,39,130,6)
    distance=t*160/120
    for xx in range(4,128,12):s.wheel(xx,42,2,distance/2)
    for i in range(4):
        x=wrap(distance+i*40)
        s.box(x-4,32,8,6)
        if x>=31:
            s.box(x-3,27,6,4);s.dot(x+1,29)
        if x>=65:s.line((x-4,33),(x-6,36));s.line((x+4,33),(x+6,35))
        if x>=96:s.line((x-2,35),(x,36),(x+2,33))
    for i,base in enumerate((31,65,96)):
        dx=(distance-16-base+20)%40-20
        contact=max(0,1-abs(dx)/12)
        yy=(27,32,31)[i]
        tip=(base+dx*contact,14+(yy-14)*ease(contact))
        elbow=(base-8+3*contact,9+4*contact)
        s.box(base-4,-1,8,5);s.line((base,4),elbow,tip,w=2);s.oval(*elbow,2,2)
        s.line((tip[0]-3,tip[1]+3),(tip[0]-2,tip[1]),(tip[0]+2,tip[1]),(tip[0]+3,tip[1]+3))
        if i==0 and dx<0:s.box(tip[0]-2,tip[1]+1,4,3)
        if i==2 and abs(dx)<1.8:s.line((tip[0]+5,tip[1]+1),(tip[0]+7,tip[1]-1))


def steampunk(s,t):
    for i in range(3):
        x=wrap(36+i*61-t*180/120,180,25);y=33+i%2*8
        s.poly((x-15,y),(x+17,y),(x+7,y+4),(x+2,y+10),(x-6,y+5))
        if i%2:s.tower(x-3,y-1,8,6)
    x=60+21*wave(t,120);y=18+4*wave(t,40)
    s.oval(x,y,23,9);s.oval(x,y,11,9,None);s.line((x-22,y),(x+22,y))
    s.poly((x-18,y),(x-29,y-5),(x-27,y+4))
    s.line((x-13,y+6),(x-8,y+14),(x+9,y+14),(x+15,y+6))
    s.box(x-8,y+12,17,4);s.line((x+11,y+11),(x+11,y+17))
    s.smoke(x-8,y+10,4);s.bird(wrap(11+t*160/60),6,3)

def mining(s,t):
    s.line((0,9),(12,4),(26,8),(40,4),(57,7),(70,3),(89,6),(113,2),(127,8))
    for x in (12,90,112):s.line((x,9),(x,48));s.line((x,11),(x+5,7))
    s.line((0,46),(83,46));s.box(5,24,28,4)
    dx=36+6*wave(t,24);s.line((31,26),(dx,26),w=3);s.poly((dx,22),(dx+7,26),(dx,29))
    for i in range(6):
        x=wrap(t*160/30+i*7);y=34+(x-44)*.12
        if 42<x<84:s.oval(x,y,2,1,1)
    s.line((42,37),(85,42));s.line((46,38),(46,45));s.line((82,42),(82,46));yy=track(t,(0,40),(18,40),(48,14),(70,14),(106,40),(120,40))
    s.box(92,yy-6,15,7);s.line((99,6),(99,yy-6))
    x=track(t,(0,-12),(34,38),(62,38),(99,-12),(120,-12))
    s.poly((x-7,37),(x+7,37),(x+4,43),(x-5,43));s.wheel(x-4,44,2,x/2);s.wheel(x+4,44,2,x/2)

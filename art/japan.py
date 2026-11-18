from stage import *
from crossings import footbridge, path_height

def pagoda(s,x,y,k=1):
    for i in range(3):
        w=(15-3*i)*k;yy=y-i*7*k
        s.box(x-w*.64,yy-7*k,w*1.28,7*k)
        s.poly((x-w,yy-6*k),(x-w*.64,yy-7*k),(x,yy-12*k),(x+w*.63,yy-7*k),(x+w,yy-6*k))
        s.line((x-2,yy-4*k),(x+2,yy-4*k))
    s.line((x,y-25*k),(x,y-30*k))

def petals(s):
    for i in range(7):
        x=(i*49+s.t*144/24)%144-8;y=(i*13+s.t*56/30)%56-2
        s.line((x,y),(x+1,y-1))

def samurai(s,t):
    s.ridge(30,19);pagoda(s,109,34,.62);footbridge(s,34,76,44,2)
    for x in (3,8,19,25):
        s.line((x,46),(x+3,7+x%6),w=2)
        for y in (18,26,35):s.line((x+1,y),(x+5,y-4));s.dot(x+1,y+1,0)
    x=track(t,(0,-9),(38,45),(56,71),(78,71),(113,138),(120,138))
    s.person(x,path_height(x,34,76,44,2)-1,'samurai',1,2*sin(x*.8));petals(s)

def temple_moon(s,t):
    s.moon(84,8,7);s.ridge(33,18);pagoda(s,42,44,1.15)
    for x in (74,94):
        s.line((x,45),(x,29),(x+5,29));s.oval(x+4,34,2,3,int(wave(t,12,x)>.05))
    x=track(t,(0,-8),(25,20),(43,57),(58,57),(82,84),(99,84),(120,139))
    s.line((0,46),(127,46));s.person(x,45,'cloak',1,2*sin(x*.8))
    for i in range(4):
        x=wrap(i*41+t*160/60);s.line((x,18+i*5),(x+12,18+i*5),(x+16,17+i*5))

def koi(s,t):
    # Top-down garden. Fish turn tangent to their paths and pass under the pads and bridge.
    for i,(cx,cy,rx,ry,k,direction) in enumerate(((48,28,27,13,1,1),(75,26,23,15,.78,-1),(69,34,38,8,.66,1))):
        a=direction*tau*t/120*(1+i%2)+i*2
        x=cx+rx*cos(a);y=cy+ry*sin(a)
        vx=-direction*rx*sin(a);vy=direction*ry*cos(a);length=(vx*vx+vy*vy)**.5
        ux,uy=vx/length,vy/length
        def p(f,l):return x+k*(ux*f-uy*l),y+k*(uy*f+ux*l)
        bend=1.5*wave(t,2,i/3)
        s.poly(p(-3,-1),p(-8,-2+bend),p(-7,bend),p(-8,3+bend),p(-3,1),fill=1)
        s.poly(p(-5,0),p(-1,-2),p(3,-3),p(6,-1),p(6,1),p(4,2),p(0,2),fill=1)
        s.line(p(0,-1),p(2,0),p(2,1),c=0);s.dot(*p(4,-1),0)
    for when,xx,yy in [(19,46,15),(58,78,37),(98,29,31)]:
        z=(t-when)/8
        if 0<z<1:s.oval(xx,yy,2+7*z,1+3*z,None)
    s.poly((-2,-2),(38,-2),(30,4),(17,6),(5,12),(-2,17))
    for x,y,r in [(17,14,5),(12,21,3),(108,42,5),(117,39,3)]:
        s.oval(x,y,r,r*.75,1);s.line((x,y),(x+r,y-1),c=0)
    s.poly((76,-2),(96,-2),(92,4),(85,8),(79,6))
    s.poly((118,-2),(130,-2),(130,24),(124,21),(117,16),(112,15),(113,10))
    s.poly((85,1),(118,9),(117,16),(84,8))
    for dx in range(3,33,4):
        yy=1+dx/4;s.line((85+dx,yy+1),(84+dx,yy+6))
    for i in range(3):
        xx=wrap(25+i*48+t*160/60);yy=(8+i*15+2*wave(t,12,i/3));s.line((xx,yy),(xx+1,yy-1))


def ronin(s,t):
    s.moon(65,11,8);s.ridge(29,7);s.line((0,45),(127,45))
    gap=track(t,(0,56),(28,28),(54,24),(62,8),(64,-9),(72,-15),(94,-31),(120,-56))
    for i in (-1,1):s.person(64+i*gap,44,'samurai',-i if gap>0 else i,wave(t,4)*2)
    if 61<t<64:s.line((54,38),(73,25));s.glow(64,32,3)
    for x,h in ((1,5),(4,3),(18,2),(82,3),(104,2),(121,4),(124,3)):
        s.line((x,51),(x+wave(t,6,x/17)-2,51-h))
    petals(s)

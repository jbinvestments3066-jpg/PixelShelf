"""Shared 1-bit ink, silhouettes, landscape layers and 120-second choreography."""
from math import sin, cos, pi, tau, floor
from PIL import Image, ImageDraw

def wave(t, period, phase=0):
    return sin(tau*(t/period+phase))

def ease(u):
    u=max(0,min(1,u))
    return u*u*(3-2*u)

def track(t,*keys):
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b: return x+(y-x)*ease((t-a)/(b-a))
    return keys[-1][1]

def swell(t,a,b):
    return sin(pi*(t-a)/(b-a))**2 if a<t<b else 0

def wrap(x, width=160, margin=16):
    return x%width-margin

class Stage:
    def __init__(self,t):
        self.t=t
        self.im=Image.new('1',(128,52))
        self.d=ImageDraw.Draw(self.im)

    def line(self,*points,c=1,w=1):
        self.d.line([(round(x),round(y)) for x,y in points],fill=c,width=w)
    def poly(self,*points,fill=0,edge=1):
        self.d.polygon([(round(x),round(y)) for x,y in points],fill=fill,outline=edge)
    def box(self,x,y,w,h,fill=0,edge=1):
        self.d.rectangle((round(x),round(y),round(x+w),round(y+h)),fill,edge)
    def oval(self,x,y,rx,ry,fill=0,edge=1):
        self.d.ellipse((round(x-rx),round(y-ry),round(x+rx),round(y+ry)),fill,edge)
    def dot(self,x,y,c=1):
        self.d.point((round(x),round(y)),fill=c)
    def stars(self,n=14):
        for i in range(n):
            x=(i*41+7)%128
            y=(i*17+3)%24
            self.dot(x,y)
            if i%6==0 and wave(self.t,12,i/5)>.8: self.line((x-1,y),(x+1,y))
    def moon(self,x=101,y=10,r=6):
        self.oval(x,y,r,r,1)
        self.oval(x+2,y-2,r-1,r-1,0,0)
    def ridge(self,y=30,h=13,shift=0):
        points=[(i*8-shift%128,y-h*(.49+.33*cos(i*pi/4)+.18*sin(i*pi*3/8))) for i in range(34)]
        self.poly(*points,(points[-1][0],53),(points[0][0],53),edge=0)
        self.line(*points)
        for i in range(0,len(points)-2,5):
            x,v=points[i]; self.line((x,v+1),(x+4,v+5),(x+6,v+5))
    def water(self,y=38):
        for i in range(19):
            # Periodic advection, one or two full laps per film.
            x=(i*31+self.t*144/120*(1+i%2))%144-8
            v=y+((i*7)%max(2,52-y))+wave(self.t,6,i)*1.3
            self.line((x,v),(x+2+i%6,v))
    def ground(self,y=43):
        self.line((0,y),(127,y))
        for i in range(11): self.line((i*13+1,y+3+i%3),(i*13+3,y+3+i%3))
    def wind(self,n=10,snow=False):
        for i in range(n):
            x=(i*57+self.t*144/120*(4+i%3))%144-8
            y=(i*31+self.t*56/120*(2+i%4))%56-3
            self.line((x,y),(x+(1 if snow else 3),y+1))
    def smoke(self,x,y,n=5,period=8):
        for i in range(n):
            u=(self.t/period+i/n)%1
            self.line((x+u*9+sin(u*8)*2,y-u*16),(x+u*11+2,y-u*16-1))
    def glow(self,x,y,r,phase=0):
        for i in range(8):
            a=i*pi/4+phase
            self.line((x+r*cos(a),y+r*sin(a)),(x+(r+2)*cos(a),y+(r+2)*sin(a)))
    def pine(self,x,y,h):
        self.line((x,y),(x,y-h*.23))
        def p(dx,dy):return x+dx*h,y-dy*h
        # One stepped silhouette and two side-lit boughs leave the interior dark.
        self.poly(p(0,1),p(.12,.66),p(.06,.68),p(.21,.42),p(.12,.45),
                  p(.29,.17),p(.08,.21),p(-.07,.20),p(-.29,.17),p(-.12,.45),
                  p(-.22,.42),p(-.065,.69),p(-.13,.65))
        if h>=20:
            self.line(p(-.14,.44),p(-.045,.49))
            self.line(p(.05,.29),p(.15,.25))
    def tower(self,x,y,h=15,w=10):
        self.box(x,y-h,w,h)
        for k in range(0,w,4): self.box(x+k,y-h-2,2,2,1)
        self.box(x+w//2-1,y-h+5,1,3,1)
    def cottage(self,x,y,w=15,h=11):
        self.box(x,y-h,w,h); self.poly((x-2,y-h),(x+w*.4,y-h-6),(x+w+2,y-h))
        self.box(x+2,y-h+3,3,3,1); self.box(x+w-5,y-5,3,5)
    def city(self,shift=0,y=40):
        # Silhouette skyline with roof detail and isolated lit windows.
        for i in range(-1,31):
            x=i*10-round(shift)%160
            if x < -12 or x > 127:continue
            j=i%16
            h=(11,17,10,22,14,16,9,13,21,12,8,19,14,9,17,12)[j]
            self.box(x,y-h,8,h,edge=0)
            self.line((x,y-2),(x,y-h),(x+7,y-h),(x+7,y-h+3))
            if j%4==1:self.line((x+2,y-h),(x+2,y-h-3))
            for k in range(3,h-2,6):
                if (k+j)%3:self.line((x+3,y-h+k),(x+4,y-h+k))

    def flag(self,x,y,h=10):
        self.line((x,y),(x,y-h))
        f=wave(self.t,4)
        self.poly((x,y-h),(x+8,y-h+f),(x+6,y-h+3+f),(x,y-h+3),fill=1)
    def person(self,x,y,kind='walker',face=1,step=0):
        def p(dx,dy): return (x+face*dx,y+dy)
        self.line(p(0,-11),p(0,-4),c=0,w=7)
        self.oval(*p(0,-10),2,2,1);self.dot(*p(1,-10),0)
        self.poly(p(-2,-8),p(1,-8),p(3,-3),p(-3,-3))
        self.line(p(-1,-3),p(-1-step,0)); self.line(p(1,-3),p(1+step,0))
        self.line(p(0,-7),p(3,-5),p(4,-6))
        if kind in ('knight','samurai'): self.line(p(3,-4),p(8,-10));self.line(p(2,-5),p(5,-3))
        if kind in ('cowboy','samurai','explorer'): self.line(p(-4,-11),p(4,-11))
        if kind=='astronaut': self.box(x-3,y-13,6,5);self.line(p(0,-11),p(2,-11));self.box(x-4,y-8,2,5)
        if kind=='cloak': self.poly(p(0,-12),p(5,-2),p(-4,-2));self.dot(*p(1,-9))
        if kind=='robot': self.box(x-3,y-13,6,5);self.line(p(0,-11),p(2,-11));self.box(x-3,y-7,6,5)
    def bird(self,x,y,size=4,phase=0):
        tip=size*wave(self.t,2,phase)
        self.line((x-size,y+tip),(x-2,y-1),(x,y+1),(x+2,y-1),(x+size,y+tip))
    def fish(self,x,y,s=1,face=1):
        self.oval(x,y,5*s,2.5*s,1)
        self.poly((x-face*4*s,y),(x-face*8*s,y-3*s),(x-face*8*s,y+2*s),fill=1)
        self.dot(x+face*3*s,y-1,0)
    def wheel(self,x,y,r,phase):
        self.oval(x,y,r,r)
        for i in range(3):
            a=phase+i*tau/3; self.line((x,y),(x+(r-1)*cos(a),y+(r-1)*sin(a)))
    def fire(self,x,y):
        k=wave(self.t,1.5)
        self.poly((x-4,y),(x-3,y-4),(x-1,y-3),(x+1,y-8-k*2),(x+3,y-4),(x+4,y),fill=1)
        self.line((x-5,y+2),(x+5,y+1))
    def ship(self,x,y,s=1,face=1):
        def p(a,b):return x+face*a*s,y+b*s
        self.poly(p(-11,-3),p(-3,-3),p(0,-7),p(6,-5),p(13,0),p(5,2),p(-10,2))
        self.line(p(-1,-4),p(4,-4));self.line(p(-9,-1),p(-13-2*wave(self.t,1.5),-1))
    def sailboat(self,x,y,s=1):
        def p(a,b):return x+a*s,y+b*s
        self.poly(p(-16,-3),p(16,-3),p(11,2),p(-10,2),fill=1)
        self.line(p(0,-3),p(0,-23))
        self.poly(p(-1,-21),p(-11,-6),p(-1,-6))
        self.poly(p(2,-20),p(12,-7),p(2,-7),fill=1)
    def beast(self,x,y,kind,face=1,scale=1,pace=4,stride=None):
        def p(a,b):return x+a*face*scale,y+b*scale
        def shape(*xy):self.poly(*(p(*q) for q in xy),fill=1)
        g=wave(self.t,pace) if stride is None else stride
        if kind=='rex':
            # Biped in profile: low counterweight tail, raised jaw, forearms and two hind feet.
            self.line(p(4-g*2,-7),p(6-g*2,-4),p(5-g*3,0),p(8-g*3,0))
            shape((-18,-9),(-8,-8),(-3,-11),(3,-12),(7,-10),(9,-15),(15,-15),
                  (18,-13),(17,-10),(11,-10),(9,-6),(6,-5),(3,-4),(-4,-5),(-10,-6))
            self.dot(*p(14,-13),0);self.line(p(14,-11),p(17,-11),c=0)
            self.line(p(6,-6),p(8,-4),p(10,-5))
            self.line(p(0,-6),p(-1+g*2,-3),p(1+g*3,0),p(4+g*3,0),w=2)
            return
        self.oval(x,y-5*scale,8*scale,4*scale,1)
        for i in (-5,4):
            self.line(p(i,-4),p(i+g*2,-2),p(i+g*3,1),w=2)
            self.line(p(i+2,-3),p(i+2-g*2,0))
        if kind=='sauropod':
            shape((1,-7),(6,-10),(9,-20),(13,-21),(15,-19),(12,-18),(10,-8),(6,-4))
            shape((-5,-6),(-13,-6),(-23,-10),(-18,-6),(-11,-3))
            for a in (-4,0,4):self.dot(*p(a,-6),0)
        elif kind=='camel':
            self.oval(*p(-3,-9),3*scale,4*scale,1)
            shape((3,-7),(7,-8),(10,-15),(15,-14),(15,-12),(12,-12),(9,-5))
            self.line(p(-8,-6),p(-10,-2),p(-11,-4));self.line(p(-3,-7),p(2,-7),c=0)
        elif kind=='horse':
            shape((3,-7),(7,-14),(8,-17),(10,-14),(14,-12),(13,-10),(9,-11),(7,-5))
            shape((-6,-7),(-11,-7),(-15,-2),(-12,-2),(-8,-5))
            self.line(p(-3,-7),p(-3,-4),p(2,-4),c=0)
        elif kind=='bear':
            self.oval(*p(3,-7),5*scale,4*scale,1)
            shape((4,-8),(9,-9),(11,-7),(14,-6),(13,-4),(8,-4))
            self.oval(*p(7,-9),1.6*scale,1.6*scale,1)
            self.dot(*p(10,-7),0);self.dot(*p(13,-6),0)
            self.line(p(-4,-2),p(1,-2),c=0)
        else:
            self.oval(*p(8,-6),4*scale,3*scale,1); self.oval(*p(8,-9),1.4*scale,1.4*scale,1)
            self.line(p(9,-6),p(10,-6),c=0)

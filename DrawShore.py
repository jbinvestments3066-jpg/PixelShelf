"""Rebuild the OLED shoreline film. Playback only needs the generated frames."""
from pathlib import Path
from math import sin, cos, pi
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
FPS = 10
TAU = 2*pi

# '.' is transparent, 'o' is the lit outline/plumage, '#' is dark plumage.
# A white face stripe curls behind the eye. The bib crosses the white chest.
UP = [
    "......oooo.....",
    ".....o####o....",
    "....o##ooo#o...",
    "....o#oo#o#ooo.",
    "....o#o###ooooo",
    "....o#ooooo....",
    "....o###ooo....",
    "...o####ooo....",
    "...o##oo###o...",
    "..o##o##oooo...",
    "..o#o###ooooo..",
    ".o##o##oooooo..",
    ".o#o##ooo#ooo..",
    "o#o###ooooooo..",
    ".o###ooooooo...",
    "..o##ooooooo...",
    "...oooooooo....",
]
FLAT = [
    "............oooo.....",
    "...........o##ooo....",
    "....ooooooo#oo#o#ooo.",
    "..oo########ooooooo..",
    "oo###ooooo###ooo.....",
    ".ooo######ooooo......",
    "...ooooooooooo.......",
]

def sprite(rows):
    image = Image.new("RGBA", (max(map(len, rows)), len(rows)))
    for y,row in enumerate(rows):
        for x,p in enumerate(row):
            if p != ".":
                v = 255 if p == "o" else 0
                image.putpixel((x,y), (v,v,v,255))
    return image

upright, prone = sprite(UP), sprite(FLAT)

def shore(x):
    return 29 + max(0,min(14,(x-34)*14/38))

# Time, horizontal position, action for the interval starting at that time.
beats = [(0,17,'watch'),(9,17,'walk'),(21,34,'look'),(26,34,'settle'),
         (27,35,'slide'),(30,82,'splash'),(32,82,'swim'),(45,112,'float'),
         (51,112,'swim'),(60,83,'hop'),(62,68,'walk'),(80,26,'preen'),
         (89,26,'walk'),(96,12,'look'),(101,12,'walk'),(113,38,'settle'),
         (114,38,'slide'),(117,92,'splash'),(119,92,'swim'),
         (127,110,'dive'),(135,96,'float'),(142,96,'swim'),
         (151,80,'hop'),(153,68,'walk'),(173,17,'watch'),(180,17,'watch')]

def render(t):
    image = Image.new("1",(128,52))
    d = ImageDraw.Draw(image)
    # Crescent, distant basalt stacks, a sliver of snow on the bank.
    d.ellipse((94,2,102,10),fill=1)
    d.ellipse((97,0,104,8),fill=0)
    for x,y in [(8,7),(26,3),(51,8),(73,4),(117,12)]:
        d.point((x,y),fill=1)
    d.line([(0,22),(3,20),(5,16),(7,16),(10,21)],fill=1)
    d.line([(79,29),(86,25),(90,25),(91,22),(94,21),(96,24),(101,25)],fill=1)
    d.line([(106,28),(112,26),(116,26)],fill=1)
    d.line([(0,29),(34,29),(72,43),(77,43)],fill=1)
    for a,b in [(2,9),(15,18),(29,32),(39,47),(52,55),(62,68)]:
        d.line([(a,round(shore(a))+3),(b,round(shore(b))+3)],fill=1)
    for x,y,l in [(77,44,8),(100,43,7),(118,43,7),(82,48,5),(109,47,9),(99,50,3)]:
        drift=round(2*sin(TAU*t/6+x))
        d.line((x+drift,y,x+drift+l,y),fill=1)

    k = next(i for i,b in enumerate(beats[1:]) if t<b[0])
    start,src,act=beats[k]
    end,dest,_=beats[k+1]
    dt=t-start
    u=dt/(end-start)
    smooth=u*u*(3-2*u)
    travel=u*u if act=='slide' else smooth
    x=round(src+(dest-src)*travel)
    face = 1 if dest>=src else -1
    if act in ('preen','look','float','watch'):
        face = -1 if start in (26,45,80,173) else 1
        if start==173 and dt>=4: face=1
    feet_y=round(shore(x))
    pose=upright
    angle=0
    wet=act in ('splash','swim','float','dive')
    if wet:
        pose=prone
        feet_y=45+round(sin(TAU*t/2.5))
        if act=='splash': feet_y=43+round(4*sin(pi*u))
        if act=='dive': feet_y+=round(9*sin(pi*u))
    elif act in ('slide','settle'):
        pose=prone if act=='slide' or u>.65 else upright
        angle=-18 if pose is prone else -round(42*u)
        feet_y-=1
    elif act=='hop':
        pose=prone if u<.3 else upright
        feet_y-=round(8*sin(pi*u))
    elif act=='walk':
        angle=round(7*sin((x-src)*.9))
        feet_y-=round(abs(sin((x-src)*.9)))
    elif act=='preen': angle=round(-12*(.5-.5*cos(TAU*dt/3)))
    elif act=='look': angle=round(5*sin(TAU*dt/(end-start)))
    if pose is upright:
        step=round(2*sin((x-src)*.9)) if act=='walk' else 0
        for offset,lift in [(-3, max(0,step)),(2,max(0,-step))]:
            fx=x+face*offset
            d.line((fx,feet_y-lift,fx+face*3,feet_y-lift),fill=1)
        feet_y-=1
    if angle: pose=pose.rotate(angle,expand=True,resample=Image.Resampling.NEAREST)
    if face<0: pose=pose.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    left=x-pose.width//2
    top=feet_y-pose.height+1
    if wet: pose=pose.crop((0,0,pose.width,max(0,min(pose.height,43-top))))
    if pose.height: image.paste(pose.convert('1'),(left,top),pose.getchannel('A'))
    if wet:
        radius=3+round(6*((dt%1.8)/1.8))
        d.line((x-radius,44,x-radius+2,44),fill=1)
        d.line((x+radius,44,x+radius+2,44),fill=1)
        if act=='dive' and 0.15<u<0.88:
            for n in range(3):
                f=(dt*.65+n/3)%1
                bx=x+round(3*sin(TAU*f+n))+2*n
                by=48-round(9*f)
                d.point((bx,by),fill=1)
    if act=='splash':
        for direction,speed,delay in [(-1,10,0),(1,12,0),(-1,6,.2),(1,7,.35)]:
            phase=(dt-delay)/1.35
            if 0<=phase<=1:
                px=x+direction*round(3+speed*phase)
                py=42-round(40*phase*(1-phase))
                d.line((px,py,px,py+1),fill=1)
    return image

if __name__=='__main__':
    frames=[render(i/FPS) for i in range(180*FPS)]
    (ROOT/'Shore.frames').write_bytes(b''.join(im.tobytes() for im in frames))
    frames[0].save(ROOT/'Shore.gif',save_all=True,append_images=frames[1:],
                   duration=100,loop=0,optimize=False)

from stage import *
from crossings import locomotive, railbed, tunnel
from random import Random

def soil_texture():
    rng=Random(1301)
    return [(rng.randrange(128),rng.randrange(13,52)) for i in range(92)]

SOIL=soil_texture()

def island(s,t):
    s.water(32);s.poly((9,34),(25,27),(40,27),(59,21),(72,23),(92,31),(88,36),(37,40),(17,38))
    s.cottage(39,32,14,8);s.pine(25,30,14)
    s.poly((66,26),(68,9),(73,9),(76,27));s.box(67,6,7,4);s.poly((66,6),(70,2),(76,6))
    beam=wave(t,24);s.line((70,8),(70+beam*30,5));s.line((70,9),(70+beam*30,12))
    s.line((84,34),(111,34),w=2)
    for xx in (91,108):s.line((xx,35),(xx,39))
    x=track(t,(0,107),(22,107),(48,71),(72,35),(97,79),(113,107),(120,107))
    s.poly((x-8,42),(x+9,42),(x+5,45),(x-5,45),fill=1);s.line((x,42),(x,38),(x+4,37),(x+10,34))
    s.line((x+10,34),(x+13,43));s.bird(wrap(t*160/60),13,3)

def village(s,t):
    s.ridge(23,16);s.line((0,27),(21,24),(38,28),(58,26),(74,28),(98,25))
    s.cottage(22,25,12,7);s.cottage(38,26,10,6)
    s.box(59,22,20,10);s.poly((56,22),(62,18),(76,18),(82,22))
    s.box(62,25,4,3,1);s.box(72,26,4,6)
    s.line((54,33),(87,33));s.line((54,34),(87,34))
    rail=41
    railbed(s,rail,13,48)
    x=track(t,(0,-17),(33,55),(47,80),(67,80),(112,173),(120,173))
    locomotive(s,x,rail);tunnel(s,106,rail)


def ants(s,t):
    surface=[(-2,10),(21,10),(33,4),(41,4),(55,10),(129,10)]
    s.line(*surface)
    for xx,yy in SOIL:s.dot(xx,yy)
    path=[(38,5),(31,15),(24,22),(42,26),(61,19),(79,20),(77,28),(64,36),(54,41),(76,41),(93,35),(111,40)]
    # Clear a passage inside its two edges. Chamber masks merge with the open tunnels.
    s.line(*path,w=8);s.line(*path,w=6,c=0)
    for x,y,rx,ry in [(24,22,10,5),(77,20,11,5),(54,41,13,7),(111,40,10,5)]:
        s.oval(x,y,rx,ry)
    s.line(*path,w=4,c=0)
    for xx in (48,53,58):s.oval(xx,45,1,1,1)
    lengths=[((bx-ax)**2+(by-ay)**2)**.5 for (ax,ay),(bx,by) in zip(path,path[1:])]
    total=sum(lengths)
    for i in range(6):
        phase=(t/120+i/6)%1;returning=phase>.5
        travel=(1-abs(2*phase-1))*total
        for j,length in enumerate(lengths):
            if travel<=length or j==len(lengths)-1:break
            travel-=length
        ax,ay=path[j];bx,by=path[j+1];q=travel/length
        xx=ax+(bx-ax)*q;yy=ay+(by-ay)*q+(1 if returning else -1)
        face=1 if (bx>ax)!=returning else -1
        s.line((xx-2*face,yy),(xx,yy));s.dot(xx+2*face,yy-1)
        s.dot(xx-face,yy+1)
        if i%3==0 and not returning:s.line((xx+face,yy-2),(xx+3*face,yy-4))
    # An excavator extends a small blind passage from the last chamber, then carries spoil back.
    reach=swell(t,31,106)
    end=117+round(7*reach)
    s.line((116,42),(end,40),w=5);s.line((116,42),(end,40),w=3,c=0)
    xx=116+round((end-116)*(.5+.5*wave(t,12)))
    s.line((xx-1,41),(xx+1,41));s.dot(xx+2,40)

"""Regression checks for the military camera, aircraft spacing and rail contact."""
from bake import ROOT
from stage import Stage
from crossings import locomotive, path_height, tunnel
from flight import carrier_set, armored_set, patrol_set, extraction_set, patrol_positions


def check_cameras():
    for name, scenery, first_clear_row in (
        ('carrier', carrier_set, 37), ('armored', armored_set, 41),
        ('patrol', patrol_set, 28), ('extraction', extraction_set, 46)
    ):
        reference = Stage(0)
        scenery(reference)
        fixed = reference.im.tobytes()
        packed = (ROOT/'films'/('flight_'+name+'.frames')).read_bytes()
        offset = first_clear_row*16
        for tick in range(1200):
            stage = Stage(tick/10)
            scenery(stage)
            assert stage.im.tobytes() == fixed, (name,tick,'scenery moved')
            frame = packed[tick*832:(tick+1)*832]
            assert frame[offset:] == fixed[offset:], (name,tick,'fixed terrain changed')
    smallest_gap = 128
    for tick in range(1200):
        boxes = []
        for x,y,far in patrol_positions(tick/10):
            left = round(x)-(10 if far else 15)
            right = round(x)+(11 if far else 15)
            if right >= 0 and left < 128:
                boxes.append((left,right))
        assert boxes, ('empty patrol',tick)
        boxes.sort()
        for front,following in zip(boxes,boxes[1:]):
            gap = following[0]-front[1]-1
            smallest_gap = min(smallest_gap,gap)
            assert gap >= 24, ('patrol overlap',tick,gap)
    return smallest_gap


def check_crossings():
    for left,right,bank,rise in [(28,72,43,4),(34,76,44,2),(12,53,43,2)]:
        assert path_height(left,left,right,bank,rise) == path_height(right,left,right,bank,rise) == bank
        for x in range(left-1,right+1):
            assert abs(path_height(x,left,right,bank,rise)-path_height(x+1,left,right,bank,rise)) <= 1
    for rail,mouth in [(39,109),(41,106)]:
        for x in range(17,121):
            view = Stage(0)
            locomotive(view,x,rail)
            assert all(view.im.getpixel((x+dx,rail)) for dx in (-7,0,7))
            assert not view.im.crop((0,rail+1,128,52)).getbbox()
        # Pausing alters only the steam. The complete chassis holds its contact pose.
        views = []
        for t in (48,55.5,61,66):
            view = Stage(t)
            locomotive(view,80,rail)
            views.append(view.im.crop((0,rail-16,128,52)).tobytes())
        assert len(set(views)) == 1
        empty = Stage(0)
        tunnel(empty,mouth,rail)
        box = (mouth+1,rail-15,128,rail+2)
        wall = empty.im.crop(box).tobytes()
        for x in range(mouth-10,mouth+70):
            view = Stage(0)
            locomotive(view,x,rail)
            tunnel(view,mouth,rail)
            assert view.im.crop(box).tobytes() == wall, ('tunnel intrusion',x)


if __name__ == '__main__':
    clearance = check_cameras()
    check_crossings()
    print(f'4,800 locked-camera frames checked. Minimum patrol spacing {clearance} clear columns. Rail and footbridge contact checks passed.')

"""Build films and shelf manifest. Python and Pillow are authoring tools only."""
import argparse
import importlib
from pathlib import Path
import xml.etree.ElementTree as ET
from catalog import CATEGORIES
from stage import Stage

ROOT=Path(__file__).resolve().parents[1]
def build(only=None):
    films=ROOT/'films'
    films.mkdir(exist_ok=True)
    shelf=ET.Element('shelf')
    ET.SubElement(shelf,'scene',id='penguin',category='Arctic Wilderness',title='Shoreline Penguin',
        frames='Shore.frames',fps='10',seconds='180',source='DrawShore.py',player='Penguin.ps1',stopEvent=r'Local\AbiOledPenguinStop')
    for category,module,entries in CATEGORIES:
        for title,fn in entries:
            identifier=module+'_'+fn
            filename=identifier+'.frames'
            ET.SubElement(shelf,'scene',id=identifier,category=category,title=title,frames='films/'+filename,
                fps='10',seconds='120',source='art/'+module+'.py#'+fn,player='Penguin.ps1',stopEvent='Local\\Shelf_'+identifier)
            if only and module!=only:continue
            draw=getattr(importlib.import_module(module),fn)
            tmp=(films/filename).with_suffix('.tmp')
            with tmp.open('wb') as f:
                for tick in range(1200):
                    scene=Stage(tick/10);draw(scene,scene.t);f.write(scene.im.tobytes())
            tmp.replace(films/filename)
        print(category,flush=True)
    ET.indent(shelf)
    path=ROOT/'Shelf.xml'
    tmp=path.with_suffix('.tmp')
    ET.ElementTree(shelf).write(tmp,encoding='utf-8',xml_declaration=True)
    tmp.replace(path)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--category-module')
    build(parser.parse_args().category_module)

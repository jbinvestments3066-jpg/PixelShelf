"""Produce the illustrated catalog and audit the packed deliverables after baking."""
import hashlib
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from bake import ROOT

# Representative beats for the index. The full films remain at native cadence.
POSTERS = [45,65,58,58, 68,64,52,61, 37,55,45,39, 58,57,56,69,
           52,57,62,31, 63,49,36,62, 47,52,36,47, 61,47,58,65,
           27,52,31,61, 53,71,63,40, 45,61,36,49, 58,64,67,64,62,49]

def generate():
    rows=list(ET.parse(ROOT/'Shelf.xml').getroot())
    assert len(rows)==51 and len(POSTERS)==len(rows)-1
    groups=defaultdict(list)
    atlas=Image.new('RGB',(5*260+12,10*133+12),'#252433')
    label=ImageDraw.Draw(atlas)
    digests=set(); count=0
    for i,row in enumerate(rows):
        blob=(ROOT/row.get('frames')).read_bytes()
        frames=[blob[j:j+832] for j in range(0,len(blob),832)]
        n=int(row.get('seconds'))*int(row.get('fps'))
        assert len(blob)==832*n and all(any(f) for f in frames)
        assert all(frames[:k]*(n//k)!=frames for k in range(1,n) if n%k==0)
        digest=hashlib.sha256(blob).digest()
        assert digest not in digests
        digests.add(digest);count+=n
        groups[row.get('category')].append(row)
        if not i:continue
        index=i-1;x=8+index%5*260;y=8+index//5*133
        tile=Image.frombytes('1',(128,52),frames[10*POSTERS[index]])
        colors=Image.new('RGB',tile.size,'#282e40');colors.paste('#f4e0b4',(0,0,128,52),tile)
        atlas.paste(colors.resize((256,104),Image.Resampling.NEAREST),(x,y))
        label.text((x+4,y+108),row.get('title'),fill='#f4e0b4')
    assert len(groups)==13
    atlas.save(ROOT/'Library.png',optimize=True)
    doc=['# Pixel Shelf film index','',
         'The 50 new films each run for two minutes. Shoreline Penguin runs for three minutes. The complete collection plays for 103 minutes at 10 frames per second.',
         '', '![The 50 new films, in catalog order](Library.png)','',
         '[Machine-readable manifest](Shelf.xml) · [Player and playlist controls](README.md)','']
    for group,films in groups.items():
        doc+=['## '+group,'','| Film | Drawing module and function | Playback file |','| --- | --- | --- |']
        for row in films:
            module,_,fn=row.get('source').partition('#')
            doc.append('| '+row.get('title')+' | ['+module+']('+module+') · '+(fn or 'render')+' | ['+row.get('id')+']('+row.get('frames')+') |')
        doc+=['']
    doc+=['## Authoring and tuning','',
          'The drawing modules use Pillow at 128 × 52 in one-bit mode. Each film has its own timeline. The shared stage supplies pixel shapes, actors and timing helpers. The player streams prebuilt frames using the display dimensions and cadence verified on this Arctis Nova Pro Wireless.',
          '', 'Edit a drawing function, then run `python art/bake.py --category-module ocean` from this directory to rebuild that module. Use `python art/bake.py` for the whole library and `python art/index_library.py` to refresh the index and audit the files. Register future films in `art/catalog.py` and restart the picker after a catalog change.',
          '', 'Rebuild the Windows app with the .NET Framework C# compiler, including both `PixelShelf.cs` and `Playback.cs` and references to System.Windows.Forms, System.Drawing and System.Xml.Linq. Playback itself needs Windows PowerShell and SteelSeries GG.']
    (ROOT/'Library.md').write_text('\n'.join(doc)+'\n',encoding='utf-8')
    print(f'{len(digests)} unique films, {len(groups)} categories, {count} frames verified.')

if __name__=='__main__':generate()

"""Render original documentation artwork. Optional authoring dependency: Pillow.

Run from any directory. No network access, screenshots, or third-party artwork.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BG = '#0b1220'
FG = '#eff5ff'
MUTED = '#b6c5d9'
TEAL = '#64e4c2'


def font(size, bold=False):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    candidates = [Path('C:/Windows/Fonts') / name,
                  Path('/usr/share/fonts/truetype/dejavu') /
                  ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise RuntimeError('Install Segoe UI or DejaVu Sans to render documentation.')


def shield(draw, x, y, size, color):
    points = [(x + size*.5, y), (x + size*.9, y + size*.18),
              (x + size*.83, y + size*.64), (x + size*.5, y + size),
              (x + size*.17, y + size*.64), (x + size*.1, y + size*.18),
              (x + size*.5, y)]
    draw.line(points, fill=color, width=max(3, int(size*.035)), joint='curve')
    draw.line([(x+size*.30,y+size*.47),(x+size*.45,y+size*.62),
               (x+size*.71,y+size*.34)], fill=color, width=max(3,int(size*.04)))


def hero():
    im = Image.new('RGB', (1600, 640), BG)
    d = ImageDraw.Draw(im)
    for x in range(32, 1600, 40):
        for y in range(24, 640, 40):
            d.ellipse((x,y,x+2,y+2),fill='#1b2b40')
    d.rounded_rectangle((56,50,1544,590),radius=30,fill='#101d2e',outline='#294257',width=2)
    d.text((100,88),'FLIORCIE LABS  /  OPEN SOURCE',font=font(22,True),fill=TEAL)
    d.text((100,168),'Security Agent Skills',font=font(66,True),fill=FG)
    d.text((100,270),'Review the boundary.',font=font(35),fill=FG)
    d.text((100,321),'Keep the evidence. Preserve the unknowns.',font=font(30),fill=MUTED)
    for x, number, label in [(100,'41','SKILLS'),(368,'31','AGENT PROFILES'),(710,'4','MCP TOOLS')]:
        d.text((x,418),number,font=font(48,True),fill=TEAL)
        d.text((x,483),label,font=font(18,True),fill=MUTED)
    shield(d,1190,190,220,TEAL)
    d.text((1188,470),'PUBLIC PREVIEW',font=font(20,True),fill='#ffd18a')
    im.save(HERE/'fliorcie-security-hero.png',optimize=True)


PATHS = {
    'skills': '<path d="M16 17h32v30H16z M22 25h20 M22 32h15 M22 39h11"/>',
    'agents': '<circle cx="32" cy="23" r="8"/><path d="M17 49v-6a15 15 0 0 1 30 0v6 M32 8V4 M10 29h7 M47 29h7"/>',
    'mcp': '<path d="M17 20h12v24H17 M47 20H35v24h12 M7 26h10 M7 38h10 M47 26h10 M47 38h10 M29 32h6"/>',
    'witness': '<path d="M9 32s8-14 23-14 23 14 23 14-8 14-23 14S9 32 9 32Z"/><circle cx="32" cy="32" r="7"/>',
    'bench': '<path d="M13 48V33h8v15 M28 48V23h8v25 M43 48V13h8v35 M9 52h46"/>',
    'evidence': '<path d="M17 9h23l9 9v37H17z M39 9v11h10 M24 35l6 6 12-14"/>',
    'adapter': '<path d="M10 17h17v12H10z M37 35h17v12H37z M27 23h10v18 M17 29v12h20"/>',
}


def icons():
    for name, paths in PATHS.items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
               '<rect width="64" height="64" rx="15" fill="#132638"/>'
               '<g stroke="#64e4c2" stroke-width="2.5" stroke-linecap="round" '
               'stroke-linejoin="round" fill="none">'+paths+'</g></svg>')
        (HERE/f'icon-{name}.svg').write_text(svg,encoding='utf-8')


def workflow():
    im = Image.new('RGB',(1600,520),BG)
    d = ImageDraw.Draw(im)
    d.text((65,42),'A focused review, with evidence at every step',font=font(36,True),fill=FG)
    cards = [('01','Choose','One question.','One relevant skill.'),
             ('02','Inspect','Bounded local input.','No target code execution.'),
             ('03','Review','File and line leads.','Retain skipped scope.'),
             ('04','Decide','Check the source.','Record the next action.')]
    for i,(n,title,a,b) in enumerate(cards):
        x=65+i*375
        d.rounded_rectangle((x,135,x+345,390),radius=20,fill='#101d2e',outline='#294257',width=2)
        d.text((x+24,157),n,font=font(24,True),fill=TEAL)
        d.text((x+24,211),title,font=font(32,True),fill=FG)
        d.text((x+24,281),a,font=font(21),fill=MUTED)
        d.text((x+24,319),b,font=font(21),fill=MUTED)
    d.text((65,442),'Static review leads remain PARTIAL. A passing helper does not establish project safety.',font=font(23),fill='#ffd18a')
    im.save(HERE/'security-workflow.png',optimize=True)


if __name__ == '__main__':
    hero()
    icons()
    workflow()

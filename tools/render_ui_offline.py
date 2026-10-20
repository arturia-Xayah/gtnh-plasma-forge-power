#!/usr/bin/env python3
"""Source-based UI reconstruction, NOT a Minecraft client/OpenGL screenshot.

Uses the current ForgePowerGui geometry, zh_CN strings, and vanilla 1.7.10
Unicode bitmap font. Pillow is the only dependency. No client is launched.
This intentionally does not claim to execute ModularUI's rendering pipeline.
"""
from pathlib import Path
from functools import lru_cache
import hashlib
import json
import math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'build/resources/patchedMc/assets/minecraft'
SOURCE = ROOT / 'src/main/java/dev/plasmaforgepower/ui/ForgePowerGui.java'
OUT = ROOT / 'previews'
SCALE = 3
TEXT, SUB, BLUE = '#203b50', '#536d82', '#176aab'
BG, PANEL, LINE, ACTIVE = '#e8eef4', '#f6f9fc', '#b6c8d8', '#d2eafd'
COLORS = ['#292c30', '#c5484a', '#538548', '#805432', '#3e59b2', '#8142ab',
          '#308b96', '#a6a9a4', '#555b61', '#e995af', '#83b940', '#e2cc44',
          '#6cb5db', '#ba59c4', '#e89535', '#eeeeee']
LANG = dict(line.split('=', 1) for line in
            (ROOT / 'src/main/resources/assets/plasmaforgepower/lang/zh_CN.lang')
            .read_text().splitlines() if '=' in line and not line.startswith('#'))
GLYPHS = (ASSETS / 'font/glyph_sizes.bin').read_bytes()


def tr(key):
    return LANG['pfp.' + key]


def jround(value):
    return math.floor(value + 0.5)


@lru_cache(maxsize=None)
def glyph(char):
    code = ord(char)
    bits = GLYPHS[code]
    if char == ' ':
        return None, 4, 4
    if not bits:
        raise ValueError('Vanilla font is missing U+%04X' % code)
    left, right = bits >> 4, (bits & 15) + 1
    page = Image.open(ASSETS / ('textures/font/unicode_page_%02x.png' % (code // 256))).convert('RGBA')
    x, y = (code % 16) * 16, ((code & 255) // 16) * 16
    bitmap = page.crop((x + left, y, x + right, y + 16)).getchannel('A')
    # MC measures integer widths, while renderUnicodeChar advances fractional widths.
    measured_left, measured_right = (0, 16) if right > 8 else (left, right)
    return bitmap, (right - left) / 2 + 1, (measured_right - measured_left) // 2 + 1


def text_width(text):
    return sum(glyph(c)[2] for c in text)


def wrap(text, width):
    """FontRenderer's simple word/newline wrapping for these unformatted labels."""
    result = []
    for paragraph in text.split('\n'):
        while text_width(paragraph) > width:
            count, space, w = 0, -1, 0
            for i, char in enumerate(paragraph):
                w += glyph(char)[2]
                if char == ' ':
                    space = i
                if w > width:
                    break
                count = i + 1
            count = space if space >= 0 else max(1, count)
            result.append(paragraph[:count])
            paragraph = paragraph[count + (paragraph[count:count+1] == ' '):]
        result.append(paragraph)
    return result


class Renderer:
    def __init__(self):
        self.image = Image.new('RGB', (386 * SCALE, 272 * SCALE), BG)
        self.labels = []

    def box(self, x, y, w, h, color, border=None):
        if w <= 0 or h <= 0:
            return
        d = ImageDraw.Draw(self.image)
        bounds = tuple(jround(v * SCALE) for v in (x, y, x+w, y+h))
        d.rectangle((bounds[0], bounds[1], bounds[2]-1, bounds[3]-1), fill=color,
                    outline=border, width=SCALE if border else 1)

    def text(self, text, x, y, w, h, scale=1, color=TEXT, align=0, overlay=False):
        # TextWidget adds its scale to wrapping width; IKey overlays do not.
        max_width = w if overlay else w + scale
        lines = wrap(text, max(10, int(max_width / scale)))
        line_height = 9 * scale
        # TextRenderer uses integer Java rounding followed by integer /scale coords.
        local_y = jround(h * .5) - jround((len(lines) * line_height - scale) * .5)
        for line in lines:
            local_x = max(0, jround(max_width * align) - jround(text_width(line) * scale * align))
            pen_x = x + int(local_x / scale) * scale
            pen_y = y + int(local_y / scale) * scale
            for char in line:
                bitmap, advance, _ = glyph(char)
                if bitmap is not None:
                    target_w = max(1, jround(bitmap.width / 2 * scale * SCALE))
                    target_h = max(1, jround(8 * scale * SCALE))
                    mask = bitmap.resize((target_w, target_h), Image.Resampling.NEAREST)
                    self.image.paste(color, (jround(pen_x*SCALE), jround(pen_y*SCALE)), mask)
                pen_x += advance * scale
            local_y += int(line_height)
        self.labels.append({'text': text, 'box': [x,y,w,h], 'scale': scale, 'lines': lines})

    def render(self, selected, amps, tier, supply, power, status, manual_colors, automatic=False):
        self.box(0,0,386,272,BG,LINE)
        self.box(1,1,384,35,PANEL)
        self.text(tr('forge'),14,9,330,12,1.1)
        self.text(tr('title'),14,24,330,9,.8,SUB)
        self.box(362,8,16,16,PANEL)
        self.text('×',362,8,16,16,1,SUB,.5,True)
        self.box(0,36,386,1,LINE)
        supply_voltage = 134217728  # Actual UMV hatch used by these example states.
        if supply >= 1_000_000_000:
            mantissa, exponent = ('%.2e' % supply).split('e')
            supply_label = '≈'+mantissa.rstrip('0').rstrip('.')+'×10^'+str(int(exponent))
        else:
            supply_label = format(supply,',')
        self.text(tr('supply')+'  '+supply_label+' EU/t ('+str(supply//supply_voltage)+'A UMV)',12,43,285,10,.8)
        self.text(tr('formed'),303,43,72,10,.8,BLUE)
        self.box(0,59,386,1,LINE)
        self.box(134,60,1,178,LINE)
        self.text(tr('groups'),12,70,114,10,.8,SUB)
        for position in range(16):
            c = 15-position
            x,y = 10+(position%4)*30,87+(position//4)*29
            self.box(x,y,26,26,ACTIVE if c==selected else PANEL,BLUE if c==selected else LINE)
            self.box(x+9,y+4,8,8,COLORS[c])
            self.text(tr('color.'+str(c)),x+1,y+15,24,8,.65,TEXT,.5)
            if c in manual_colors:
                self.box(x+22,y+2,2,2,BLUE)
        self.box(10,207,116,18,ACTIVE if selected==-1 else PANEL,BLUE if selected==-1 else LINE)
        self.text(tr('color.-1'),10,207,116,18,1,TEXT,.5,True)
        self.text(tr('marker'),10,229,118,8,.65,SUB)
        self.box(148,73,9,9,LINE if selected==-1 else COLORS[selected])
        self.text(tr('color.'+str(selected))+tr('input'),164,72,150,12)
        self.text(tr('auto' if automatic else 'manual'),316,74,58,9,.8,BLUE)
        self.text(tr('amps'),148,99,100,10,.8,SUB)
        self.text(tr('voltage'),267,99,104,10,.8,SUB)
        self.box(148,113,104,22,PANEL,LINE)
        self.text(amps,152,113,96,22,overlay=True)
        self.box(267,113,105,22,PANEL,LINE)
        self.text(tier+'  ▾',267,113,103,20,1,SUB if automatic else TEXT,.5)
        self.text(tr('automatic_hint'),148,141,224,10,.7,SUB)
        self.box(148,160,224,49,'#dce6ef')
        self.text(tr('preview'),156,167,112,9,.75,SUB)
        self.text('>100%' if power>supply else '%.3f%%'%(100*power/supply),288,167,76,9,.75,SUB,1)
        self.text(format(power,',')+' EU/t',156,181,208,13,1.05)
        self.box(156,201,208,3,'#c4d1dc')
        self.box(156,201,min(208,int(208*power/supply)),3,BLUE)
        self.text(tr(status),148,215,224,18,.75,'#8c4c00' if power>supply else SUB)
        self.box(0,239,386,1,LINE)
        self.text(tr('unsaved' if status=='over_budget' else 'next_recipe'),12,251,276,10,.75,SUB)
        self.box(300,246,73,20,'#246b9e')
        self.text(tr('save'),300,246,73,20,1,'#ffffff',.5,True)
        return self.image


def main():
    source = SOURCE.read_text()
    # Fail instead of silently claiming the preview follows a changed native layout.
    for anchor in ['WIDTH = 386, HEIGHT = 272', '.pos(148, 113)', '.pos(267, 113)',
                   '.pos(148, 160)', '.pos(300, 246)', '.size(73, 20)',
                   'text(editor::previewText, 156, 181, 208, 13)']:
        assert anchor in source, 'Native UI changed: review renderer geometry: '+anchor
    OUT.mkdir(exist_ok=True)
    cases = [
        ('red-manual',dict(selected=1,amps='1',tier='UEV',supply=137438953472,
                           power=8388608,status='next_recipe',manual_colors=[1,2])),
        ('unpainted-auto',dict(selected=-1,amps='-1',tier='UMV',supply=137438953472,
                              power=137438953472,status='next_recipe',manual_colors=[1,2],automatic=True)),
        ('green-over-limit',dict(selected=2,amps='8',tier='UMV',supply=536870912,
                                power=1073741824,status='over_budget',manual_colors=[1,2])),
    ]
    report = {'kind':'source-based offline reconstruction; NOT an in-game screenshot',
              'minecraft_client_launched':False,'logical_size':[386,272],'output_scale':SCALE,
              'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'font':'Minecraft 1.7.10 vanilla Unicode bitmap font, Chinese language mode',
              'limitations':['Does not run native ModularUI/OpenGL draw calls.',
                             'Uses example UI states; not a live server snapshot.',
                             'Resource packs, runtime theme/shadow, GUI scale and GPU rasterization may differ.',
                             'No hover, focused cursor, open dropdown or world backdrop is simulated.'],
              'cases':[]}
    for name, state in cases:
        renderer=Renderer()
        renderer.render(**state).save(OUT/(name+'.png'))
        report['cases'].append({'file':name+'.png','state':state,'labels':renderer.labels})
    (OUT/'offline-render.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(OUT),'images':[name+'.png' for name,_ in cases]},ensure_ascii=False))


if __name__=='__main__':
    main()

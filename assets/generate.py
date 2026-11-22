"""Generates the animated SVGs of the profile README.

Run from the repository root: python assets/generate.py
today.py then refreshes the live values (ids: age_data, commit_data,
repo_data, contrib_data) in dark_mode.svg and light_mode.svg every day.
"""
import datetime
import math
import re
from html import escape
from pathlib import Path

from dateutil import relativedelta

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
BIRTHDAY = datetime.datetime(2004, 2, 10)
CW = 8.4  # Every ASCII glyph is placed on this grid, so art aligns in any font.

THEMES = {
    'dark': dict(bg='#0d1117', panel='#161b22', line='#30363d', fg='#c9d1d9',
                 dim='#6e7681', green='#3fb950', amber='#f0883e',
                 blue='#58a6ff', red='#f85149'),
    'light': dict(bg='#ffffff', panel='#f6f8fa', line='#d0d7de', fg='#24292f',
                  dim='#6e7781', green='#1a7f37', amber='#bc4c00',
                  blue='#0969da', red='#cf222e'),
}


def css(t, extra=''):
    return f"""<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace;font-size:14px;fill:{t['fg']};white-space:pre}}
.d{{fill:{t['dim']}}}.g{{fill:{t['green']}}}.a{{fill:{t['amber']}}}.b{{fill:{t['blue']}}}.r{{fill:{t['red']}}}
.k{{fill:{t['amber']}}}.h{{font-weight:700}}
.in{{animation:in .01s steps(1) both}}
.fr{{opacity:0}}.f0{{opacity:1}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes blink{{0%,50%{{opacity:1}}51%,100%{{opacity:0}}}}
{extra}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""


def svg(w, h, t, body, title, extra=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">\n'
            f'<title>{escape(title)}</title>\n{css(t, extra)}\n'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" '
            f'fill="{t["bg"]}" stroke="{t["line"]}"/>\n{body}\n</svg>\n')


def txt(x, y, s, cls='', style=''):
    c = f' class="{cls}"' if cls else ''
    st = f' style="{style}"' if style else ''
    return f'<text x="{x:g}" y="{y:g}"{c}{st}>{escape(s, quote=False)}</text>'


def art(x, y, s, cls='', style='', cw=CW):
    """Draws a string with each glyph pinned to the monospace grid."""
    cells = [(x + i * cw, ch) for i, ch in enumerate(s) if ch != ' ']
    if not cells:
        return ''
    xs = ' '.join(f'{p:.1f}' for p, _ in cells)
    chars = ''.join(ch for _, ch in cells)
    c = f' class="{cls}"' if cls else ''
    st = f' style="{style}"' if style else ''
    return f'<text x="{xs}" y="{y:g}"{c}{st}>{escape(chars, quote=False)}</text>'


def frame_css(n):
    p = 100 / n
    return f'@keyframes fr{n}{{0%,{p - .01:.3f}%{{opacity:1}}{p:.3f}%,100%{{opacity:0}}}}'


def frames(x, y, strings, period, cls='', draw=art):
    """Loops through strings, showing one at a time."""
    n = len(strings)
    out = []
    for i, s in enumerate(strings):
        base = 'fr f0' if i == 0 else 'fr'
        full = f'{base} {cls}'.strip()
        style = f'animation:fr{n} {period}s steps(1) {i * period / n:.3f}s infinite'
        out.append(draw(x, y, s, full, style))
    return ''.join(out)


# ---------------------------------------------------------------- boot hero

BOOT = [
    ('0.000', 'reset', 'vector table @ 0x08000000', 'OK'),
    ('0.004', 'rcc', 'pll locked, sysclk 180 MHz', 'OK'),
    ('0.011', 'fmc', 'sdram up, framebuffer mapped', 'OK'),
    ('0.018', 'ltdc', 'ili9341 panel online', 'OK'),
    ('0.026', 'tim4', 'servo pwm 50 Hz', 'OK'),
    ('0.031', 'tim2', 'hc-sr04 capture, 1 us', 'OK'),
    ('0.044', 'rtos', 'scheduler started', 'OK'),
    ('0.052', 'ros2', 'robot node', 'WIP'),
    ('0.060', 'user', 'eiffis logged in', 'OK'),
]

ROBOT = [
    r'         |         ',
    r'    .----+----.    ',
    r'   /           \   ',
    None,  # eyes
    r'  |     ___     |  ',
    r'   \   \___/   /   ',
    r"    '---------'    ",
    r'   ____|===|____   ',
    r'  [____|   |____]  ',
    r'      /=====\      ',
    None,  # wheels
]


def live_values():
    """Keeps the stats already in the SVG when the art is regenerated."""
    values = {'commit_data': '0', 'repo_data': '0', 'contrib_data': '0'}
    source = ROOT / 'dark_mode.svg'
    if source.exists():
        content = source.read_text(encoding='utf-8')
        for key in values:
            found = re.search(rf'id="{key}"[^>]*>([^<]+)<', content)
            if found:
                values[key] = found.group(1)
    return values


def uptime():
    d = relativedelta.relativedelta(datetime.datetime.today(), BIRTHDAY)
    plural = lambda v: 's' if v != 1 else ''
    return (f'{d.years} year{plural(d.years)}, {d.months} month{plural(d.months)}, '
            f'{d.days} day{plural(d.days)}')


def hero(t, values):
    w, h = 985, 540
    b = [f'<path d="M1 34H{w-1}" stroke="{t["line"]}"/>']
    for i, (color, dur) in enumerate(((t['red'], 0), (t['amber'], .35), (t['green'], .22))):
        anim = f' class="blink" style="animation-duration:{dur}s"' if dur else ''
        b.append(f'<circle cx="{22 + i * 20}" cy="17" r="5" fill="{color}"{anim}/>')
    b.append(txt(92, 22, 'PWR  TX  RX', 'd'))
    b.append(txt(w - 245, 22, '/dev/ttyACM0  115200 8N1', 'd'))

    step = .17
    for i, (ts, tag, msg, status) in enumerate(BOOT):
        y = 66 + i * 24
        delay = f'animation-delay:{.25 + i * step:.2f}s'
        line = (f'<g class="in" style="{delay}">' + txt(28, y, f'[ {ts}]', 'd')
                + txt(116, y, tag, 'b') + txt(176, y, msg.ljust(32, ' '))
                + art(176 + len(msg) * CW + CW, y, '.' * (29 - len(msg)), 'd')
                + txt(436, y, f'[{status}]', 'a' if status == 'WIP' else 'g') + '</g>')
        b.append(line)

    ready = .25 + len(BOOT) * step
    rx, ry, lh = 590, 72, 20
    robot = [art(rx + 8 * CW, ry - 18, '(*)', 'r blink')]
    for i, row in enumerate(ROBOT):
        y = ry + i * lh
        if row is None and i == 3:
            robot.append(art(rx, y, '  |             |  '))
            eyes = ['     [O]   [O]'] * 7 + ['     [-]   [-]']
            eyes += ['     [o]   [o]', '    [o]   [o]',
                     '     [o]   [o]', '      [o]   [o]']
            robot.append(frames(rx, y, eyes, 4.8, 'g'))
        elif row is None:
            wheels = [f'     ({c})-----({c})     ' for c in '|/-\\']
            robot.append(frames(rx - CW, y, wheels, .8, 'b'))
        else:
            robot.append(art(rx, y, row))
    for i in range(3):
        robot.append(art(rx + (11.5 + i) * CW, ry - 18, ')', 'a blink',
                         f'animation-duration:1.5s;animation-delay:{i * .18:.2f}s'))
    b.append(f'<g class="in" style="animation-delay:{ready:.2f}s">' + ''.join(robot) + '</g>')

    message = 'hello, world'
    typed = [message[:i] for i in range(1, len(message) + 1)]
    typed += [message] * 14
    b.append(f'<g class="in" style="animation-delay:{ready + .3:.2f}s">'
             + txt(790, 122, '>', 'g')
             + frames(806, 122, typed, 5.2, '', txt) + '</g>')

    info_y = 300
    b.append(f'<g class="in" style="animation-delay:{ready + .15:.2f}s">')
    b.append(f'<path d="M24 {info_y}H{w-24}" stroke="{t["line"]}" stroke-dasharray="4 4"/>')
    left = [('user', 'eiffis'), ('role', 'Software Engineering Student'),
            ('host', 'Epitech Rennes'), ('focus', 'embedded systems & robotics'),
            ('build', 'a ROS 2 robot')]
    right = [('targets', 'STM32, ESP32'), ('firmware', 'bare-metal, drivers, RTOS'),
             ('langs', 'C, C++')]
    for i, (k, v) in enumerate(left):
        y = info_y + 34 + i * 26
        b.append(txt(28, y, k, 'k') + txt(116, y, v, 'a h' if k == 'build' else ''))
    for i, (k, v) in enumerate(right):
        y = info_y + 34 + i * 26
        b.append(txt(510, y, k, 'k') + txt(610, y, v))
    y = info_y + 34 + 3 * 26
    b.append(txt(510, y, 'uptime', 'k')
             + f'<text x="610" y="{y}" id="age_data">{uptime()}</text>')
    y += 26
    b.append(txt(510, y, 'github', 'k') + f'<text x="610" y="{y}">'
             f'<tspan class="b" id="commit_data">{values["commit_data"]}</tspan>'
             '<tspan class="d"> commits  </tspan>'
             f'<tspan class="b" id="repo_data">{values["repo_data"]}</tspan>'
             '<tspan class="d"> repos  </tspan>'
             f'<tspan class="b" id="contrib_data">{values["contrib_data"]}</tspan>'
             '<tspan class="d"> contrib</tspan></text>')
    prompt = 'eiffis@fw:~$ '
    b.append(txt(28, h - 28, prompt, 'g')
             + txt(28 + len(prompt) * CW, h - 28, './build_robots --forever')
             + f'<rect class="blink" x="{28 + (len(prompt) + 25) * CW:.1f}" y="{h - 40}" '
               f'width="8" height="15" fill="{t["green"]}"/>')
    b.append('</g>')
    extra = '\n'.join(frame_css(n) for n in sorted({12, 4, len(typed)}))
    return svg(w, h, t, '\n'.join(b), 'eiffis firmware boot log and animated ASCII robot', extra)


# -------------------------------------------------------------- Mini-Sonar

def sonar(t):
    w, h = 985, 380
    cx, cy, radius, col, row = 300, 346, 19, CW, 16
    period, half = 7.8, 39
    dt = period / (half * 2)
    extra = (frame_css(half * 2)
             + f'\n.ray{{opacity:0;animation:ray {period}s linear infinite}}'
             + '\n@keyframes ray{0%{opacity:1}3%{opacity:.5}8%{opacity:.16}13%,100%{opacity:0}}'
             + f'\n.blip{{opacity:0;animation:blip {period}s linear infinite}}'
             + '\n@keyframes blip{0%{opacity:1}24%{opacity:.75}42%{opacity:.2}48%,100%{opacity:0}}')

    def cell(angle, dist):
        a = math.radians(angle)
        return cx + dist * math.sin(a) * col * 2, cy - dist * math.cos(a) * row

    b = [txt(24, 28, 'MINI-SONAR', 'g h'), txt(116, 28, '  // STM32F429I-DISCO', 'd')]
    grid_x, grid_y, grid_c = [], [], []
    for dist in (5, 10, 15, 19):
        steps = int(dist * 4.5)
        for s in range(steps + 1):
            x, y = cell(-45 + 90 * s / steps, dist)
            grid_x.append(f'{x:.1f}'), grid_y.append(f'{y:.1f}'), grid_c.append('.')
    for angle in (-45, -22.5, 0, 22.5, 45):
        for dist in range(1, 20):
            x, y = cell(angle, dist)
            grid_x.append(f'{x:.1f}'), grid_y.append(f'{y:.1f}'), grid_c.append(':')
    b.append(f'<text x="{" ".join(grid_x)}" y="{" ".join(grid_y)}" class="d">{"".join(grid_c)}</text>')
    b.append(art(cx - CW, cy + 16, '[#]', 'g'))

    angle_of = lambda frame: -45 + 90 * (frame if frame <= half else half * 2 - frame) / half
    for frame in range(half * 2):
        angle = angle_of(frame)
        xs, ys, chars = [], [], ''
        for dist in range(1, 20):
            x, y = cell(angle, dist)
            xs.append(f'{x:.1f}'), ys.append(f'{y:.1f}')
            chars += '#' if dist > 14 else '+' if dist > 6 else '='
        cls = 'ray g f0' if frame == 0 else 'ray g'
        b.append(f'<text x="{" ".join(xs)}" y="{" ".join(ys)}" class="{cls}" '
                 f'style="animation-delay:{frame * dt:.3f}s">{chars}</text>')

    for angle, dist in ((-31, 15), (-29, 15), (-12, 9), (9, 17), (11, 17), (32, 12)):
        for frame in range(half * 2):
            if abs(angle_of(frame) - angle) <= 90 / half / 2:
                x, y = cell(angle, dist)
                b.append(f'<text x="{x:.1f}" y="{y:.1f}" class="blip r h" '
                         f'style="animation-delay:{frame * dt:.3f}s">@</text>')

    specs = [('MCU', 'STM32F429 @ 180 MHz'), ('SERVO', 'TIM4 PWM, 50 Hz'),
             ('SENSOR', 'HC-SR04, TIM2 capture'), ('RESOLUTION', '1 us'),
             ('SWEEP', '90 deg, 101 positions'), ('RANGE', '2 to 100 cm'),
             ('DISPLAY', 'LTDC + SDRAM framebuffer'), ('DRIVERS', 'bare-metal CMSIS')]
    for i, (k, v) in enumerate(specs):
        y = 80 + i * 26
        b.append(txt(610, y, k, 'k') + txt(712, y, v))
    readings = [f'{angle_of(f):+06.1f} deg' for f in range(half * 2)]
    b.append(txt(610, 310, 'ANGLE', 'k') + frames(712, 310, readings, period, 'g h', txt))
    return svg(w, h, t, '\n'.join(b), 'Animated ASCII radar of the Mini-Sonar project', extra)


# ------------------------------------------------------------------ pinout

def pinout(t):
    w, h = 985, 300
    left = ['C', 'C++', 'BARE-METAL', 'DRIVERS', 'CORTEX-M']
    right = ['RTOS', 'ROS 2', 'STM32', 'ESP32', 'LINUX']
    chip_x, chip_w, top, lh = 372, 241, 52, 42
    b = [f'<rect x="{chip_x}" y="{top - 22}" width="{chip_w}" height="{lh * 5 + 26}" rx="6" '
         f'fill="{t["panel"]}" stroke="{t["blue"]}" stroke-width="1.5"/>',
         f'<circle cx="{chip_x + 18}" cy="{top - 5}" r="4" fill="{t["dim"]}"/>']
    center = chip_x + chip_w / 2
    b.append(f'<text x="{center}" y="{top + 58}" text-anchor="middle" class="h" style="font-size:22px">EIFFIS</text>')
    b.append(f'<text x="{center}" y="{top + 86}" text-anchor="middle" class="d">embedded / robotics</text>')
    b.append(f'<text x="{center}" y="{top + 112}" text-anchor="middle" class="d">rev 2026</text>')
    b.append(f'<text x="{center}" y="{top + 150}" text-anchor="middle" class="g blink">RUNNING</text>')
    length = 19

    def trace(offset, reverse):
        cells = ['-'] * length
        for pulse in (offset, (offset + 10) % length):
            cells[pulse] = '<' if reverse else '>'
        return ''.join(cells)

    for side, labels in (('L', left), ('R', right)):
        for i, label in enumerate(labels):
            y = top + 8 + i * lh
            if side == 'L':
                b.append(f'<text x="176" y="{y}" text-anchor="end" class="h">{escape(label)}</text>')
                b.append(txt(188, y, f'P{i}', 'd'))
                x = 210
                strings = [trace(j, False) for j in range(length)]
            else:
                b.append(txt(chip_x + chip_w + 188 - 6, y, f'P{i + 5}', 'd'))
                b.append(txt(chip_x + chip_w + 214, y, label, 'h'))
                x = chip_x + chip_w + 8
                strings = [trace(length - 1 - j, True) for j in range(length)]
            shifted = strings[i * 3:] + strings[:i * 3]
            b.append(frames(x, y, shifted, 1.6, 'g'))
    return svg(w, h, t, '\n'.join(b), 'Skills drawn as the pinout of a chip',
               frame_css(length))


# ------------------------------------------------------------------ footer

def footer(t):
    w, h = 985, 120
    extra = ('.bot{animation:roll 12s linear infinite}'
             f'\n@keyframes roll{{from{{transform:translateX(-110px)}}to{{transform:translateX({w + 20}px)}}}}\n'
             + frame_css(4))
    wheels = [f'({c})---({c})' for c in '|/-\\']
    bot = ('<g class="bot">' + art(10, 44, ' .---. ') + art(10, 62, ' [o_o] ', 'g')
           + art(10, 80, " '-+-' ") + frames(6, 96, wheels, .6, 'b') + '</g>')
    rail = art(6, 110, '=' * 115, 'd')
    message = txt(24, 26, 'eiffis@fw:~$ ', 'g') + txt(24 + 13 * CW, 26, 'halt  # thanks for reading, see you on the bus', 'd')
    return svg(w, h, t, message + bot + rail, 'A small ASCII robot rolling along a rail', extra)


def main():
    values = live_values()
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ROOT / f'{name}_mode.svg').write_text(hero(t, values), encoding='utf-8')
        (ASSETS / f'sonar_{name}.svg').write_text(sonar(t), encoding='utf-8')
        (ASSETS / f'pinout_{name}.svg').write_text(pinout(t), encoding='utf-8')
        (ASSETS / f'footer_{name}.svg').write_text(footer(t), encoding='utf-8')


if __name__ == '__main__':
    main()

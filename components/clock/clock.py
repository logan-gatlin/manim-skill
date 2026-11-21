"""An analog clock with the time in digits below it, which can be turned forwards and
backwards.

Copy this file and the skill's code_font.py next to scene.py:

    from clock import Clock

    clock = Clock("09:15", date="2026-11-21", weekday=True, zone="UTC")
    self.add(clock)
    self.play(clock.to("17:40"))            # on to the next 17:40: the hands spin clockwise
    self.play(clock.back(hours=3))          # back three hours: they spin the other way
    self.play(clock.forward(days=1))        # the weekday and the date turn over too

While the time changes, the hands sweep through every hour in between, leaving a trail
behind them, and each digit turns on a wheel of its own: upwards going forwards, downwards
going backwards. See README.md.
"""

import datetime

import numpy as np
from manim import ORIGIN, PI, TAU, Animation, AnnularSector, CapStyleType, Circle, Dot, Rectangle, Text, ValueTracker, VGroup, VMobject, smooth

from code_font import MONO

PANEL = "#141821"
LINE = "#3a4252"
INK = "#eef1f6"
MUTED = "#8a93a6"
BLUE = "#60a5fa"

DAY = 1440.0    # minutes
TRAIL = 0.07    # a moving hand trails the angle it covers in this many seconds
ROLL = 0.3      # seconds a digit's wheel takes to turn to the next digit
REEL = 0.3      # a digit changing about this often a frame is a blur: its wheel turns this far a frame
WHEEL = 0.8     # the radius of a digit's wheel, in digit heights
DEPTH = 3.2     # how far away the wheels are seen from, in wheel radii: nearer bends them more
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _minutes(time):
    """Minutes since midnight for "17:40", "17:40:30", (17, 40) or (17, 40, 30)."""
    parts = [float(x) for x in time.split(":")] if isinstance(time, str) else list(time)
    h, m, s = (parts + [0, 0])[:3]
    return h * 60 + m + s / 60


def _line(a, b, color, width, opacity=1.0):
    m = VMobject().set_points_as_corners([a, b])
    return m.set_stroke(color, width, opacity).set_fill(opacity=0).set_cap_style(CapStyleType.ROUND)


def _outline(glyph):
    """A glyph's outline as closed loops of points: curves that can be cut and bent."""
    t = np.linspace(0, 1, 8, endpoint=False)[:, None]
    loops = []
    for sub in glyph.get_subpaths():
        p = sub[:, :2]
        loops.append(np.vstack([(1 - t) ** 3 * p[i] + 3 * (1 - t) ** 2 * t * p[i + 1] + 3 * (1 - t) * t ** 2 * p[i + 2]
                                + t ** 3 * p[i + 3] for i in range(0, len(p), 4)]))
    return loops


def _cut(loop, y, keep):
    """The part of a closed loop above the line at height y (keep=1) or below it (keep=-1)."""
    inside = keep * (loop[:, 1] - y) >= 0
    if inside.all():
        return loop
    if not inside.any():
        return None
    out = []
    for i in range(len(loop)):
        a, b = loop[i], loop[(i + 1) % len(loop)]
        if inside[i]:
            out.append(a)
        if inside[i] != inside[(i + 1) % len(loop)]:
            out.append(a + (y - a[1]) / (b[1] - a[1]) * (b - a))
    return np.array(out) if len(out) >= 3 else None


def _on_wheel(loops, turn, radius):
    """A character's outline as it looks on the rim of a wheel that has turned by `turn`
    radians, top going away. The character is printed so that it reads flat when it faces
    front; as the wheel turns it climbs, flattens toward the rim, and the part that has
    gone over the top is cut off. Seen from near enough that what is further is smaller."""
    rim = radius * np.cos(turn)
    out = []
    for loop in loops:
        loop = _cut(loop, rim, -1) if turn > 0 else _cut(loop, -rim, 1)
        if loop is None:
            continue
        angle = np.arcsin(np.clip(loop[:, 1] / radius, -1, 1)) + turn
        near = (DEPTH - 1) / (DEPTH - np.cos(angle))
        out.append(np.column_stack([loop[:, 0] * near, radius * np.sin(angle) * near]))
    return out


def _filled(loops, color, opacity):
    """Closed loops of points as one filled shape."""
    chunks = []
    for loop in loops:
        a = np.hstack([loop, np.zeros((len(loop), 1))])
        b = np.roll(a, -1, axis=0)
        chunks.append(np.stack([a, a + (b - a) / 3, a + 2 * (b - a) / 3, b], axis=1).reshape(-1, 3))
    m = VMobject(stroke_width=0)
    m.set_points(np.vstack(chunks))
    return m.set_fill(color, opacity)


class _Type:
    """The code font at one size: each character as a glyph and as an outline, both
    measured from the middle of the character's cell, so they can be set side by side."""

    def __init__(self, size):
        self.size, self._made = size, {}
        pair = Text("00", font=MONO, font_size=size)
        self.advance = pair[1].get_center()[0] - pair[0].get_center()[0]
        self.height = pair[0].height            # of a digit

    def get(self, ch):
        if ch not in self._made:
            pair = Text("0" + ch, font=MONO, font_size=self.size)
            glyph = pair[1].shift(-pair[0].get_center() - np.array([self.advance, 0, 0]))
            self._made[ch] = (glyph, _outline(glyph))
        return self._made[ch]


class _Jump(Animation):
    """Turns a clock to another time. Where it ends is worked out when it begins, so several
    jumps can be queued and each starts from where the last one stopped."""

    def __init__(self, clock, target_of, run_time, rate_func, zone=None):
        self.clock, self.target_of, self.zone = clock, target_of, zone
        if run_time is None:                       # longer for a longer journey, up to 3 s
            now = float(clock.minutes.get_value())
            run_time = min(3.0, 1.0 + 0.3 * np.sqrt(abs(target_of(now) - now) / 60))
        super().__init__(clock.minutes, run_time=run_time, rate_func=rate_func)

    def begin(self):
        self.start = float(self.mobject.get_value())
        self.end = self.target_of(self.start)
        self.clock._jumping = True
        if self.zone is not None:
            self.clock._zone_next = (self.zone, 1 if self.end >= self.start else -1, 0.0)
        super().begin()

    def interpolate_mobject(self, alpha):
        self.mobject.set_value(self.start + (self.end - self.start) * self.rate_func(alpha))
        if self.zone is not None and self.clock._zone_next:       # the name turns over half-way there
            turned = float(np.clip(0.5 + (alpha - 0.5) * self.run_time / (1.6 * ROLL), 0, 1))
            self.clock._zone_next = (*self.clock._zone_next[:2], turned)

    def finish(self):
        super().finish()
        self.mobject.set_value(self.end)
        self.clock._jumping = False
        if self.zone is not None:
            self.clock._zone, self.clock._zone_next = self.zone, None


class Clock(VMobject):
    """A clock face `2 * radius` wide with the time in 24-hour digits below it, centred
    where you put it. A second, smaller line can show the weekday, the date and the time
    zone.

    time      the time it starts at: "17:40", "17:40:30" or (17, 40).
    radius    the size of the face. Don't `scale` the clock: the next redraw undoes that.
    date      the date it starts on, "2026-11-21" or a datetime.date. Shown as 21 Nov, and
              it turns over at midnight.
    weekday   True shows the weekday of `date` before it. Or give the day it starts on
              ("Sat") to show a weekday with no date.
    year      True adds the year to the date.
    zone      the name of the time zone, shown after the date: "UTC", "PST", "UTC+9".
    seconds   show a second hand and seconds in the digits.
    digital   False leaves out everything below the face.
    color     the color of the second hand.
    rate      seconds of clock time that pass per second of video while nothing else is
              turning it. 0 is a stopped clock, 1 a clock that keeps real time.

    `clock.minutes` is a ValueTracker of minutes since midnight on the starting date, for
    motion of your own.
    """

    def __init__(self, time="12:00", radius=1.0, date=None, weekday=False, year=False, zone=None, seconds=False,
                 digital=True, color=BLUE, rate=0.0, **kwargs):
        super().__init__(stroke_width=0, fill_opacity=0, **kwargs)
        # One invisible point, the anchor: the renderer then re-reads the children every
        # frame, and moving the clock moves where the next drawing lands.
        self.set_points_as_corners([ORIGIN, ORIGIN])
        self.minutes = ValueTracker(_minutes(time))
        self.rate = rate
        self._r, self._accent, self._seconds, self._digital, self._year = radius, color, seconds, digital, year
        self._date = datetime.date.fromisoformat(date) if isinstance(date, str) else date
        if weekday is True and self._date is None:
            raise ValueError('weekday=True needs a date; or name the day it starts on, as in weekday="Sat"')
        self._weekday = None if not weekday else (self._date.weekday() if weekday is True
                                                  else [d.lower() for d in WEEKDAYS].index(weekday[:3].lower()))
        self._zone, self._zone_next = zone, None           # _zone_next: (name, way it turns, how far it has turned)
        self._jumping = False
        self._seen = float(self.minutes.get_value())
        self._moved, self._dt, self._speed = 0.0, 1 / 60, 0.0   # minutes last frame, its length, smoothed minutes/s
        self._phase = 0.0
        self._build()
        self._redraw(0)
        self.add_updater(lambda m, dt: m._redraw(dt))

    # ---- turning it

    def to(self, time, forward=True, days=0, run_time=None, rate_func=smooth):
        """Turn to the next `time` (or, with forward=False, back to the last one), plus
        `days` whole days. Returns the animation."""
        want = _minutes(time) % DAY

        def target(start):
            step = (want - start) % DAY if forward else -((start - want) % DAY)
            return start + step + (days if forward else -days) * DAY

        return _Jump(self, target, run_time, rate_func)

    def forward(self, hours=0, minutes=0, seconds=0, days=0, run_time=None, rate_func=smooth):
        """Turn forwards by this much. Returns the animation."""
        step = days * DAY + hours * 60 + minutes + seconds / 60
        return _Jump(self, lambda start: start + step, run_time, rate_func)

    def back(self, hours=0, minutes=0, seconds=0, days=0, run_time=None, rate_func=smooth):
        """Turn backwards by this much. Returns the animation."""
        step = days * DAY + hours * 60 + minutes + seconds / 60
        return _Jump(self, lambda start: start - step, run_time, rate_func)

    def to_zone(self, zone, hours=0, run_time=None, rate_func=smooth):
        """Change the time zone shown to `zone`, turning the clock by the `hours` that zone
        is ahead of the one it shows now (negative if it is behind). Returns the animation."""
        return _Jump(self, lambda start: start + hours * 60, run_time, rate_func, zone=zone)

    def set(self, time):
        """Show `time` at once, with no animation."""
        self.minutes.set_value(_minutes(time))
        self._seen, self._moved, self._speed = float(self.minutes.get_value()), 0.0, 0.0
        self._redraw(0)
        return self

    # ---- drawing it

    def _build(self):
        r = self._r
        self._big, self._small = _Type(30 * r), _Type(14 * r)
        self._second_line = self._date is not None or self._weekday is not None or self._zone is not None
        below = 0.0
        if self._digital:
            below += 0.3 * r + self._big.height
            if self._second_line:
                below += 0.24 * r + self._small.height
        self._height = 2 * r + below
        self._centre = np.array([0, self._height / 2 - r, 0])
        self._digits_y = self._centre[1] - r - 0.3 * r - self._big.height / 2
        self._line_y = self._digits_y - self._big.height / 2 - 0.24 * r - self._small.height / 2

        c = self._centre
        self._face = VGroup(Circle(radius=r, stroke_color=LINE, stroke_width=3 * r, fill_color=PANEL, fill_opacity=1).move_to(c))
        for k in range(12):
            d = np.array([np.sin(k * TAU / 12), np.cos(k * TAU / 12), 0])
            if k % 3 == 0:
                self._face.add(_line(c + 0.77 * r * d, c + 0.89 * r * d, INK, 3.5 * r, 0.9))
            else:
                self._face.add(_line(c + 0.83 * r * d, c + 0.89 * r * d, MUTED, 2.5 * r, 0.8))

        # the digits: how often each changes, in the smallest unit shown
        if self._seconds:
            self._steps = [None, 3600, 0, 600, 60, 0, 10, 1]
            self._bounds, self._per_day = [0, 36000, 72000, 86400], 86400
        else:
            self._steps = [None, 60, 0, 10, 1]
            self._bounds, self._per_day = [0, 600, 1200, 1440], 1440
        self._bases = [3, 10, 0, 6, 10, 0, 6, 10]
        widths = [0.62 if s == 0 else 1.0 for s in self._steps]        # the colon sits tighter than a digit
        lefts = np.cumsum([0, *widths[:-1]])
        self._xs = [(a + w / 2 - sum(widths) / 2) * self._big.advance for a, w in zip(lefts, widths)]

    def _string(self, whole):
        whole = int(whole) % self._per_day
        if self._seconds:
            return f"{whole // 3600:02d}:{whole // 60 % 60:02d}:{whole % 60:02d}"
        return f"{whole // 60:02d}:{whole % 60:02d}"

    def _day(self, day):
        """The words of the second line that depend on the day, `day` days after the start."""
        words = []
        if self._weekday is not None:
            words.append(WEEKDAYS[(self._weekday + day) % 7])
        if self._date is not None:
            d = self._date + datetime.timedelta(days=day)
            words += [f"{d.day:02d}", MONTHS[d.month - 1]] + ([str(d.year)] if self._year else [])
        return words

    def _redraw(self, dt=0):
        if dt > 0 and self.rate and not self._jumping:
            self.minutes.increment_value(self.rate * dt / 60)
        now = float(self.minutes.get_value())
        if dt > 0:
            self._moved, self._dt = now - self._seen, dt
            self._speed += (self._moved / dt - self._speed) * min(1.0, dt / 0.05)
            if self._moved:
                self._phase = (self._phase + np.sign(self._moved) * REEL) % 1
        self._seen = now
        for old in self.submobjects:
            old.set_opacity(0)
        self.submobjects = [self._draw(now).shift(self.points[0])]

    def _draw(self, now):
        r, c = self._r, self._centre
        # An invisible box over the whole clock keeps its size the same from frame to frame,
        # so it sits where it is put whatever the hands and digits are doing.
        g = VGroup(Rectangle(width=2 * r, height=self._height, stroke_width=0, fill_opacity=0), self._face.copy())
        hands = [(720, 0.5, 7, INK), (60, 0.74, 4.5, INK)]               # minutes a turn, length, width, color
        if self._seconds:
            hands.append((1, 0.8, 2, self._accent))
        lines = VGroup()
        for period, length, width, color in hands:
            angle = now / period * TAU                                    # clockwise from 12
            swept = abs(self._moved) / period * TAU                       # in the last frame
            trail = min(TAU, abs(self._speed) / period * TAU * TRAIL)
            # A hand turning most of the way round each frame can't be followed: its trail
            # evens out into a disc and the hand itself fades into it.
            blur = float(np.clip((swept - 0.8) / 1.6, 0, 1))
            if trail > 0.03:
                # The trail is the hand's own color, as if smeared: a fan of thin wedges
                # side by side, each fainter than the last. (Stacking see-through wedges
                # instead would drift in hue as their rounding errors added up.)
                side, span, n = (1 if self._speed > 0 else -1), trail + (TAU - trail) * blur, 40
                for k in range(n):
                    faint = 0.2 * (1 - (k + 0.5) / n) ** 1.5
                    faint += (0.09 - faint) * blur
                    g.add(AnnularSector(inner_radius=0, outer_radius=length * r, angle=side * span / n,
                                        start_angle=PI / 2 - angle + side * span * k / n, fill_color=color,
                                        fill_opacity=faint, stroke_width=0).shift(c))
            d = np.array([np.sin(angle), np.cos(angle), 0])
            tail = 0.14 if period == 1 else 0.0
            lines.add(_line(c - tail * r * d, c + length * r * d, color, width * r, 1 - 0.85 * blur))
        g.add(lines, Dot(c, radius=0.055 * r, color=self._accent if self._seconds else INK))
        if self._digital:
            self._write(g, now)
        return g

    def _put(self, g, type_, ch, x, y, at, opacity, color):
        """One character on its wheel, `at` quarter turns on from facing front (positive is
        up and away). The wheel carries a character every quarter turn."""
        if ch == " " or opacity < 0.01 or abs(at) > 0.97:
            return
        glyph, loops = type_.get(ch)
        if abs(at) < 1e-4:
            g.add(glyph.copy().set_color(color).set_opacity(opacity).shift([x, y, 0]))
            return
        loops = _on_wheel(loops, at * PI / 2, WHEEL * type_.height)
        if loops:                                           # darker as it turns away from the light
            g.add(_filled(loops, color, opacity * (0.12 + 0.88 * np.cos(at * PI / 2) ** 1.5)).shift([x, y, 0]))

    def _write(self, g, now):
        """The time in digits, and the line below it. Each character sits on a wheel of its
        own. One about to change turns over in the ROLL seconds before it does: it goes up
        and over the top as the next comes up from below when time runs forwards, and the
        other way when it runs backwards. A digit changing too fast to read is shown as its
        wheel spinning the same way, at a speed the eye can follow."""
        per = 60 if self._seconds else 1                                 # the smallest unit shown, per minute
        u = round(now * per, 6)
        text = self._string(np.floor(u))
        per_frame = abs(self._moved) * per
        reach = max(per_frame / self._dt * ROLL, 1e-6)                    # units covered in one roll at this speed

        def wheel(type_, x, y, color, cur, nxt, to_next, between, spin, i):
            """A character that becomes `nxt` in `to_next` units, having been `cur` for
            `between`. `spin` is what its wheel shows `j` places on when it is a blur."""
            blur = float(np.clip((per_frame / between - 0.6 * REEL) / (0.6 * REEL), 0, 1))
            if blur < 1:
                window = min(reach, between)
                e = float(np.clip(1 - to_next / window, 0, 1))
                e += (smooth(e) - e) * (1 - window / between)             # ease a lone turn; keep a steady one even
                self._put(g, type_, cur, x, y, e, 1 - blur, color)
                if e > 0:
                    self._put(g, type_, nxt, x, y, e - 1, 1 - blur, color)
            if blur > 0:
                at = (self._phase + 0.37 * i) % 1
                for j in (0, 1):
                    self._put(g, type_, spin(j), x, y, at - j, 0.75 * blur, color)

        for i, ch in enumerate(text):
            x, step = self._xs[i], self._steps[i]
            if step == 0:
                self._put(g, self._big, ":", x, self._digits_y, 0, 1, MUTED)
                continue
            if step is None:                                              # tens of hours: 0, 1, 2, then round again
                p = u % self._per_day
                k = max(j for j in range(3) if self._bounds[j] <= p)
                to_next, between = self._bounds[k + 1] - p, self._bounds[k + 1] - self._bounds[k]
            else:
                to_next, between = step - u % step, step
            wheel(self._big, x, self._digits_y, INK, ch, self._string(round(u + to_next))[i], to_next, between,
                  lambda j, ch=ch, i=i: str((int(ch) + j) % self._bases[i]), i)

        if not self._second_line:
            return
        # The second line: the words that change with the day, then the time zone.
        day = int(np.floor(u / self._per_day))
        today, tomorrow = self._day(day), self._day(day + 1)
        to_next = self._per_day - u % self._per_day
        old = self._zone or ""
        new, way, turned = self._zone_next or (old, 1, 0.0)
        turned = smooth(turned)
        gap = " · " if today and (old or new) else ""
        fixed = " ".join(today) + gap
        length = len(fixed) + len(old) + (len(new) - len(old)) * turned      # the line stays centred as the zone's
        left = -length / 2 * self._small.advance                              # name changes length
        x_of = lambda k: left + (k + 0.5) * self._small.advance
        k = 0
        for a, b in zip(today, tomorrow):
            for ch, ch2 in zip(a, b):
                if a != b and (a.isalpha() or ch != ch2):                    # a word turns over whole; a number, digit by digit
                    wheel(self._small, x_of(k), self._line_y, MUTED, ch, ch2, to_next, self._per_day,
                          lambda j, ch=ch, ch2=ch2: (ch, ch2)[j], k)
                else:
                    self._put(g, self._small, ch, x_of(k), self._line_y, 0, 1, MUTED)
                k += 1
            k += 1
        if gap:
            self._put(g, self._small, "·", x_of(len(fixed) - 2), self._line_y, 0, 1, LINE)
        for j in range(max(len(old), len(new))):
            a, b, x = old[j:j + 1] or " ", new[j:j + 1] or " ", x_of(len(fixed) + j)
            if a == b:
                self._put(g, self._small, a, x, self._line_y, 0, 1, MUTED)
            else:
                self._put(g, self._small, a, x, self._line_y, way * turned, 1, MUTED)
                self._put(g, self._small, b, x, self._line_y, way * (turned - 1), 1, MUTED)

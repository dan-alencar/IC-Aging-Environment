"""Slack statistics, trends and Arrhenius acceleration (fbs SPEC §6.2).

Window statistics come straight from the payload's sums: mean = sum/n and
std = sqrt(sumsq/n - mean^2), the spread of the sweeps inside one window.
The trend is an ordinary least-squares slope of the window means over a time span, with
its standard error, so a drift can be told from noise.
The acceleration factor is Arrhenius between the die and a use temperature:
AF = exp(Ea/k (1/T_use - 1/T_die)), default Ea = 0.7 eV, T_use = 55 degC (both configurable),
and equivalent hours are the integral of AF over stress time.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional, Tuple

K_EV = 8.617333262e-5
EA_EV = 0.7
T_USE_C = 55.0


def window_stats(n: int, s: int, sq: int) -> Tuple[Optional[float], Optional[float]]:
    """(mean, std) of one window; (None, None) without sweeps."""
    if n <= 0:
        return None, None
    mean = s / n
    var = max(0.0, sq / n - mean * mean)
    return mean, math.sqrt(var)


def acceleration_factor(die_c: float, t_use_c: float = T_USE_C, ea_ev: float = EA_EV) -> float:
    return math.exp(ea_ev / K_EV * (1.0 / (t_use_c + 273.15) - 1.0 / (die_c + 273.15)))


@dataclass
class Trend:
    """OLS slope of (t, y) over the last span_s seconds, in y units per hour."""

    span_s: float = 3600.0
    pts: Deque[Tuple[float, float]] = field(default_factory=deque)

    def add(self, t: float, y: Optional[float]) -> None:
        if y is None or (isinstance(y, float) and math.isnan(y)):
            return
        self.pts.append((t, y))
        while self.pts and t - self.pts[0][0] > self.span_s:
            self.pts.popleft()

    def slope_per_h(self) -> Tuple[Optional[float], Optional[float]]:
        """(slope, standard error) per hour; None with fewer than 3 points."""
        n = len(self.pts)
        if n < 3:
            return None, None
        t0 = self.pts[0][0]
        xs = [(t - t0) / 3600.0 for t, _ in self.pts]
        ys = [y for _, y in self.pts]
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx == 0:
            return None, None
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        resid = sum((y - my - b * (x - mx)) ** 2 for x, y in zip(xs, ys))
        se = math.sqrt(resid / (n - 2) / sxx) if n > 2 else None
        return b, se


@dataclass
class EquivalentHours:
    t_use_c: float = T_USE_C
    ea_ev: float = EA_EV
    stress_h: float = 0.0
    eq_h: float = 0.0

    def add(self, dt_s: float, die_c: Optional[float], stressed: bool) -> None:
        if not stressed or die_c is None:
            return
        self.stress_h += dt_s / 3600.0
        self.eq_h += dt_s / 3600.0 * acceleration_factor(die_c, self.t_use_c, self.ea_ev)

    @property
    def af(self) -> Optional[float]:
        return self.eq_h / self.stress_h if self.stress_h else None

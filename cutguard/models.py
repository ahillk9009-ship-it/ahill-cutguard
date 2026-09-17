from dataclasses import dataclass, field
import math


@dataclass(frozen=True)
class Config:
    black_min: float = 0.08
    freeze_min: float = 1.0
    scene_threshold: float = 0.3
    short_cut_max: float = 0.12
    cps_max: float = 15.0
    line_max: int = 22
    thumbnails: int = 24
    timeout: float = 1800.0

    def __post_init__(self):
        for key in ('black_min', 'freeze_min', 'short_cut_max', 'cps_max', 'timeout'):
            value = getattr(self, key)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{key}: finite positive number required')
        if not math.isfinite(self.scene_threshold) or not 0 < self.scene_threshold < 1:
            raise ValueError('scene_threshold: must be between 0 and 1')
        if self.line_max < 1 or not 0 <= self.thumbnails <= 200:
            raise ValueError('line_max >= 1; thumbnails between 0 and 200 required')


@dataclass
class Finding:
    code: str
    start: float
    end: float
    title: str
    detail: str
    severity: str = 'review'
    cue: str | None = None
    evidence: list = field(default_factory=list)


@dataclass
class Cue:
    number: str
    start: float
    end: float
    text: str


def timestamp(seconds):
    millis = round(max(0, seconds) * 1000)
    seconds, ms = divmod(millis, 1000)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f'{hours:02}:{minute:02}:{sec:02}.{ms:03}'

from dataclasses import dataclass
from enum import Enum


class Edges(Enum):
    top = "top"
    right = "right"
    bottom = "bottom"
    left = "left"


@dataclass
class Intersection:
    coordinates: tuple[float, float]
    edge: Edges


@dataclass
class BoundingBox:
    xmin: float
    xmax: float
    ymin: float
    ymax: float


class IntersectionException(BaseException): ...

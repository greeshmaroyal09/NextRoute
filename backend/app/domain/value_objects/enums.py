from __future__ import annotations

from enum import Enum


class StationType(str, Enum):
    MAJOR_JUNCTION = "MAJOR_JUNCTION"
    JUNCTION = "JUNCTION"
    REGULAR = "REGULAR"
    HALT = "HALT"


class TrainType(str, Enum):
    EXPRESS = "EXPRESS"
    SUPERFAST = "SUPERFAST"
    MAIL = "MAIL"
    PASSENGER = "PASSENGER"
    RAJDHANI = "RAJDHANI"
    SHATABDI = "SHATABDI"
    GARIB_RATH = "GARIB_RATH"
    LOCAL = "LOCAL"


class TravelClass(str, Enum):
    GENERAL = "GENERAL"
    SLEEPER = "SLEEPER"
    AC_3 = "AC_3"
    AC_2 = "AC_2"
    AC_1 = "AC_1"


class BusOperator(str, Enum):
    APSRTC = "APSRTC"
    TSRTC = "TSRTC"
    TNSTC = "TNSTC"
    KSRTC = "KSRTC"


class BusType(str, Enum):
    ORDINARY = "ORDINARY"
    EXPRESS = "EXPRESS"
    SUPER_LUXURY = "SUPER_LUXURY"
    SLEEPER = "SLEEPER"


class SeatStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RAC = "RAC"
    WL_1_TO_10 = "WL_1_TO_10"
    WL_11_TO_30 = "WL_11_TO_30"
    WL_30_PLUS = "WL_30_PLUS"
    UNAVAILABLE = "UNAVAILABLE"


class TransferType(str, Enum):
    STATION_TO_STATION = "STATION_TO_STATION"
    STATION_TO_BUS = "STATION_TO_BUS"
    BUS_TO_STATION = "BUS_TO_STATION"
    BUS_TO_BUS = "BUS_TO_BUS"


class TravelMode(str, Enum):
    DEFAULT = "DEFAULT"
    WOMEN = "WOMEN"
    SENIOR = "SENIOR"
    STUDENT = "STUDENT"
    FAMILY = "FAMILY"


class TransportType(str, Enum):
    TRAIN = "TRAIN"
    BUS = "BUS"
    WALK = "WALK"
    WAIT = "WAIT"


class TransferDifficulty(str, Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    DIFFICULT = "DIFFICULT"


class LightingQuality(str, Enum):
    WELL_LIT = "WELL_LIT"
    MODERATE = "MODERATE"
    POOR = "POOR"
    UNKNOWN = "UNKNOWN"


class CrowdLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class DatasetStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    APPLYING = "APPLYING"
    APPLIED = "APPLIED"
    GRAPH_BUILDING = "GRAPH_BUILDING"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ROLLED_BACK = "ROLLED_BACK"
    REJECTED = "REJECTED"

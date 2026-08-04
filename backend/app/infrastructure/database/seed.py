from __future__ import annotations

import asyncio
import math
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import engine
from app.infrastructure.database.models import (
    Base,
    BusRoute,
    BusStop,
    BusStopSequence,
    NearbyConnection,
    ScoringWeight,
    Station,
    SystemSetting,
    TrainFare,
    TrainRoute,
    TrainStop,
)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


stations_data = [
    # code, name, city, state, lat, lon, station_type, zone
    (
        "MAS",
        "Chennai Central",
        "Chennai",
        "TN",
        13.0827,
        80.2707,
        "MAJOR_JUNCTION",
        "SR",
    ),
    ("MS", "Chennai Egmore", "Chennai", "TN", 13.0732, 80.2609, "JUNCTION", "SR"),
    (
        "SBC",
        "KSR Bengaluru",
        "Bengaluru",
        "KA",
        12.9716,
        77.5946,
        "MAJOR_JUNCTION",
        "SWR",
    ),
    ("YPR", "Yesvantpur", "Bengaluru", "KA", 13.0358, 77.5500, "JUNCTION", "SWR"),
    (
        "MDU",
        "Madurai Junction",
        "Madurai",
        "TN",
        9.9195,
        78.1193,
        "MAJOR_JUNCTION",
        "SR",
    ),
    (
        "CBE",
        "Coimbatore Junction",
        "Coimbatore",
        "TN",
        11.0168,
        76.9558,
        "MAJOR_JUNCTION",
        "SR",
    ),
    ("SA", "Salem Junction", "Salem", "TN", 11.6643, 78.1460, "JUNCTION", "SR"),
    ("ED", "Erode Junction", "Erode", "TN", 11.3410, 77.7172, "JUNCTION", "SR"),
    (
        "TPJ",
        "Tiruchirappalli Junction",
        "Tiruchirappalli",
        "TN",
        10.7905,
        78.6826,
        "MAJOR_JUNCTION",
        "SR",
    ),
    (
        "TEN",
        "Tirunelveli Junction",
        "Tirunelveli",
        "TN",
        8.7254,
        77.6939,
        "JUNCTION",
        "SR",
    ),
    ("TCN", "Tuticorin", "Tuticorin", "TN", 8.7642, 78.1348, "REGULAR", "SR"),
    (
        "VM",
        "Villupuram Junction",
        "Villupuram",
        "TN",
        11.9394,
        79.4925,
        "JUNCTION",
        "SR",
    ),
    ("KPD", "Katpadi Junction", "Katpadi", "TN", 12.9672, 79.1453, "JUNCTION", "SR"),
    ("JTJ", "Jolarpettai", "Jolarpettai", "TN", 12.5680, 78.5730, "JUNCTION", "SR"),
    (
        "AJJ",
        "Arakkonam Junction",
        "Arakkonam",
        "TN",
        13.0716,
        79.6724,
        "JUNCTION",
        "SR",
    ),
    ("KRR", "Karur Junction", "Karur", "TN", 10.9601, 78.0766, "REGULAR", "SR"),
    ("DG", "Dindigul Junction", "Dindigul", "TN", 10.3624, 77.9695, "JUNCTION", "SR"),
    (
        "VPT",
        "Virudhunagar Junction",
        "Virudhunagar",
        "TN",
        9.5858,
        77.9518,
        "JUNCTION",
        "SR",
    ),
    (
        "SC",
        "Secunderabad Junction",
        "Hyderabad",
        "TS",
        17.4344,
        78.5013,
        "MAJOR_JUNCTION",
        "SCR",
    ),
    ("HYB", "Hyderabad Deccan", "Hyderabad", "TS", 17.3753, 78.4744, "JUNCTION", "SCR"),
    ("TPTY", "Tirupati", "Tirupati", "AP", 13.6288, 79.4192, "MAJOR_JUNCTION", "SCR"),
    (
        "RU",
        "Renigunta Junction",
        "Renigunta",
        "AP",
        13.6515,
        79.5156,
        "JUNCTION",
        "SCR",
    ),
    (
        "BZA",
        "Vijayawada Junction",
        "Vijayawada",
        "AP",
        16.5193,
        80.6305,
        "MAJOR_JUNCTION",
        "SCR",
    ),
    (
        "VSKP",
        "Visakhapatnam",
        "Visakhapatnam",
        "AP",
        17.7215,
        83.3025,
        "MAJOR_JUNCTION",
        "SCR",
    ),
    ("GNT", "Guntur Junction", "Guntur", "AP", 16.2987, 80.4358, "JUNCTION", "SCR"),
    ("OGL", "Ongole", "Ongole", "AP", 15.5057, 80.0499, "REGULAR", "SCR"),
    ("NLDA", "Nellore", "Nellore", "AP", 14.4426, 79.9865, "REGULAR", "SCR"),
    ("GDR", "Gudur Junction", "Gudur", "AP", 14.1467, 79.8505, "JUNCTION", "SCR"),
    (
        "GTL",
        "Guntakal Junction",
        "Guntakal",
        "AP",
        15.1711,
        77.3752,
        "MAJOR_JUNCTION",
        "SCR",
    ),
    ("ATP", "Anantapur", "Anantapur", "AP", 14.6819, 77.5006, "REGULAR", "SCR"),
    (
        "DMM",
        "Dharmavaram Junction",
        "Dharmavaram",
        "AP",
        14.4136,
        77.7111,
        "JUNCTION",
        "SCR",
    ),
    ("KRNT", "Kurnool Town", "Kurnool", "AP", 15.8281, 78.0373, "REGULAR", "SCR"),
    ("NDL", "Nandyal", "Nandyal", "AP", 15.4782, 78.4836, "REGULAR", "SCR"),
    ("GY", "Gooty Junction", "Gooty", "AP", 15.1190, 77.6277, "JUNCTION", "SCR"),
    ("WDI", "Wadi Junction", "Wadi", "KA", 17.0537, 76.9897, "JUNCTION", "SCR"),
    ("MYS", "Mysuru Junction", "Mysuru", "KA", 12.2958, 76.6394, "JUNCTION", "SWR"),
    ("UBL", "Hubballi Junction", "Hubballi", "KA", 15.3518, 75.1353, "JUNCTION", "SWR"),
    ("GR", "Gulbarga", "Kalaburagi", "KA", 17.3297, 76.8343, "REGULAR", "SWR"),
    ("HPT", "Hosapete Junction", "Hosapete", "KA", 15.2689, 76.3909, "JUNCTION", "SWR"),
    ("RCR", "Raichur", "Raichur", "KA", 16.2120, 77.3439, "REGULAR", "SWR"),
    ("SKLR", "Shimoga Town", "Shimoga", "KA", 13.9299, 75.5681, "REGULAR", "SWR"),
    ("HAS", "Hassan", "Hassan", "KA", 12.9577, 76.0996, "REGULAR", "SWR"),
    ("ASK", "Arsikere Junction", "Arsikere", "KA", 13.3100, 76.2500, "JUNCTION", "SWR"),
    ("TK", "Tumkur", "Tumkur", "KA", 13.3379, 77.1173, "REGULAR", "SWR"),
    ("MAQ", "Mangaluru Central", "Mangaluru", "KA", 12.8661, 74.8426, "JUNCTION", "SR"),
    (
        "ERS",
        "Ernakulam Junction",
        "Kochi",
        "KL",
        9.9816,
        76.2999,
        "MAJOR_JUNCTION",
        "SR",
    ),
    (
        "TVC",
        "Thiruvananthapuram Central",
        "Thiruvananthapuram",
        "KL",
        8.4855,
        76.9492,
        "MAJOR_JUNCTION",
        "SR",
    ),
    ("CLT", "Kozhikode", "Kozhikode", "KL", 11.2588, 75.7804, "JUNCTION", "SR"),
    ("WL", "Warangal", "Warangal", "TS", 17.9689, 79.5941, "JUNCTION", "SCR"),
    ("NZB", "Nizamabad", "Nizamabad", "TS", 18.6725, 78.0940, "REGULAR", "SCR"),
]

train_routes_data = [
    (
        "12637",
        "Pandian Express",
        "EXPRESS",
        "daily",
        [
            ("MAS", "21:30", "21:30", 0),
            ("VM", "23:15", "23:20", 0),
            ("TPJ", "01:40", "01:45", 1),
            ("DG", "03:50", "03:55", 1),
            ("MDU", "05:15", "05:15", 1),
        ],
    ),
    (
        "12657",
        "Chennai Mail",
        "SUPERFAST",
        "daily",
        [
            ("SBC", "23:00", "23:00", 0),
            ("KPD", "01:30", "01:35", 1),
            ("AJJ", "03:00", "03:05", 1),
            ("MAS", "04:30", "04:30", 1),
        ],
    ),
    (
        "12609",
        "Chennai Express",
        "EXPRESS",
        "daily",
        [
            ("SBC", "06:00", "06:00", 0),
            ("JTJ", "08:00", "08:05", 0),
            ("KPD", "09:00", "09:05", 0),
            ("AJJ", "10:15", "10:20", 0),
            ("MAS", "11:30", "11:30", 0),
        ],
    ),
    (
        "16525",
        "Island Express",
        "EXPRESS",
        "daily",
        [
            ("SBC", "15:15", "15:15", 0),
            ("SA", "19:00", "19:05", 0),
            ("ED", "19:45", "19:50", 0),
            ("CBE", "21:15", "21:20", 0),
            ("ERS", "02:15", "02:20", 1),
            ("TVC", "06:15", "06:15", 1),
        ],
    ),
    (
        "17603",
        "Kacheguda Express",
        "EXPRESS",
        "daily",
        [
            ("SC", "18:30", "18:30", 0),
            ("GTL", "01:30", "01:35", 1),
            ("DMM", "03:00", "03:05", 1),
            ("SBC", "06:30", "06:30", 1),
        ],
    ),
    (
        "12785",
        "Bangalore Express",
        "SUPERFAST",
        "daily",
        [
            ("SC", "22:30", "22:30", 0),
            ("GY", "03:00", "03:05", 1),
            ("GTL", "04:00", "04:05", 1),
            ("SBC", "07:00", "07:00", 1),
        ],
    ),
    (
        "12615",
        "Grand Trunk Express",
        "SUPERFAST",
        "daily",
        [
            ("MAS", "19:20", "19:20", 0),
            ("AJJ", "20:45", "20:50", 0),
            ("RU", "22:45", "22:50", 0),
            ("GDR", "23:30", "23:35", 0),
            ("OGL", "01:30", "01:35", 1),
            ("BZA", "04:30", "04:40", 1),
            ("SC", "11:00", "11:00", 1),
        ],
    ),
    (
        "12627",
        "Karnataka Express",
        "SUPERFAST",
        "daily",
        [
            ("MAS", "06:00", "06:00", 0),
            ("AJJ", "07:15", "07:20", 0),
            ("KPD", "08:45", "08:50", 0),
            ("JTJ", "10:00", "10:05", 0),
            ("SBC", "12:00", "12:00", 0),
        ],
    ),
    (
        "16353",
        "Nagercoil Express",
        "EXPRESS",
        "daily",
        [
            ("MAS", "17:00", "17:00", 0),
            ("VM", "19:30", "19:35", 0),
            ("TPJ", "22:00", "22:05", 0),
            ("DG", "00:30", "00:35", 1),
            ("MDU", "01:45", "01:50", 1),
            ("VPT", "03:00", "03:05", 1),
            ("TEN", "05:15", "05:15", 1),
        ],
    ),
    (
        "11013",
        "Coimbatore Express",
        "EXPRESS",
        "daily",
        [
            ("MAS", "22:20", "22:20", 0),
            ("AJJ", "23:45", "23:50", 0),
            ("SA", "02:30", "02:35", 1),
            ("ED", "03:15", "03:20", 1),
            ("CBE", "05:00", "05:00", 1),
        ],
    ),
    (
        "16339",
        "Nagarcoil Express",
        "EXPRESS",
        "daily",
        [
            ("MAS", "21:00", "21:00", 0),
            ("VM", "23:00", "23:05", 0),
            ("TPJ", "01:30", "01:35", 1),
            ("CBE", "06:00", "06:05", 1),
            ("ERS", "09:30", "09:30", 1),
        ],
    ),
    (
        "12629",
        "Yercaud Express",
        "EXPRESS",
        "daily",
        [
            ("MAS", "23:00", "23:00", 0),
            ("KPD", "01:00", "01:05", 1),
            ("JTJ", "02:30", "02:35", 1),
            ("SA", "04:00", "04:00", 1),
        ],
    ),
    (
        "17229",
        "Sabari Express",
        "EXPRESS",
        "1010100",
        [
            ("SC", "07:30", "07:30", 0),
            ("GTL", "14:00", "14:10", 0),
            ("SBC", "21:00", "21:15", 0),
            ("ERS", "06:00", "06:05", 1),
            ("TVC", "10:30", "10:30", 1),
        ],
    ),
    (
        "12863",
        "Howrah Express",
        "SUPERFAST",
        "daily",
        [
            ("MAS", "22:50", "22:50", 0),
            ("GDR", "02:00", "02:05", 1),
            ("OGL", "04:30", "04:35", 1),
            ("BZA", "07:00", "07:10", 1),
            ("VSKP", "13:30", "13:30", 1),
        ],
    ),
    (
        "56213",
        "Passenger",
        "PASSENGER",
        "daily",
        [
            ("MDU", "06:00", "06:00", 0),
            ("DG", "07:15", "07:20", 0),
            ("KRR", "08:30", "08:35", 0),
            ("TPJ", "10:00", "10:00", 0),
        ],
    ),
]

bus_stops_data = [
    ("MAS-CMBT", "CMBT Bus Stand", "Chennai", "TN", 13.0694, 80.2046, "TNSTC"),
    ("SBC-MJSTC", "Majestic Bus Station", "Bengaluru", "KA", 12.9770, 77.5730, "KSRTC"),
    ("MDU-BS", "Madurai Mattuthavani", "Madurai", "TN", 9.9000, 78.1300, "TNSTC"),
    ("CBE-BS", "Coimbatore Gandhipuram", "Coimbatore", "TN", 11.0186, 76.9676, "TNSTC"),
    (
        "TPJ-BS",
        "Trichy Central Bus Stand",
        "Tiruchirappalli",
        "TN",
        10.8005,
        78.6895,
        "TNSTC",
    ),
    ("SA-BS", "Salem Bus Stand", "Salem", "TN", 11.6565, 78.1568, "TNSTC"),
    ("SC-MGBS", "MGBS Hyderabad", "Hyderabad", "TS", 17.3784, 78.4867, "TSRTC"),
    ("SC-JBS", "JBS Secunderabad", "Hyderabad", "TS", 17.4525, 78.5005, "TSRTC"),
    ("BZA-BS", "Vijayawada Bus Stand", "Vijayawada", "AP", 16.5150, 80.6200, "APSRTC"),
    (
        "VSKP-BS",
        "Visakhapatnam Bus Complex",
        "Visakhapatnam",
        "AP",
        17.7100,
        83.3000,
        "APSRTC",
    ),
    ("TPTY-BS", "Tirupati Bus Stand", "Tirupati", "AP", 13.6350, 79.4200, "APSRTC"),
    ("ATP-BS", "Anantapur Bus Stand", "Anantapur", "AP", 14.6850, 77.5050, "APSRTC"),
    ("GTL-BS", "Guntakal Bus Stand", "Guntakal", "AP", 15.1750, 77.3800, "APSRTC"),
    ("MYS-BS", "Mysuru Bus Stand", "Mysuru", "KA", 12.2960, 76.6450, "KSRTC"),
    ("UBL-BS", "Hubballi Bus Stand", "Hubballi", "KA", 15.3550, 75.1400, "KSRTC"),
    ("MAQ-BS", "Mangaluru Bus Stand", "Mangaluru", "KA", 12.8700, 74.8450, "KSRTC"),
    (
        "TVC-BS",
        "Trivandrum KSRTC",
        "Thiruvananthapuram",
        "KL",
        8.4880,
        76.9500,
        "KSRTC",
    ),
    ("ERS-BS", "Ernakulam Bus Stand", "Kochi", "KL", 9.9830, 76.3010, "KSRTC"),
    ("TEN-BS", "Tirunelveli Bus Stand", "Tirunelveli", "TN", 8.7280, 77.6960, "TNSTC"),
    ("GNT-BS", "Guntur Bus Stand", "Guntur", "AP", 16.3000, 80.4400, "APSRTC"),
    ("WL-BS", "Warangal Bus Stand", "Warangal", "TS", 17.9700, 79.5960, "TSRTC"),
    ("KRNT-BS", "Kurnool Bus Stand", "Kurnool", "AP", 15.8300, 78.0400, "APSRTC"),
    ("CLT-BS", "Kozhikode Bus Stand", "Kozhikode", "KL", 11.2600, 75.7820, "KSRTC"),
]

bus_routes_data = [
    (
        "KSRTC-1",
        "KSRTC",
        "SUPER_LUXURY",
        30,
        [("SBC-MJSTC", "00:00", "00:00", 0.0), ("MYS-BS", "03:00", "03:00", 400.0)],
    ),
    (
        "TNSTC-1",
        "TNSTC",
        "EXPRESS",
        60,
        [
            ("MAS-CMBT", "00:00", "00:00", 0.0),
            ("TPJ-BS", "05:00", "05:15", 300.0),
            ("MDU-BS", "08:00", "08:00", 450.0),
        ],
    ),
    (
        "APSRTC-1",
        "APSRTC",
        "SUPER_LUXURY",
        45,
        [("SC-MGBS", "00:00", "00:00", 0.0), ("BZA-BS", "05:00", "05:00", 600.0)],
    ),
    (
        "TSRTC-1",
        "TSRTC",
        "EXPRESS",
        30,
        [("SC-MGBS", "00:00", "00:00", 0.0), ("WL-BS", "03:00", "03:00", 250.0)],
    ),
    (
        "KSRTC-2",
        "KSRTC",
        "SLEEPER",
        120,
        [("SBC-MJSTC", "00:00", "00:00", 0.0), ("MAQ-BS", "08:00", "08:00", 800.0)],
    ),
    (
        "TNSTC-2",
        "TNSTC",
        "SUPER_LUXURY",
        90,
        [
            ("CBE-BS", "00:00", "00:00", 0.0),
            ("SA-BS", "03:00", "03:15", 250.0),
            ("MAS-CMBT", "10:00", "10:00", 700.0),
        ],
    ),
    (
        "APSRTC-2",
        "APSRTC",
        "SLEEPER",
        120,
        [("SC-MGBS", "00:00", "00:00", 0.0), ("TPTY-BS", "12:00", "12:00", 850.0)],
    ),
    (
        "KSRTC-3",
        "KSRTC",
        "EXPRESS",
        60,
        [("SBC-MJSTC", "00:00", "00:00", 0.0), ("UBL-BS", "07:00", "07:00", 550.0)],
    ),
    (
        "APSRTC-3",
        "APSRTC",
        "EXPRESS",
        60,
        [("BZA-BS", "00:00", "00:00", 0.0), ("VSKP-BS", "06:00", "06:00", 500.0)],
    ),
    (
        "APSRTC-4",
        "APSRTC",
        "EXPRESS",
        90,
        [("ATP-BS", "00:00", "00:00", 0.0), ("SBC-MJSTC", "05:00", "05:00", 400.0)],
    ),
    (
        "KSRTC-4",
        "KSRTC",
        "SUPER_LUXURY",
        45,
        [("TVC-BS", "00:00", "00:00", 0.0), ("ERS-BS", "05:00", "05:00", 350.0)],
    ),
    (
        "TNSTC-3",
        "TNSTC",
        "ORDINARY",
        120,
        [("SA-BS", "00:00", "00:00", 0.0), ("SBC-MJSTC", "05:00", "05:00", 300.0)],
    ),
]

nearby_data = [
    ("MAS", "MAS-CMBT", 4500, 15, "STATION_TO_BUS"),
    ("SBC", "SBC-MJSTC", 800, 10, "STATION_TO_BUS"),
    ("MDU", "MDU-BS", 3000, 12, "STATION_TO_BUS"),
    ("CBE", "CBE-BS", 1500, 8, "STATION_TO_BUS"),
    ("TPJ", "TPJ-BS", 2000, 10, "STATION_TO_BUS"),
    ("SA", "SA-BS", 1200, 7, "STATION_TO_BUS"),
    ("SC", "SC-MGBS", 2500, 12, "STATION_TO_BUS"),
    ("BZA", "BZA-BS", 1000, 6, "STATION_TO_BUS"),
    ("VSKP", "VSKP-BS", 1500, 8, "STATION_TO_BUS"),
    ("TPTY", "TPTY-BS", 1800, 9, "STATION_TO_BUS"),
    ("ATP", "ATP-BS", 900, 5, "STATION_TO_BUS"),
    ("GTL", "GTL-BS", 700, 4, "STATION_TO_BUS"),
    ("MYS", "MYS-BS", 1100, 6, "STATION_TO_BUS"),
    ("UBL", "UBL-BS", 600, 4, "STATION_TO_BUS"),
    ("MAQ", "MAQ-BS", 2000, 10, "STATION_TO_BUS"),
    ("TVC", "TVC-BS", 500, 3, "STATION_TO_BUS"),
    ("ERS", "ERS-BS", 1200, 7, "STATION_TO_BUS"),
    ("TEN", "TEN-BS", 800, 5, "STATION_TO_BUS"),
    ("GNT", "GNT-BS", 1300, 7, "STATION_TO_BUS"),
    ("WL", "WL-BS", 1000, 6, "STATION_TO_BUS"),
    ("CLT", "CLT-BS", 900, 5, "STATION_TO_BUS"),
    ("SC", "SC-JBS", 1500, 8, "STATION_TO_BUS"),
]

scoring_weights_data = [
    ("DEFAULT", 0.20, 0.10, 0.10, 0.15, 0.10, 0.10, 0.10, 0.08, 0.05, 0.02),
    ("WOMEN", 0.20, 0.10, 0.10, 0.12, 0.10, 0.08, 0.25, 0.03, 0.01, 0.01),
    ("SENIOR", 0.20, 0.10, 0.10, 0.10, 0.10, 0.25, 0.08, 0.03, 0.02, 0.02),
    ("STUDENT", 0.20, 0.10, 0.10, 0.30, 0.10, 0.05, 0.10, 0.03, 0.01, 0.01),
    ("FAMILY", 0.20, 0.10, 0.10, 0.15, 0.10, 0.15, 0.15, 0.03, 0.01, 0.01),
]

settings_data = [
    ("nearby_radius_km", "30", "FLOAT", "graph", "Default nearby station radius"),
    ("max_transfers", "3", "INTEGER", "graph", "Maximum allowed transfers"),
    (
        "min_transfer_buffer_mins",
        "20",
        "INTEGER",
        "graph",
        "Minimum buffer between connections",
    ),
    ("search_result_limit", "10", "INTEGER", "scoring", "Max results returned"),
    ("k_shortest_paths", "50", "INTEGER", "graph", "K for Yen's algorithm"),
    ("cache_search_ttl_seconds", "900", "INTEGER", "cache", "Search result cache TTL"),
    ("cache_station_ttl_seconds", "86400", "INTEGER", "cache", "Station cache TTL"),
    (
        "graph_rebuild_cron",
        '"0 3 * * 0"',
        "STRING",
        "graph",
        "Weekly graph rebuild schedule",
    ),
    ("min_graph_nodes", "500", "INTEGER", "graph", "Minimum graph nodes for health"),
    ("min_graph_edges", "2000", "INTEGER", "graph", "Minimum graph edges for health"),
]


async def seed_data():
    async with engine.begin() as conn:
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        # Check if already seeded
        result = await session.execute(select(Station).limit(1))
        if result.scalars().first():
            print("Database already seeded. Skipping.")
            return

        print("Seeding stations...")
        station_map = {}
        station_coords = {}
        for code, name, city, state, lat, lon, st_type, zone in stations_data:
            st = Station(
                id=str(uuid.uuid4()),
                code=code,
                name=name,
                city=city,
                state=state,
                latitude=lat,
                longitude=lon,
                station_type=st_type,
                zone=zone,
            )
            session.add(st)
            station_map[code] = st.id
            station_coords[code] = (lat, lon)
        await session.commit()

        print("Seeding train routes and stops...")
        for tr_num, tr_name, tr_type, runs_on, stops in train_routes_data:
            route = TrainRoute(
                id=str(uuid.uuid4()),
                train_number=tr_num,
                train_name=tr_name,
                train_type=tr_type,
                runs_on=runs_on,
            )
            session.add(route)

            total_dist = 0.0
            prev_code = None
            stop_objects = []

            for seq, (code, arr, dep, day) in enumerate(stops, start=1):
                if prev_code:
                    lat1, lon1 = station_coords[prev_code]
                    lat2, lon2 = station_coords[code]
                    dist = haversine(lat1, lon1, lat2, lon2)
                    total_dist += dist

                ts = TrainStop(
                    train_route_id=route.id,
                    station_id=station_map[code],
                    stop_sequence=seq,
                    arrival_time=arr,
                    departure_time=dep,
                    day_offset=day,
                    distance_from_origin=total_dist,
                )
                session.add(ts)
                stop_objects.append(ts)
                prev_code = code

            # Create fares for all combinations of stops
            for i in range(len(stop_objects)):
                for j in range(i + 1, len(stop_objects)):
                    st1 = stop_objects[i]
                    st2 = stop_objects[j]
                    dist = st2.distance_from_origin - st1.distance_from_origin

                    # Fares: Gen 0.5, Slp 1.0, AC3 2.0, AC2 3.0
                    for t_class, rate in [
                        ("GENERAL", 0.5),
                        ("SLEEPER", 1.0),
                        ("AC_3", 2.0),
                        ("AC_2", 3.0),
                    ]:
                        fare = TrainFare(
                            train_route_id=route.id,
                            from_station_id=st1.station_id,
                            to_station_id=st2.station_id,
                            travel_class=t_class,
                            fare_inr=max(10.0, round(dist * rate)),
                        )
                        session.add(fare)
        await session.commit()

        print("Seeding bus stops...")
        bus_map = {}
        for code, name, city, state, lat, lon, operator in bus_stops_data:
            bs = BusStop(
                id=str(uuid.uuid4()),
                code=code,
                name=name,
                city=city,
                state=state,
                latitude=lat,
                longitude=lon,
                operator=operator,
            )
            session.add(bs)
            bus_map[code] = bs.id
        await session.commit()

        print("Seeding bus routes and sequences...")
        for r_num, operator, b_type, freq, stops in bus_routes_data:
            br = BusRoute(
                id=str(uuid.uuid4()),
                route_number=r_num,
                operator=operator,
                bus_type=b_type,
                frequency_minutes=freq,
            )
            session.add(br)
            for seq, (code, arr, dep, fare) in enumerate(stops, start=1):
                bss = BusStopSequence(
                    bus_route_id=br.id,
                    bus_stop_id=bus_map[code],
                    stop_sequence=seq,
                    times=f"{arr}-{dep}",
                    fare=fare,
                )
                session.add(bss)
        await session.commit()

        print("Seeding nearby connections...")
        for st_code, bs_code, dist_m, walk_m, c_type in nearby_data:
            nc = NearbyConnection(
                station_id=station_map[st_code],
                bus_stop_id=bus_map[bs_code],
                connected_station_id=None,
                connected_bus_stop_id=None,
                distance_meters=dist_m,
                walking_time_minutes=walk_m,
                transfer_type=c_type,
            )
            session.add(nc)
        await session.commit()

        print("Seeding scoring weights...")
        for mode, tw, ww, trw, cw, aw, comw, saw, rew, wdw, arw in scoring_weights_data:
            sw = ScoringWeight(
                mode=mode,
                travel_time_weight=tw,
                waiting_time_weight=ww,
                transfers_weight=trw,
                cost_weight=cw,
                availability_weight=aw,
                comfort_weight=comw,
                safety_weight=saw,
                reliability_weight=rew,
                walking_distance_weight=wdw,
                arrival_penalty_weight=arw,
            )
            session.add(sw)
        await session.commit()

        print("Seeding system settings...")
        for key, val, v_type, cat, desc in settings_data:
            ss = SystemSetting(
                key=key,
                value={"v": val},
                category=cat,
            )
            session.add(ss)
        await session.commit()

        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())

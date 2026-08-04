import re

with open("app/infrastructure/database/seed.py", "r") as f:
    content = f.read()

# Specifically target BusStopSequence
bus_stop_sequence_pattern = r'(bss\s*=\s*BusStopSequence\([^)]+)arrival_time=arr,\s*departure_time=dep,'
content = re.sub(bus_stop_sequence_pattern, r'\1', content)

with open("app/infrastructure/database/seed.py", "w") as f:
    f.write(content)

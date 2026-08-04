import re

with open("app/infrastructure/database/seed.py", "r") as f:
    content = f.read()

# Remove id=str(uuid.uuid4()), for integer PK models
models_to_fix = ['TrainStop', 'TrainFare', 'BusStopSequence', 'NearbyConnection', 'ScoringWeight', 'SystemSetting']
for model in models_to_fix:
    pattern = rf'({model}\([^)]*)id=str\(uuid\.uuid4\(\)\),\s*'
    content = re.sub(pattern, r'\1', content)

# Fix BusStopSequence kwargs
content = content.replace("fare_from_origin=fare", "times=f'{arr}-{dep}', fare=fare")

# Fix ScoringWeight kwargs
content = content.replace("arrival_time_weight=arw", "arrival_penalty_weight=arw")

# Fix SystemSetting kwargs
content = content.replace("value_type=v_type,", "")
content = content.replace("description=desc", "")
content = content.replace("value=val,", 'value={"v": val},')

with open("app/infrastructure/database/seed.py", "w") as f:
    f.write(content)

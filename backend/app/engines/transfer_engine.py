from app.domain.entities.journey import Journey, TransferDifficultyResult
from app.domain.value_objects.enums import TransferDifficulty, TransportType

class TransferEngine:
    def analyze_transfers(self, journey: Journey) -> list[TransferDifficultyResult]:
        results = []
        
        for i in range(len(journey.segments) - 1):
            current_seg = journey.segments[i]
            next_seg = journey.segments[i+1]
            
            # Direct transfer (wait only)
            if current_seg.segment_type != TransportType.WALK and next_seg.segment_type != TransportType.WALK:
                buffer_minutes = int((next_seg.departure_time - current_seg.arrival_time).total_seconds() / 60)
                difficulty = TransferDifficulty.EASY
                if buffer_minutes < 15:
                    difficulty = TransferDifficulty.DIFFICULT
                elif buffer_minutes < 30:
                    difficulty = TransferDifficulty.MODERATE
                    
                results.append(TransferDifficultyResult(
                    station_name=current_seg.destination_name,
                    difficulty=difficulty,
                    walking_meters=0,
                    buffer_minutes=buffer_minutes,
                    walking_minutes=0
                ))
            
            # Transfer involving a walk
            elif current_seg.segment_type != TransportType.WALK and next_seg.segment_type == TransportType.WALK:
                walk_seg = next_seg
                if i + 2 < len(journey.segments):
                    target_seg = journey.segments[i+2]
                    buffer_minutes = int((target_seg.departure_time - current_seg.arrival_time).total_seconds() / 60)
                else:
                    buffer_minutes = walk_seg.duration_minutes
                
                walking_meters = int(walk_seg.distance_km * 1000)
                walking_minutes = walk_seg.duration_minutes
                
                if walking_meters > 1000 or buffer_minutes < walking_minutes + 10:
                    difficulty = TransferDifficulty.DIFFICULT
                elif walking_meters > 500 or buffer_minutes < walking_minutes + 20:
                    difficulty = TransferDifficulty.MODERATE
                else:
                    difficulty = TransferDifficulty.EASY
                
                results.append(TransferDifficultyResult(
                    station_name=walk_seg.origin_name,
                    difficulty=difficulty,
                    walking_meters=walking_meters,
                    buffer_minutes=buffer_minutes,
                    walking_minutes=walking_minutes
                ))
                
        return results

from app.domain.entities.journey import ScoredJourney, ExplainReason, ExplainedJourney, TransferDifficultyResult
from app.domain.value_objects.enums import TransferDifficulty

class ExplainabilityEngine:
    def explain(self, scored_journey: ScoredJourney, transfer_results: list[TransferDifficultyResult]) -> ExplainedJourney:
        positive_reasons = []
        negative_reasons = []
        badges = []
        
        # Analyze factor scores
        for factor, score in scored_journey.factor_scores.items():
            if score > 0.8:
                positive_reasons.append(ExplainReason(
                    icon="⭐",
                    text=f"Great {factor}",
                    factor=factor,
                    impact="HIGH",
                    strength="STRONG"
                ))
            elif score < 0.3:
                negative_reasons.append(ExplainReason(
                    icon="⚠️",
                    text=f"Poor {factor}",
                    factor=factor,
                    impact="HIGH",
                    strength="WEAK"
                ))
        
        # Transfer logic
        if any(tr.difficulty == TransferDifficulty.DIFFICULT for tr in transfer_results):
            negative_reasons.append(ExplainReason(
                icon="🏃",
                text="Contains difficult transfers",
                factor="transfers",
                impact="HIGH",
                strength="STRONG"
            ))
        elif all(tr.difficulty == TransferDifficulty.EASY for tr in transfer_results) and transfer_results:
            positive_reasons.append(ExplainReason(
                icon="✅",
                text="Easy transfers",
                factor="transfers",
                impact="HIGH",
                strength="STRONG"
            ))
            
        if scored_journey.overall_score >= 0.85:
            badges.append("Top Pick")
            
        return ExplainedJourney(
            scored_journey=scored_journey,
            positive_reasons=positive_reasons,
            negative_reasons=negative_reasons,
            badges=badges,
            recommendation_sentence=f"This journey scored {scored_journey.overall_score:.2f} overall.",
            transfer_difficulties=transfer_results
        )

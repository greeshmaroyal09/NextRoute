from app.domain.entities.journey import ExplainedJourney


class RecommendationEngine:
    def tag_recommendations(
        self, journeys: list[ExplainedJourney]
    ) -> list[ExplainedJourney]:
        if not journeys:
            return []

        # Sort journeys based on various parameters to assign tags/badges

        # Best Overall
        best_overall = max(journeys, key=lambda j: j.scored_journey.overall_score)
        if "Best Overall" not in best_overall.badges:
            best_overall.badges.append("Best Overall")

        # Cheapest
        cheapest = min(journeys, key=lambda j: j.scored_journey.journey.total_cost_inr)
        if "Cheapest" not in cheapest.badges:
            cheapest.badges.append("Cheapest")

        # Fastest
        fastest = min(
            journeys, key=lambda j: j.scored_journey.journey.total_duration_minutes
        )
        if "Fastest" not in fastest.badges:
            fastest.badges.append("Fastest")

        # Best for Women (example heuristic: least transfers or specialized factor score if available)
        # assuming 'safety_score' might be in factor scores
        best_for_women = max(
            journeys,
            key=lambda j: j.scored_journey.factor_scores.get("safety", 0.0),
            default=None,
        )
        if (
            best_for_women
            and best_for_women.scored_journey.factor_scores.get("safety", 0.0) > 0.7
        ):
            if "Best for Women" not in best_for_women.badges:
                best_for_women.badges.append("Best for Women")

        return journeys

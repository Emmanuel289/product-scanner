from typing import Dict, List, Optional, Tuple

from constants import FitScoreThreshold, Outcome, RiskLevel, SkinType, UserProfile


def extract_product_attrs(product: Dict) -> Tuple[List]:
    """
    Return the attributes of a product including supported skin types,
    concerns it targets, concerns it's not ideal for, and skin types
    to avoid usage.
    """
    product_skin_types = product.get("skin_types", [])
    skin_types_to_avoid = product.get("avoid_for", [])
    concerns_targeted = product.get("concerns_targeted", [])
    concerns_not_ideal = product.get("concerns_not_ideal", [])
    return (
        product_skin_types,
        skin_types_to_avoid,
        concerns_targeted,
        concerns_not_ideal,
    )


def extract_user_attrs(user_profile: UserProfile) -> Tuple[List]:
    """
    Return the attributes of a user including their skin type,
    any concerns, and whether or not they have sensitive skin.
    """
    user_profile_dict = user_profile.model_dump()
    user_skin_type = user_profile_dict.get("skin_type", "")
    concerns = user_profile_dict.get("concerns", [])
    user_sensitive = user_profile_dict.get("sensitive", False)

    return user_skin_type, concerns, user_sensitive


# ----- Fit score calculation ----- #
def compute_fit_score(product: Dict, user_profile: UserProfile) -> int:
    """
    Compute a 0-100 fit score for a product given a user profile.
    The score reflects how well the product's attributes align with
    the user's skin type, concerns, and sensitivities.
    """
    score = 61  # Start with a neutral score

    # Extract attributes from the user's profile
    user_skin_type, user_concerns, user_sensitive = extract_user_attrs(user_profile)
    # Extract attributes from the product
    product_skin_types, skin_types_to_avoid, concerns_targeted, concerns_not_ideal = (
        extract_product_attrs(product)
    )

    # Check if the user's skin type aligns with the product and whether
    # or not to avoid it.
    user_skin_type_val = user_skin_type.value if user_skin_type else ""
    if user_skin_type_val:
        if user_skin_type_val in product_skin_types:
            score += 20
        elif user_skin_type_val in skin_types_to_avoid:
            score -= 35

    # Cross-check the user's concerns with the product's targeted concerns
    matched_concerns = [
        concern for concern in user_concerns if concern in concerns_targeted
    ]
    # Assign a high positive bias to matching concerns
    score += len(matched_concerns) * 3

    # Cross-check the user's concerns with those that the product is not ideal for
    conflicting_concerns = [
        concern for concern in user_concerns if concern in concerns_not_ideal
    ]
    # Assign a higher negative bias to conflicting concerns
    score -= len(conflicting_concerns) * 11

    if (
        user_sensitive
        and product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value
    ):
        score -= 19

    # Penalize the fitness score if the user has an oily skin type and the product
    # has a high comedogenic risk
    if user_skin_type_val and user_skin_type_val in [
        SkinType.OILY.value,
        SkinType.COMBINATION.value,
    ]:
        if product.get("comedogenic_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
            score -= 11

    # Normalize the fit_score to 0-100
    fit_score = max(0, min(100, score))
    return fit_score


# ----- Deterministic rule engine ----- #
def generate_decision_summary(
    product: Dict, user_profile: Optional[UserProfile] = None
) -> Dict:
    """
    Given a product and optional user profile, return a decision summary including:
    - outcome (good/mixed/not recommended)
    - rationale (why it's recommended or not)
    - personalization flag
    """
    outcome = None
    rationale: List[str] = []
    personalized = False
    fit_score = None

    # --- Product skin type conflict check --- #
    skin_types: List = product.get("skin_types", [])
    if SkinType.DRY.value in skin_types and SkinType.OILY.value in skin_types:
        outcome = Outcome.MIXED.value
        rationale.append("This product is suitable for both dry and oily skin types.")

    # --- Comedogenic / sensitivity risk --- #
    if product.get("comedogenic_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        outcome = Outcome.NOT_RECOMMENDED.value
        rationale.append(
            "This product has a high comedogenic risk and may cause breakouts."
        )

    if product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        outcome = Outcome.NOT_RECOMMENDED.value
        rationale.append(
            "This product has a high sensitivity risk and may irritate the skin."
        )

    # --- Explicit avoid_for skin types --- #
    avoid: List = product.get("avoid_for", [])
    if avoid:
        rationale.append(
            f"This product is not ideal for {', '.join(avoid)} skin type(s)"
        )

    # --- Benefits and limitations --- #
    pros: List = product.get("pros", [])
    if pros:
        rationale.append("The key benefits of this product include: " + ", ".join(pros))

    cons: List = product.get("cons", [])
    if cons:
        rationale.append("The limitations of this product include: " + ", ".join(cons))

    # --- Personalization logic --- #
    if user_profile:
        personalized = True
        user_profile_dict = user_profile.model_dump()

        user_skin_type: Optional[SkinType] = user_profile_dict.get("skin_type", None)
        user_skin_type_val = user_skin_type.value if user_skin_type else ""
        user_concerns = user_profile_dict.get("concerns", [])
        user_sensitive = user_profile_dict.get("sensitive", False)

        # --- Skin type alignment --- #
        if user_skin_type_val:
            if user_skin_type_val in skin_types:
                rationale.append(
                    f"This product is well aligned with your {user_skin_type_val} skin type."
                )
            elif user_skin_type_val in product.get("avoid_for", []):
                outcome = Outcome.NOT_RECOMMENDED.value
                rationale.append(
                    f"This product is not suitable for your {user_skin_type_val} skin type."
                )

        # --- Concern targeting --- #
        concerns_targeted = product.get("concerns_targeted", [])
        concerns_not_ideal = product.get("concerns_not_ideal", [])

        matched_concerns = [
            concern for concern in user_concerns if concern in concerns_targeted
        ]
        if matched_concerns:
            rationale.append(
                f"This product targets your concerns: {', '.join(matched_concerns)}"
            )

        conflicting_concerns = [
            concern for concern in user_concerns if concern in concerns_not_ideal
        ]
        if conflicting_concerns:
            outcome = Outcome.NOT_RECOMMENDED.value
            rationale.append(
                f"This product may not be ideal for your concerns: {', '.join(conflicting_concerns)}"
            )

        # --- Sensitivity override --- #
        if (
            user_sensitive
            and product.get("sensitivity_risk", RiskLevel.LOW.value)
            == RiskLevel.HIGH.value
        ):
            outcome = Outcome.NOT_RECOMMENDED.value
            rationale.append(
                "This product has a high sensitivity risk level and you indicated having sensitive skin."
            )

        # --- Compute the fitness score for a selected user profile --- #
        fit_score = compute_fit_score(product, user_profile)

        if fit_score >= FitScoreThreshold.GOOD.value:
            outcome = Outcome.GOOD.value
        elif (
            fit_score >= FitScoreThreshold.MIXED.value
            and fit_score < FitScoreThreshold.GOOD.value
        ):
            outcome = Outcome.MIXED.value
        else:
            outcome = Outcome.NOT_RECOMMENDED.value

    # --- Final summary --- #
    summary = {
        "outcome": outcome,
        "rationale": rationale,
        "personalized": personalized,
        "fit_score": fit_score,
        "skin_types": product.get("skin_types", []),
        "texture": product.get("texture", ""),
        "finish": product.get("finish", ""),
        "ingredient_intent": product.get("ingredient_intent", ""),
        "pros": product.get("pros", []),
        "cons": product.get("cons", []),
        "category": product.get("category", ""),
        "coverage": product.get("coverage"),
        "best_for": product.get("best_for", []),
        "avoid_for": product.get("avoid_for", []),
        "concerns_targeted": product.get("concerns_targeted", []),
        "concerns_not_ideal": product.get("concerns_not_ideal", []),
        "comedogenic_risk": product.get("comedogenic_risk", RiskLevel.LOW.value),
        "sensitivity_risk": product.get("sensitivity_risk", RiskLevel.LOW.value),
    }

    return summary

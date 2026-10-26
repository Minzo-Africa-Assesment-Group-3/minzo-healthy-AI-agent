from app.llm.openai import moderation_llm
from app.schemas.moderation import ReviewModerationDecision


def moderate_comment(comment: str) -> ReviewModerationDecision:
    prompt = f"""
        You are a content moderation agent for a healthcare review platform.

        Your job is to review comments written about healthcare professionals
        and healthcare institutions.

        The platform allows users to write both positive and negative reviews.
        Negative reviews are allowed as long as they are respectful and relevant
        to the user's experience.

        Classify the comment into an appropriate moderation action.

        Use these categories when applicable:

        - harassment
        - hate
        - threat
        - sexual_content
        - personal_information
        - spam
        - fraud
        - profanity
        - none

        Important rules:

        - Do NOT reject a review simply because it is negative.
        - Do NOT reject a review merely because it expresses dissatisfaction.
        - The user is allowed to criticize healthcare professionals or institutions.
        - Complaints about waiting times, service quality, communication,
        treatment experience, cost, and similar experiences are allowed.
        - Focus on whether the criticism is expressed as a legitimate review
        rather than harassment or abuse.
        - Do not invent information that is not present in the comment.

        Use these actions:

        1. allow
        - Genuine positive or negative feedback.
        - Respectful criticism.
        - Complaints about waiting time, service quality,
            communication, treatment experience, cost, etc.

        2. flag
        - Content that may require human review.
        - Content where the intent or severity is unclear.
        - Potentially problematic content where an automatic rejection
            would be inappropriate.

        3. block
        - Harassment.
        - Threats.
        - Hate or degrading attacks.
        - Sexual content that violates platform rules.
        - Exposure of personal information.
        - Spam or unrelated advertising.
        - Fraudulent or deceptive content.
        - Profanity used primarily to attack or harass someone.

        For your response, provide all of these fields:

        - is_abusive:
        true when the review contains abusive, threatening, hateful,
        harassing, or otherwise clearly abusive content.
        false for legitimate respectful reviews.

        - action:
        choose exactly one of:
        allow, flag, block.

        - categories:
        provide one or more relevant categories.
        Use "none" by itself when there is no violation.

        - severity:
        choose exactly one:
        none, low, medium, high.

        - confidence:
        a number between 0 and 1 representing your confidence
        in the moderation decision.

        - explanation:
        briefly explain why the action was chosen.

        - requires_human_review:
        true when the content should be reviewed by a human.
        Otherwise false.

        Important:
        - A legitimate negative review should normally be:
        is_abusive=false, action=allow, categories=["none"],
        severity="none", requires_human_review=false.
        - Do not treat criticism or dissatisfaction as abuse.

        Comment to moderate: {comment}
    """

    return moderation_llm.invoke(prompt)


def adapt_moderation_decision(
    result: ReviewModerationDecision,
) -> dict:
    """Convert the AI moderation decision to Minzo's response format."""

    if result.action == "allow":
        decision = "APPROVED"

    elif result.action == "flag":
        decision = "FLAGGED"

    elif result.action == "block":
        decision = "REJECTED"

    else:
        raise ValueError(
            f"Unknown moderation action: {result.action}"
        )

    return {
        "decision": decision,
        "reason": result.explanation,
        "confidence": result.confidence,
        "categories": result.categories,
    }
    
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import ModerationResult


client = TestClient(app)


def test_empty_comment():
    response = client.post(
        "/moderate",
        json={"comment": ""},
    )

    assert response.status_code == 422


def test_comment_too_long():
    comment = "a" * 2001

    response = client.post(
        "/moderate",
        json={"comment": comment},
    )

    assert response.status_code == 422


def test_allowed_review(monkeypatch):
    def mock_moderate_comment(comment):
        return ModerationResult(
            allowed=True,
            category="allowed",
            reason="The review is respectful and relevant.",
            suggestion="",
        )

    monkeypatch.setattr(
        "app.main.moderate_comment",
        mock_moderate_comment,
    )

    response = client.post(
        "/moderate",
        json={
            "comment": "The doctor was professional and helpful."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["allowed"] is True
    assert data["category"] == "allowed"


def test_abusive_review(monkeypatch):
    def mock_moderate_comment(comment):
        return ModerationResult(
            allowed=False,
            category="abusive",
            reason="The review contains abusive language.",
            suggestion="Please rewrite your review using respectful language.",
        )

    monkeypatch.setattr(
        "app.main.moderate_comment",
        mock_moderate_comment,
    )

    response = client.post(
        "/moderate",
        json={
            "comment": "This doctor is terrible."
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["allowed"] is False
    assert data["category"] == "abusive"


def test_spam_review(monkeypatch):
    def mock_moderate_comment(comment):
        return ModerationResult(
            allowed=False,
            category="spam",
            reason="The review contains promotional content.",
            suggestion="Please remove promotional content and describe your healthcare experience.",
        )

    monkeypatch.setattr(
        "app.main.moderate_comment",
        mock_moderate_comment,
    )

    response = client.post(
        "/moderate",
        json={
            "comment": "BUY OUR AMAZING PRODUCT NOW!"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["allowed"] is False
    assert data["category"] == "spam"
    
    
def test_moderation_service_error(monkeypatch):
    def mock_moderate_comment(comment):
        raise Exception("OpenAI API error")

    monkeypatch.setattr(
        "app.main.moderate_comment",
        mock_moderate_comment,
    )

    response = client.post(
        "/moderate",
        json={
            "comment": "The doctor was helpful."
        },
    )

    assert response.status_code == 503

    data = response.json()

    assert data["detail"] == (
        "The moderation service is temporarily unavailable. "
        "Please try again later."
    )

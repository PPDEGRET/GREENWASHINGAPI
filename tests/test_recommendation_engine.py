import pytest
from src.app.services.recommendation_engine import RecommendationEngine

@pytest.fixture
def engine():
    """Provides a RecommendationEngine instance for testing."""
    return RecommendationEngine()

def test_detect_superlatives_trigger(engine):
    """Tests that the 'superlatives' trigger is correctly detected."""
    text = "Our new product is 100% sustainable and totally green."
    triggers = engine.detect_rule_based_triggers(text)
    assert "superlatives" in triggers

def test_detect_future_claims_trigger(engine):
    """Tests that the 'future_claims' trigger is correctly detected."""
    text = "We have a goal to be carbon neutral by 2040."
    triggers = engine.detect_rule_based_triggers(text)
    assert "future_claims" in triggers

def test_detect_offsets_trigger(engine):
    """Tests that the 'offsets' trigger is correctly detected."""
    text = "We offset our emissions through carbon credit programs."
    triggers = engine.detect_rule_based_triggers(text)
    assert "offsets" in triggers

def test_no_triggers_found(engine):
    """Tests that no triggers are found in a compliant text."""
    text = "Our product's packaging is made from 50% recycled materials, as certified by an independent third party."
    triggers = engine.detect_rule_based_triggers(text)
    assert not triggers

def test_multiple_triggers_found(engine):
    """Tests that multiple unique triggers can be detected in the same text."""
    text = "By 2050, we will be 100% eco-friendly thanks to our offset programs."
    triggers = engine.detect_rule_based_triggers(text)
    assert "superlatives" in triggers
    assert "future_claims" in triggers
    assert "offsets" in triggers
    assert len(triggers) == 3

def test_generate_recommendations_from_triggers(engine):
    """Tests the mapping from triggers to RecommendationItem objects."""
    triggers = ["superlatives", "future_claims"]
    recommendations = engine.generate_recommendations(triggers)

    assert len(recommendations) == 2

    rec_types = [rec.type for rec in recommendations]
    assert "avoid_absolute" in rec_types
    assert "future_claims" in rec_types

    superlative_rec = next(r for r in recommendations if r.type == "avoid_absolute")
    assert superlative_rec.severity == 3
    assert superlative_rec.triggered_by == ["superlatives"]

def test_generate_recommendations_empty(engine):
    """Tests that an empty list of triggers produces an empty list of recommendations."""
    recommendations = engine.generate_recommendations([])
    assert not recommendations

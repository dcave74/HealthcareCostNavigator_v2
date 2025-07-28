
import pytest
from app.models import Provider, ProviderPricing, ProviderRating

def test_provider_model(db_session):
    """Test Provider model creation"""
    provider = Provider(
        provider_id=1,
        provider_name="Test Hospital",
        provider_city="Test City",
        provider_state="NY",
        provider_zip_code="12345"
    )

    db_session.add(provider)
    db_session.commit()

    # Query the provider
    queried_provider = db_session.query(Provider).filter(Provider.provider_id == 1).first()
    assert queried_provider is not None
    assert queried_provider.provider_name == "Test Hospital"
    assert queried_provider.provider_status == "UNKNOWN"  # Default value

def test_provider_pricing_relationship(db_session):
    """Test Provider-ProviderPricing relationship"""
    # Create provider
    provider = Provider(
        provider_id=1,
        provider_name="Test Hospital",
        provider_city="Test City",
        provider_state="NY",
        provider_zip_code="12345"
    )
    db_session.add(provider)

    # Create pricing
    pricing = ProviderPricing(
        provider_id=1,
        ms_drg_definition="Test DRG",
        averaged_covered_charges=10000
    )
    db_session.add(pricing)
    db_session.commit()

    # Test relationship
    queried_provider = db_session.query(Provider).filter(Provider.provider_id == 1).first()
    assert len(queried_provider.pricing) == 1
    assert queried_provider.pricing[0].ms_drg_definition == "Test DRG"

def test_provider_rating_relationship(db_session):
    """Test Provider-ProviderRating relationship"""
    # Create provider
    provider = Provider(
        provider_id=1,
        provider_name="Test Hospital",
        provider_city="Test City",
        provider_state="NY",
        provider_zip_code="12345"
    )
    db_session.add(provider)

    # Create rating
    rating = ProviderRating(
        provider_id=1,
        provider_overall_rating=4,
        provider_star_rating=5
    )
    db_session.add(rating)
    db_session.commit()

    # Test relationship
    queried_provider = db_session.query(Provider).filter(Provider.provider_id == 1).first()
    assert len(queried_provider.rating) == 1
    assert queried_provider.rating[0].provider_overall_rating == 4

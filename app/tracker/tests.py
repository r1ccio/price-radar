import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from tracker.models import Target, PriceHistory
from tracker.tasks import parse_target_price

User = get_user_model()

#FIXTURES

@pytest.fixture
def test_data():
    user = User.objects.create_user(username="tester", password="password")
    target = Target.objects.create(
        user=user,
        url="https://rozetka.com.ua/test/iphone",
        target_price=40000.0,
        title="",
        current_price=None
    )

    html_with_json_ld = """
    <html>
        <head><title>Apple iPhone 15</title></head>
        <body>
            <script type="application/ld+json">
            {
                "@context": "http://schema.org",
                "@type": "Product",
                "name": "Apple iPhone 15",
                "offers": {
                    "@type": "Offer",
                    "price": "39999.0",
                    "priceCurrency": "UAH"
                }
            }
            </script>
        </body>
    </html>
    """

    html_empty = "<html><head><title>No Price</title></head><body><h1>Empty</h1></body></html>"

    return {
        "target": target,
        "html_with_json_ld": html_with_json_ld,
        "html_empty": html_empty
    }

#TESTS

@pytest.mark.django_db
@patch('tracker.tasks.fetch_html_with_playwright')
def test_parse_target_price_success(mock_fetch, test_data):
    mock_fetch.return_value = test_data["html_with_json_ld"]
    target = test_data["target"]

    result = parse_target_price(target.id)
    target.refresh_from_db()

    assert target.current_price == 39999.0
    assert target.title == "Apple iPhone 15"
    assert PriceHistory.objects.filter(target=target, price=39999.0).exists()
    assert "Successfully updated Target in result"

@pytest.mark.django_db
@patch('tracker.tasks.fetch_html_with_playwright')
def test_parse_target_price_not_found(mock_fetch, test_data):
    mock_fetch.return_value = test_data["html_empty"]
    target = test_data["target"]

    result = parse_target_price(target.id)
    target.refresh_from_db()

    assert target.current_price is None
    assert "Could not extract price" in result


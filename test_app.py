import pytest
from unittest.mock import patch, MagicMock
from app import app, checkout, get_active_flash_sale, flash_sale

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.get_cart_items')
@patch('app.flash')
@patch('app.redirect')
@patch('app.url_for')
def test_checkout_get_empty_cart(mock_url_for, mock_redirect, mock_flash, mock_get_cart_items, client):
    mock_get_cart_items.return_value = []
    mock_url_for.return_value = '/cart'

    with app.test_request_context('/checkout', method='GET'):
        response = checkout()

    mock_flash.assert_called_once_with("Your bag is empty. Add an item before checking out.", "warning")
    mock_url_for.assert_called_with('cart')
    mock_redirect.assert_called_once()

@patch('app.get_cart_items')
@patch('app.render_template')
def test_checkout_get_with_items(mock_render_template, mock_get_cart_items, client):
    mock_items = [
        {'name': 'Test Item', 'quantity': 1, 'subtotal': 10.0},
        {'name': 'Test Item 2', 'quantity': 2, 'subtotal': 20.0}
    ]
    mock_get_cart_items.return_value = mock_items

    with app.test_request_context('/checkout', method='GET'):
        response = checkout()

    mock_render_template.assert_called_once_with("checkout.html", items=mock_items, total=30.0, categories=[])

@patch('app.get_cart_items')
@patch('app.flash')
@patch('app.render_template')
def test_checkout_post_empty_cart(mock_render_template, mock_flash, mock_get_cart_items, client):
    mock_get_cart_items.return_value = []

    with app.test_request_context('/checkout', method='POST'):
        response = checkout()

    # It should redirect, but since we patched, check flash
    mock_flash.assert_called_once_with("Your bag is empty. Add an item before checking out.", "warning")

@patch('app.get_cart_items')
@patch('app.flash')
@patch('app.render_template')
def test_checkout_post_missing_fields(mock_render_template, mock_flash, mock_get_cart_items, client):
    mock_items = [{'name': 'Test Item', 'quantity': 1, 'subtotal': 10.0}]
    mock_get_cart_items.return_value = mock_items

    with app.test_request_context('/checkout', method='POST', data={}):
        response = checkout()

    mock_flash.assert_called_once_with("Please fill in all required fields.", "danger")
    mock_render_template.assert_called_once_with("checkout.html", items=mock_items, total=10.0, categories=[])

@patch('app.get_cart_items')
@patch('app.get_db_connection')
@patch('app.session')
@patch('app.flash')
@patch('app.redirect')
@patch('app.url_for')
def test_checkout_post_success(mock_url_for, mock_redirect, mock_flash, mock_session, mock_get_db_connection, mock_get_cart_items, client):
    mock_items = [
        {'name': 'Test Item', 'quantity': 1, 'subtotal': 10.0},
        {'name': 'Test Item 2', 'quantity': 2, 'subtotal': 20.0}
    ]
    mock_get_cart_items.return_value = mock_items
    mock_conn = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_url_for.return_value = '/'

    data = {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'address': '123 Main St',
        'city': 'Anytown',
        'postal_code': '12345',
        'country': 'USA'
    }

    with app.test_request_context('/checkout', method='POST', data=data):
        response = checkout()

    expected_items = "Test Item x1; Test Item 2 x2"
    mock_conn.execute.assert_called_once_with(
        "INSERT INTO orders (full_name, email, address, city, postal_code, country, total, items) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ('John Doe', 'john@example.com', '123 Main St', 'Anytown', '12345', 'USA', 30.0, expected_items)
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_session.pop.assert_called_once_with('cart', None)
    mock_flash.assert_called_once_with("Thank you for your order! Your purchase has been processed.", "success")
    mock_url_for.assert_called_with('index')
    mock_redirect.assert_called_once()

# ── Flash Sale Tests ───────────────────────────────────────────────────────────

@patch('app.get_db_connection')
def test_get_active_flash_sale_returns_none_when_no_sale(mock_get_db_connection):
    """get_active_flash_sale() returns None when the DB has no matching row."""
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = None
    mock_get_db_connection.return_value = mock_conn

    with app.test_request_context('/'):
        result = get_active_flash_sale()

    assert result is None


@patch('app.get_db_connection')
def test_get_active_flash_sale_returns_row_when_active(mock_get_db_connection):
    """get_active_flash_sale() returns a row dict when a sale is active."""
    mock_row = MagicMock()
    mock_row.__getitem__ = lambda self, k: "2099-01-01 00:00:00" if k == "end_time" else 1
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = mock_row
    mock_get_db_connection.return_value = mock_conn

    with app.test_request_context('/'):
        result = get_active_flash_sale()

    assert result is not None


@patch('app.get_active_flash_sale')
@patch('app.query_products')
@patch('app.render_template')
def test_flash_sale_route_no_active_sale(mock_render, mock_query, mock_get_active, client):
    """GET /flash-sale renders flash_sale.html with no products when sale is inactive."""
    mock_get_active.return_value = None
    mock_render.return_value = ""

    with app.test_request_context('/flash-sale'):
        flash_sale()

    mock_render.assert_called_once()
    call_kwargs = mock_render.call_args
    assert call_kwargs[0][0] == "flash_sale.html"
    assert call_kwargs[1]['active_sale'] is None
    assert call_kwargs[1]['products'] == []
    assert call_kwargs[1]['sale_end_time'] is None


@patch('app.get_active_flash_sale')
@patch('app.query_products')
@patch('app.render_template')
def test_flash_sale_route_active_sale(mock_render, mock_query, mock_get_active, client):
    """GET /flash-sale passes products and sale_end_time when sale is active."""
    mock_sale = MagicMock()
    mock_sale.__getitem__ = lambda self, k: "2099-12-31 23:59:59" if k == "end_time" else 1
    mock_get_active.return_value = mock_sale
    mock_query.return_value = [{"id": 1, "name": "Sale Item", "flash_sale_price": 29.99, "price": 59.99}]
    mock_render.return_value = ""

    with app.test_request_context('/flash-sale'):
        flash_sale()

    mock_render.assert_called_once()
    call_kwargs = mock_render.call_args
    assert call_kwargs[0][0] == "flash_sale.html"
    assert call_kwargs[1]['active_sale'] is not None
    assert call_kwargs[1]['sale_end_time'] == "2099-12-31 23:59:59"


@patch('app.get_active_flash_sale')
@patch('app.query_products')
@patch('app.session', {'cart': {'1': 2}})
def test_get_cart_items_applies_flash_price(mock_query, mock_get_active):
    """get_cart_items() uses flash_sale_price when a sale is active."""
    from app import get_cart_items

    mock_product = MagicMock()
    mock_product.__getitem__ = lambda self, k: {
        'id': 1, 'name': 'Sneaker', 'price': 100.0,
        'flash_sale': 1, 'flash_sale_price': 60.0, 'image_url': '/img/1.svg'
    }[k]
    mock_product.__contains__ = lambda self, k: k in {
        'id', 'name', 'price', 'flash_sale', 'flash_sale_price', 'image_url'
    }
    mock_query.return_value = [mock_product]

    mock_sale = MagicMock()
    mock_get_active.return_value = mock_sale

    with app.test_request_context('/'):
        items = get_cart_items()

    assert len(items) == 1
    assert items[0]['price'] == 60.0
    assert items[0]['original_price'] == 100.0
    assert items[0]['on_flash_sale'] is True
    assert items[0]['subtotal'] == 120.0


@patch('app.get_active_flash_sale')
@patch('app.query_products')
@patch('app.session', {'cart': {'1': 1}})
def test_get_cart_items_uses_regular_price_when_no_sale(mock_query, mock_get_active):
    """get_cart_items() uses regular price when no flash sale is active."""
    from app import get_cart_items

    mock_product = MagicMock()
    mock_product.__getitem__ = lambda self, k: {
        'id': 1, 'name': 'Sneaker', 'price': 100.0,
        'flash_sale': 0, 'flash_sale_price': None, 'image_url': '/img/1.svg'
    }[k]
    mock_product.__contains__ = lambda self, k: k in {
        'id', 'name', 'price', 'flash_sale', 'flash_sale_price', 'image_url'
    }
    mock_query.return_value = [mock_product]
    mock_get_active.return_value = None

    with app.test_request_context('/'):
        items = get_cart_items()

    assert len(items) == 1
    assert items[0]['price'] == 100.0
    assert items[0]['on_flash_sale'] is False

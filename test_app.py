import pytest
from unittest.mock import patch, MagicMock
from app import app, checkout

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
    mock_redirect.assert_called_once()</content>
<parameter name="filePath">c:\Users\HarshSharma\Downloads\InClassDemo-GHC (30thApril)\test_app.py
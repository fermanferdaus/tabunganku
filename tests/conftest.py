import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
from main import app as flask_app  # noqa: E402


@pytest.fixture
def app():
    """Flask app fixture untuk testing."""
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_token(app):
    """Generate JWT token valid untuk testing."""
    from services.auth_service import generate_token
    return generate_token(1, 'admin')


@pytest.fixture
def authed_client(client, auth_token):
    """Test client dengan JWT cookie sudah di-set."""
    client.set_cookie('access_token', auth_token, domain='localhost')
    return client

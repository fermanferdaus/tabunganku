from validators.auth_validator import validate_login, validate_change_password


class TestValidateLogin:
    def test_empty_username(self):
        errors = validate_login('', 'pass')
        assert len(errors) > 0
        assert any('Username' in e for e in errors)

    def test_empty_password(self):
        errors = validate_login('admin', '')
        assert len(errors) > 0
        assert any('Password' in e for e in errors)

    def test_both_empty(self):
        errors = validate_login('', '')
        assert len(errors) == 2

    def test_valid(self):
        errors = validate_login('admin', 'admin')
        assert len(errors) == 0

    def test_whitespace_username(self):
        errors = validate_login('   ', 'pass')
        assert len(errors) > 0


class TestValidateChangePassword:
    def test_empty_old(self):
        errors = validate_change_password('', 'new', 'new')
        assert len(errors) > 0

    def test_empty_new(self):
        errors = validate_change_password('old', '', 'confirm')
        assert len(errors) > 0

    def test_short_new(self):
        errors = validate_change_password('old', 'ab', 'ab')
        assert len(errors) > 0
        assert any('minimal' in e for e in errors)

    def test_mismatch_confirm(self):
        errors = validate_change_password('old', 'newpass', 'different')
        assert len(errors) > 0
        assert any('cocok' in e for e in errors)

    def test_empty_confirm(self):
        errors = validate_change_password('old', 'newpass', '')
        assert len(errors) > 0

    def test_valid(self):
        errors = validate_change_password('old', 'newpass', 'newpass')
        assert len(errors) == 0

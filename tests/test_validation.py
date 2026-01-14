"""Unit tests for task form validation."""
from tasks_routes import validate_task_form


class TestValidateTaskForm:
    """Test suite for validate_task_form function."""

    def test_valid_task_with_title_and_description(self):
        """Test validation passes with valid title and description."""
        form_data = {
            'title': 'Buy groceries',
            'description': 'Milk, eggs, and bread'
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert errors == {}
        assert cleaned_data['title'] == 'Buy groceries'
        assert cleaned_data['description'] == 'Milk, eggs, and bread'

    def test_valid_task_with_title_only(self):
        """Test validation passes with only title (description is optional)."""
        form_data = {
            'title': 'Buy groceries',
            'description': ''
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert errors == {}
        assert cleaned_data['title'] == 'Buy groceries'
        assert cleaned_data['description'] == ''

    def test_missing_title(self):
        """Test validation fails when title is missing."""
        form_data = {
            'title': '',
            'description': 'Some description'
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert 'title' in errors
        assert errors['title'] == 'Title is required'

    def test_title_too_long(self):
        """Test validation fails when title exceeds 255 characters."""
        long_title = 'a' * 256
        form_data = {
            'title': long_title,
            'description': 'Some description'
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert 'title' in errors
        assert errors['title'] == 'Title must be 255 characters or less'

    def test_title_exactly_255_characters(self):
        """Test validation passes when title is exactly 255 characters."""
        title_255 = 'a' * 255
        form_data = {
            'title': title_255,
            'description': ''
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert errors == {}
        assert len(cleaned_data['title']) == 255

    def test_description_too_long(self):
        """Test validation fails when description exceeds 255 characters."""
        long_description = 'b' * 256
        form_data = {
            'title': 'Valid title',
            'description': long_description
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert 'description' in errors
        assert errors['description'] == 'Description must be 255 characters or less'

    def test_description_exactly_255_characters(self):
        """Test validation passes when description is exactly 255 characters."""
        description_255 = 'b' * 255
        form_data = {
            'title': 'Valid title',
            'description': description_255
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert errors == {}
        assert len(cleaned_data['description']) == 255

    def test_whitespace_stripping(self):
        """Test that leading and trailing whitespace is stripped."""
        form_data = {
            'title': '  Buy groceries  ',
            'description': '  Milk and eggs  '
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert errors == {}
        assert cleaned_data['title'] == 'Buy groceries'
        assert cleaned_data['description'] == 'Milk and eggs'

    def test_missing_form_keys(self):
        """Test validation handles missing form keys gracefully."""
        form_data = {}
        errors, cleaned_data = validate_task_form(form_data)

        assert 'title' in errors
        assert errors['title'] == 'Title is required'

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are reported."""
        form_data = {
            'title': '',
            'description': 'x' * 256
        }
        errors, cleaned_data = validate_task_form(form_data)

        assert 'title' in errors
        assert 'description' in errors
        assert len(errors) == 2

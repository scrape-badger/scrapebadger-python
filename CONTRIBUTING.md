# Contributing to ScrapeBadger Python SDK

Thank you for your interest in contributing to the ScrapeBadger Python SDK! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Getting Started

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/scrapebadger-python.git
   cd scrapebadger-python
   ```

2. **Install dependencies:**

   ```bash
   uv sync --dev
   ```

3. **Install pre-commit hooks:**

   ```bash
   uv run pre-commit install
   ```

4. **Verify setup:**

   ```bash
   uv run pytest
   uv run ruff check src/ tests/
   uv run mypy src/
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/scrapebadger --cov-report=html

# Run specific tests
uv run pytest tests/test_client.py -v

# Run tests matching a pattern
uv run pytest -k "test_user"
```

### Code Quality

```bash
# Lint code
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Type check
uv run mypy src/
```

### All Checks

Before committing, run all checks:

```bash
uv run ruff check src/ tests/ && \
uv run ruff format --check src/ tests/ && \
uv run mypy src/ && \
uv run pytest
```

## Making Changes

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

Example: `feature/add-spaces-support`, `fix/pagination-cursor`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(twitter): add spaces endpoint support
fix(pagination): handle empty cursor correctly
docs: update authentication examples
test(users): add tests for get_followers_all
```

### Code Style

- Follow PEP 8 (enforced by Ruff)
- Use type hints for all public functions
- Write docstrings for all public classes and methods
- Keep line length under 100 characters
- Use descriptive variable names

### Adding New Features

1. **Create models in `src/scrapebadger/twitter/models.py`:**

   ```python
   class NewFeature(_BaseModel):
       """Description of the new feature.

       Attributes:
           id: Unique identifier.
           name: Feature name.
       """
       id: str
       name: str
   ```

2. **Add endpoint methods to the appropriate client:**

   ```python
   async def get_new_feature(
       self,
       feature_id: str,
       *,
       cursor: str | None = None,
   ) -> PaginatedResponse[NewFeature]:
       """Get a new feature.

       Args:
           feature_id: The feature ID.
           cursor: Pagination cursor.

       Returns:
           Paginated response containing features.

       Example:
           ```python
           features = await client.twitter.new.get_new_feature("123")
           ```
       """
       response = await self._client.get(
           f"/v1/twitter/new/{feature_id}",
           params={"cursor": cursor},
       )
       data = [NewFeature.model_validate(item) for item in response.get("data", []) or []]
       return PaginatedResponse(data=data, next_cursor=response.get("next_cursor"))
   ```

3. **Add tests in `tests/`:**

   ```python
   class TestNewFeature:
       async def test_get_new_feature(self, client):
           # Test implementation
           pass
   ```

4. **Update exports in `__init__.py` files**

5. **Update README.md with examples**

6. **Update CHANGELOG.md**

### Writing Tests

- Use pytest with async support
- Mock HTTP responses using `respx`
- Test both success and error cases
- Test edge cases (empty results, pagination)

Example test:

```python
import pytest
import respx
from httpx import Response

from scrapebadger import ScrapeBadger

class TestNewFeature:
    @respx.mock
    async def test_get_new_feature_success(self):
        respx.get("https://api.scrapebadger.com/v1/twitter/new/123").mock(
            return_value=Response(200, json={
                "data": [{"id": "1", "name": "Feature 1"}],
                "next_cursor": None
            })
        )

        async with ScrapeBadger(api_key="test") as client:
            result = await client.twitter.new.get_new_feature("123")

        assert len(result.data) == 1
        assert result.data[0].name == "Feature 1"
```

## Pull Request Process

1. **Update your branch:**

   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all checks:**

   ```bash
   uv run ruff check src/ tests/
   uv run ruff format --check src/ tests/
   uv run mypy src/
   uv run pytest
   ```

3. **Push your branch:**

   ```bash
   git push origin feature/your-feature
   ```

4. **Create a Pull Request** with:
   - Clear title describing the change
   - Description of what changed and why
   - Link to any related issues
   - Screenshots if UI changes

5. **Address review feedback** by pushing additional commits

6. **Squash and merge** once approved

## Reporting Issues

### Bug Reports

Include:
- Python version
- SDK version
- Minimal reproduction code
- Expected vs actual behavior
- Error messages and stack traces

### Feature Requests

Include:
- Use case description
- Proposed API design
- Any alternative solutions considered

## Questions?

- Open a GitHub issue
- Email: support@scrapebadger.com
- Discord: [Join our community](https://discord.com/invite/3WvwTyWVCx)

Thank you for contributing!

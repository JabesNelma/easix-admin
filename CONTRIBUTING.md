# Contributing to Easix

Thank you for considering contributing to Easix! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

1. Check the [issue tracker](https://github.com/easix-admin/easix/issues) to see if the bug has already been reported.
2. If not, create a new issue with:
   - A clear title and description
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Django and Python versions
   - Any relevant screenshots or logs

### Suggesting Features

1. Check the [roadmap](CHANGELOG.md) to see if the feature is planned.
2. Create a new issue with the "enhancement" label.
3. Describe the feature and its use case.

### Pull Requests

1. Fork the repository.
2. Create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes.
4. Write or update tests.
5. Ensure all tests pass:
   ```bash
   pytest
   ```
6. Run linting:
   ```bash
   ruff check .
   black .
   ```
7. Commit your changes with clear commit messages.
8. Push to your fork and open a pull request.

### Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **PEP 8** style guide

Configuration is in `pyproject.toml`.

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/easix.git
cd easix

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run example project
cd example
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Testing Guidelines

- Write tests for new features
- Maintain code coverage
- Test edge cases
- Use pytest fixtures for common setup

### Documentation

- Update README.md for new features
- Add docstrings to public APIs
- Include example code
- Update CHANGELOG.md

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Keep discussions on-topic

### Questions?

- Open a [discussion](https://github.com/easix-admin/easix/discussions)
- Join our community chat (coming soon)

---

Thank you for helping make Easix better! 🎉

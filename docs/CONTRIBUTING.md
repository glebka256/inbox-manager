# Contributing to Gmail Email Classifier

Thank you for your interest in contributing to the Gmail Email Classifier! This document provides guidelines for contributing to this project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project follows a standard code of conduct:
- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors
- Report any unacceptable behavior to the project maintainers

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/gmail-email-classifier.git
   cd gmail-email-classifier
   ```
3. **Set up the development environment** (see Development Setup below)
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

### Reporting Bugs
- Use the GitHub issue tracker
- Include a clear description of the problem
- Provide steps to reproduce the issue
- Include system information (OS, Python version, etc.)
- Attach relevant error messages or logs

### Suggesting Enhancements
- Use the GitHub issue tracker with the "enhancement" label
- Clearly describe the proposed feature
- Explain why this enhancement would be useful
- Consider providing examples or mockups

### Contributing Code
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Tests

## Development Setup

1. **Install Python 3.8+** if not already installed

2. **Set up virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Unix/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up test environment**:
   - Copy `.env.example` to `.env.test`
   - Use test Gmail credentials (create a dedicated test account)
   - Never use your personal Gmail account for testing

5. **Run tests** to ensure everything works:
   ```bash
   python -m pytest  # If pytest is set up
   # Or run individual test scripts
   python test_gmail_connection.py
   ```

## Coding Standards

### Python Style
- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for all functions and classes
- Keep line length under **88 characters** (Black formatter standard)

### Code Organization
- Keep functions small and focused
- Use meaningful variable and function names
- Add comments for complex logic
- Organize imports alphabetically within groups

### Example:
```python
"""Module for email classification functionality."""

import os
from typing import List, Dict, Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class EmailClassifier:
    """Classifies emails using machine learning techniques.
    
    Args:
        model_path: Path to the trained model file
        vectorizer_path: Path to the TF-IDF vectorizer
    """
    
    def __init__(self, model_path: str, vectorizer_path: str) -> None:
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.model: Optional[object] = None
        
    def predict(self, email_text: str) -> Dict[str, float]:
        """Predict email category and confidence.
        
        Args:
            email_text: The email content to classify
            
        Returns:
            Dictionary with prediction and confidence score
        """
        # Implementation here
        pass
```

## Testing

### Test Requirements
- All new features should include tests
- Bug fixes should include regression tests
- Maintain or improve test coverage

### Test Types
1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python test_gmail_connection.py

# Run with coverage
python -m pytest --cov=.
```

### Test Guidelines
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (Gmail API calls)
- Use test fixtures for common setup

## Submitting Changes

### Pull Request Process
1. **Update documentation** if needed
2. **Add or update tests** for your changes
3. **Ensure all tests pass**
4. **Update the README** if you've added features
5. **Create a pull request** with a clear description

### Pull Request Description
Include:
- **Summary** of changes
- **Motivation** for the changes
- **Testing** performed
- **Screenshots** (if UI changes)
- **Breaking changes** (if any)

### Example PR Description:
```markdown
## Summary
Add support for multiple Gmail accounts by extending the configuration system.

## Changes
- Extended .env configuration to support multiple accounts
- Updated EmailClassifier to handle account switching
- Added new command-line arguments for account selection

## Testing
- Added unit tests for multi-account configuration
- Tested with 3 different Gmail accounts
- Verified backward compatibility with single account setup

## Breaking Changes
None - fully backward compatible
```

### Code Review Process
- All submissions require review from project maintainers
- Address feedback promptly and professionally
- Be open to suggestions and improvements
- Update your PR based on review comments

## Documentation

### Documentation Guidelines
- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include code examples where helpful
- Update README.md for user-facing changes

### Documentation Types
- **README.md**: User documentation
- **Code comments**: Inline documentation
- **Docstrings**: API documentation
- **CHANGELOG.md**: Version history

## Release Process

### Version Numbers
- Follow [Semantic Versioning](https://semver.org/)
- Format: `MAJOR.MINOR.PATCH`
- Example: `1.2.3`

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Publish release notes

## Questions and Support

### Getting Help
- Check existing [GitHub Issues](https://github.com/your-username/gmail-email-classifier/issues)
- Create a new issue with the "question" label
- Join project discussions

### Contact
- **GitHub Issues**: For bug reports and feature requests
- **Email**: [your-email@example.com] for private inquiries
- **Discussions**: Use GitHub Discussions for general questions

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project. See [LICENSE](LICENSE) file for details.

---

Thank you for contributing to Gmail Email Classifier! 🚀
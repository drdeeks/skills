# Contributing to GitHub Repository Manager

Thank you for considering contributing to this skill! This document outlines the process for contributing.

## How to Contribute

### Reporting Issues
Please use the issue tracker to report bugs or suggest enhancements. Include:
- Clear description of the issue
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Relevant logs or error messages

### Suggesting Enhancements
Enhancement suggestions should include:
- Use case description
- Proposed solution
- Benefits and potential drawbacks
- Any relevant examples

### Submitting Changes
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Ensure all validations pass
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## Development Setup

### Prerequisites
- Python 3.8+
- GitHub API token (for testing)

### Installation
```bash
# Clone the skill
git clone <repository-url>
cd github-repo-manager

# No external dependencies required (uses Python stdlib only)
```

### Testing
Run the validation script to ensure everything works:
```bash
python3 validate_pro.py /path/to/skill --full
```

## Coding Standards

### Python Style
- Follow PEP 8 where applicable
- Use descriptive variable and function names
- Include docstrings for public functions
- Handle exceptions appropriately
- Use type hints where beneficial

### GitHub API Interaction
- Respect rate limits with exponential backoff
- Handle API errors gracefully
- Validate inputs before sending to API
- Log API interactions for debugging (without exposing tokens)

### Security Considerations
- Never log or expose GitHub tokens
- Validate all inputs to prevent injection
- Use environment variables for secrets
- Handle errors without exposing sensitive information

## License
This skill is released under the MIT License. See the LICENSE file for details.
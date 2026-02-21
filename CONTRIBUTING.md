# Contributing to HugPDF

Thank you for your interest in contributing to HugPDF! We welcome contributions from the community and are grateful for every bug report, feature request, and pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hugpdf.git
   cd hugpdf
   ```
3. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

---

## How to Contribute

### Reporting Bugs

Before filing a bug report, please:
- Check the [existing issues](https://github.com/sarathoff/hug-pdf/issues) to avoid duplicates
- Ensure you're using the latest version

When reporting a bug, include:
- **Description**: Clear description of the problem
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, browser version, Node.js/Python version
- **Screenshots**: If applicable

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Requesting Features

Feature requests are welcome! When submitting a feature request:
- Check if it's already been requested or implemented
- Provide a clear use case
- Explain why this feature would benefit the community

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Submitting Code

We accept contributions for:
- Bug fixes
- New features
- Documentation improvements
- Performance improvements
- Test coverage improvements
- UI/UX enhancements

---

## Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Fill in your API keys
```

### Frontend Setup

```bash
cd frontend
npm install

# Copy environment template
cp .env.example .env
# Set REACT_APP_BACKEND_URL=http://localhost:8000
```

### Running Locally

```bash
# Terminal 1: Start backend
cd backend
uvicorn server:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend
npm start
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features or bug fixes
3. **Ensure tests pass** locally before submitting
4. **Follow the style guidelines** (see below)
5. **Write a clear PR description** explaining:
   - What changes you made
   - Why you made them
   - How to test your changes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated for changed code
- [ ] Documentation updated if necessary
- [ ] No sensitive data (API keys, passwords) in the code
- [ ] PR title is descriptive and follows conventional commits format

### Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add new PDF generation mode
fix: resolve credit deduction bug
docs: update API documentation
style: format code with prettier
refactor: reorganize service layer
test: add unit tests for PDF service
chore: update dependencies
```

---

## Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints where possible
- Write docstrings for public functions
- Maximum line length: 120 characters

```python
# Good
async def generate_pdf(prompt: str, mode: str = "normal") -> bytes:
    """
    Generate a PDF document from a text prompt.

    Args:
        prompt: The text description for PDF generation
        mode: Generation mode ('normal', 'research', 'ebook')

    Returns:
        PDF file as bytes
    """
    ...
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Follow ESLint configuration in the project
- Use meaningful variable and function names
- Keep components focused and small

```jsx
// Good
const ApiKeyCard = ({ apiKey, onRevoke }) => {
  const handleRevoke = () => {
    if (window.confirm('Are you sure?')) {
      onRevoke(apiKey.id);
    }
  };

  return (
    <Card>
      <CardContent>
        <code>{apiKey.key_prefix}...</code>
        <Button onClick={handleRevoke}>Revoke</Button>
      </CardContent>
    </Card>
  );
};
```

---

## Questions?

If you have questions about contributing, feel free to:
- Open a [Discussion](https://github.com/sarathoff/hug-pdf/discussions)
- Email us at: contributors@hugpdf.app
- Join our [Discord](https://discord.gg/hugpdf)

Thank you for contributing to HugPDF! 🎉

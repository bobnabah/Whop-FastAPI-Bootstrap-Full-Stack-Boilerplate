# Contributing to Whop + FastAPI + Bootstrap Boilerplate

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/fastapi-fullstack-app.git
   cd fastapi-fullstack-app
   ```
3. **Set up the development environment** following the README instructions
4. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🎯 Types of Contributions

We welcome several types of contributions:

### 🐛 Bug Reports
- Use the GitHub issue tracker
- Include detailed steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include error messages and logs

### ✨ Feature Requests
- Open an issue to discuss the feature first
- Explain the use case and benefits
- Consider backward compatibility

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### 📚 Documentation
- README improvements
- Code comments
- API documentation
- Tutorial content

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

### Testing
- Add tests for new features
- Ensure existing tests pass
- Test webhook functionality thoroughly
- Include both unit and integration tests

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add PDF invoice generation
fix: resolve webhook signature verification issue
docs: update setup instructions
refactor: improve error handling in payment flow
```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update the README** if adding new features
5. **Create a pull request** with:
   - Clear title and description
   - Reference any related issues
   - Screenshots for UI changes
   - Testing instructions

## 🧪 Testing Your Changes

### Local Testing
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run the application
uvicorn main:app --reload

# Test webhook functionality
curl -X POST http://localhost:8000/api/admin/test-webhook
```

### Integration Testing
- Test with real Whop webhooks using ngrok
- Verify PDF generation works
- Test payment flow end-to-end
- Check admin dashboard functionality

## 🔒 Security Considerations

- Never commit real API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Report security issues privately

## 📝 Documentation Standards

- Update README.md for new features
- Add inline comments for complex logic
- Include docstrings for all functions
- Provide examples for new API endpoints

## 🎨 UI/UX Guidelines

- Maintain Bootstrap consistency
- Ensure responsive design
- Follow accessibility best practices
- Test on multiple browsers
- Keep the design clean and professional

## 🚫 What Not to Contribute

- Breaking changes without discussion
- Code that doesn't follow the project structure
- Features that significantly increase complexity
- Changes that break backward compatibility
- Proprietary or copyrighted code

## 📞 Getting Help

- Open an issue for questions
- Check existing issues and PRs
- Review the README and documentation
- Join community discussions

## 🏷️ Issue Labels

We use these labels to organize issues:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested

## 🎉 Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Credited in commit history

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make this boilerplate better for everyone! 🚀
# Contributing to Syntheverse

Thank you for your interest in contributing to Syntheverse! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ for backend development
- Node.js 18+ for frontend development
- Git for version control
- GROQ API key for AI evaluation features

### Development Setup
```bash
# Clone the repository
git clone https://github.com/FractiAI/Syntheverse.git
cd Syntheverse

# Set up Python environment
cd src/api/poc-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up Node.js environment
cd ../../frontend/poc-frontend
npm install

# Start development servers
cd ../../../scripts/development
./start_poc_ui.sh
```

## 📝 Contribution Types

### 🐛 Bug Reports
- Use GitHub Issues with the "bug" label
- Include detailed reproduction steps
- Provide system information and error logs
- Suggest potential fixes if possible

### 💡 Feature Requests
- Use GitHub Issues with the "enhancement" label
- Describe the problem you're trying to solve
- Provide mockups or examples if applicable
- Explain how this benefits the ecosystem

### 🔧 Code Contributions
- Fork the repository and create a feature branch
- Write clear, concise commit messages
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

### 📖 Documentation
- Improve existing documentation
- Add tutorials and guides
- Translate documentation to other languages
- Fix typos and improve clarity

## 🛠️ Development Guidelines

### Code Style
- **Python**: Follow PEP 8 with Black formatter
- **JavaScript/TypeScript**: Use ESLint and Prettier
- **Documentation**: Clear, concise, and accessible language

### Testing
- Write unit tests for new features
- Ensure existing tests still pass
- Test both happy path and error scenarios
- Include integration tests for API endpoints

### Commit Messages
```
feat: add new contribution evaluation algorithm
fix: resolve sandbox map rendering issue
docs: update API documentation for new endpoints
test: add integration tests for submission workflow
```

### Pull Requests
- Use descriptive titles and detailed descriptions
- Reference related issues with #issue-number
- Include screenshots for UI changes
- Ensure CI/CD checks pass
- Request review from maintainers

## 🎯 Areas for Contribution

### High Priority
- **AI Evaluation Improvements**: Enhance multi-metal classification accuracy
- **UI/UX Enhancements**: Improve contributor dashboard experience
- **Performance Optimization**: Speed up evaluation and rendering
- **Mobile Responsiveness**: Optimize for mobile devices

### Medium Priority
- **Additional Visualizations**: New ways to explore contribution relationships
- **API Documentation**: Complete OpenAPI specifications
- **Testing Coverage**: Increase automated test coverage
- **Error Handling**: Better error messages and recovery

### Future Opportunities
- **Plugin System**: Allow custom evaluation algorithms
- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Contribution impact assessment
- **Integration APIs**: Third-party service integrations

## 🔒 Security Considerations

- Never commit API keys or sensitive credentials
- Use environment variables for configuration
- Report security issues privately to maintainers
- Follow secure coding practices
- Validate all user inputs

## 📞 Getting Help

- **Documentation**: Check docs/ directory first
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: info@fractiai.com for direct support

## 🎉 Recognition

Contributors will be recognized in:
- Repository contributor list
- Release notes and changelogs
- Special acknowledgments for significant contributions
- Potential future governance participation

Thank you for contributing to Syntheverse! Your work helps advance the frontier of AI, crypto, and scientific discovery. 🚀

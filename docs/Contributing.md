# Contributing to IotaPlayer

Thank you for your interest in contributing to IotaPlayer! This guide will help you get started with contributing to the project.

## Getting Started

### Prerequisites
- **Python 3.13+** installed on your system
- **Git** for version control
- **Basic knowledge** of Python and PyQt6
- **Familiarity** with the project structure

### Development Setup
1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/IotaPlayer.git
   cd IotaPlayer
   ```
3. **Set up development environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Test the application:**
   ```bash
   python main.py
   ```

## Development Guidelines

### Code Style
- **Follow PEP 8** for Python code style
- **Use meaningful variable names** and clear comments
- **Write docstrings** for functions and classes
- **Keep functions focused** and reasonably sized
- **Use type hints** where appropriate

### Project Structure
```
IotaPlayer/
├── main.py              # Application entry point
├── config.py            # Configuration and version
├── core/                # Core application modules
│   ├── musicPlayer.py   # Main player window
│   ├── playlistMaker.py # Playlist management
│   ├── settingManager.py # Settings dialog
│   ├── discordIntegration.py # Discord Rich Presence
│   ├── google.py        # YouTube integration
│   └── ...              # Other core modules
├── utils/               # Utility modules
├── requirements.txt     # Python dependencies
└── docs/               # Documentation
```

### Git Workflow
1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** and test thoroughly
3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```
4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** on GitHub

## Areas for Contribution

### Features
- **New audio formats** support
- **Enhanced playlist features** (smart playlists, filters)
- **Additional integrations** (Spotify, Last.fm, etc.)
- **UI improvements** and accessibility features
- **Performance optimizations**

### Bug Fixes
- **Audio playback issues**
- **UI/UX problems**
- **Integration bugs** (Discord, YouTube)
- **Platform-specific issues**

### Documentation
- **Code documentation** and comments
- **User guide improvements**
- **API documentation**
- **Troubleshooting guides**

### Testing
- **Unit tests** for core functionality
- **Integration tests** for features
- **Manual testing** on different platforms
- **Performance testing**

## Development Process

### Before Starting
1. **Check existing issues** to avoid duplicates
2. **Discuss your idea** in an issue first
3. **Read the codebase** to understand the architecture
4. **Set up your development environment**

### During Development
1. **Follow the existing code style**
2. **Test your changes** thoroughly
3. **Update documentation** if needed
4. **Keep commits focused** and well-described

### Testing Your Changes
1. **Run the application** and test your feature
2. **Test on different platforms** if possible
3. **Check for regressions** in existing features
4. **Verify integrations** still work (Discord, YouTube)

### Submitting Changes
1. **Write a clear description** of your changes
2. **Include screenshots** for UI changes
3. **Mention related issues** if applicable
4. **Test your changes** one final time

## Code Review Process

### What We Look For
- **Code quality** and readability
- **Proper error handling**
- **Performance considerations**
- **Security implications**
- **Platform compatibility**

### Review Checklist
- [ ] Code follows project style guidelines
- [ ] Changes are well-tested
- [ ] Documentation is updated
- [ ] No breaking changes (unless intentional)
- [ ] Performance impact is considered
- [ ] Security implications are addressed

## Specific Contribution Areas

### Audio Engine
- **Codec support** improvements
- **Audio processing** enhancements
- **Cross-platform** audio compatibility
- **Performance optimizations**

### UI/UX Improvements
- **Accessibility** features
- **Theme system** enhancements
- **Responsive design** improvements
- **User experience** refinements

### Integrations
- **Discord Rich Presence** enhancements
- **YouTube integration** improvements
- **New service integrations**
- **API wrapper** improvements

### Platform Support
- **Windows-specific** optimizations
- **Linux desktop** integration
- **macOS support** (if needed)
- **Cross-platform** compatibility

## Getting Help

### Communication
- **GitHub Issues:** For bug reports and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Pull Request comments:** For code review feedback

### Resources
- **PyQt6 Documentation:** [Riverbank Computing](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- **Python Documentation:** [python.org](https://docs.python.org/)
- **Git Documentation:** [git-scm.com](https://git-scm.com/doc)

## Recognition

### Contributors
- **Your name** will be added to the contributors list
- **Significant contributions** will be acknowledged in release notes
- **Long-term contributors** may be invited to join the maintainer team

### Guidelines for Maintainers
- **Be respectful** and constructive in feedback
- **Provide clear guidance** for improvements
- **Recognize contributions** appropriately
- **Maintain project quality** and consistency

## Legal Considerations

### License
- **All contributions** are subject to the GNU GPL v3 license
- **Ensure you have rights** to contribute your code
- **Respect third-party licenses** and dependencies

### Code of Conduct
- **Be respectful** to all contributors
- **Welcome newcomers** and help them get started
- **Focus on constructive** feedback and discussion
- **Maintain a positive** and inclusive environment

---

**Ready to contribute?**
- [Installation](Installation) - Set up your development environment
- [User Guide](User-Guide) - Understand the application features
- [Configuration](Configuration) - Learn about the codebase structure

**Questions?** Feel free to open an issue or start a discussion on GitHub! 
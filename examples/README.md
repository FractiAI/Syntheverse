# Examples

This directory contains example scripts and demonstrations for the Syntheverse PoC system, plus an interactive menu system for easy access to all project functionality.

## Files

### Core Examples
- `demo_poc_system.py` - Complete demonstration of the PoC evaluation workflow (simulated)
- `demo_interface.html` - Static HTML demonstration of the full collaborator UI
- `test_ui.html` - Test interface for UI components with interactive elements

### Interactive Menu System
- `run.sh` - **NEW** Interactive text-based menu system providing unified access to all examples, tests, and scripts

## Interactive Menu System (`run.sh`)

The interactive menu system provides a centralized way to access all Syntheverse functionality:

### Features
- **Setup & Validation** - Check prerequisites (Python, Node.js, GROQ API key) and service health
- **Examples** - Run demo scripts and open HTML interfaces in browser
- **Tests** - Run comprehensive test suites with standardized reporting
- **Startup Scripts** - Launch system services and servers
- **Development Scripts** - Development workflow tools and utilities
- **Deployment Scripts** - Smart contract deployment
- **Utilities** - Maintenance and cleanup tools

### Usage
```bash
cd examples
./run.sh
```

Navigate through the menu system using numbered options. The menu provides:
- Colored status output (green=success, red=error, yellow=warning, blue=info)
- Path-aware execution (works from any directory)
- Error handling with helpful messages
- Service health checks before operations
- Comprehensive test execution with reporting

### Menu Structure

```
🌟 SYNTHVERSE INTERACTIVE MENU
=====================================
Project Root: /path/to/Syntheverse
Current Dir: /current/directory

Choose a category:
1) 🔧 Setup & Validation    - Check prerequisites and health
2) 📚 Examples              - Run demo scripts and view interfaces
3) 🧪 Tests                 - Run test suites and validation
4) 🚀 Startup Scripts       - Start system services
5) 💻 Development Scripts   - Development workflow tools
6) 📦 Deployment Scripts    - Deploy contracts and services
7) 🔧 Utilities             - Maintenance and cleanup tools
8) ❌ Exit
```

## Running Examples

### Python Demo
```bash
cd examples
python demo_poc_system.py
```

This demonstrates the PoC evaluation workflow with simulated data (no actual API calls).

### HTML Demos
Open the HTML files directly in a web browser to see static demonstrations of the interfaces:
- `demo_interface.html` - Shows PoC system interface design
- `test_ui.html` - Interactive test interface

You can also access these through the interactive menu (`./run.sh` → Examples).

## Port References

HTML examples reference:
- Frontend: http://localhost:3001 (Next.js PoC UI)
- API: http://localhost:5001 (PoC API)
- Legacy UI: http://localhost:5000 (Legacy Web UI)

## Prerequisites for Full Functionality

Before running examples or using the interactive menu, ensure:

1. **Python 3.8+** with required packages
2. **Node.js 18+** with dependencies installed
3. **GROQ API Key** set in environment
4. **System services running** (use menu option 4 to start)

The interactive menu will check these prerequisites and guide you through setup.

## Note

These examples are for demonstration purposes. The Python demo uses simulated data. For full functionality, the complete Syntheverse system must be running. Use the interactive menu system to easily start services and run comprehensive tests.

# Scripts

## Purpose

Scripts for development, deployment, startup, and maintenance of the Syntheverse system.

## Key Modules

### Main Menu (`main.py`)

Menu-based runner for all Syntheverse scripts.

**Class: `ScriptMenu`**

Provides an interactive terminal menu for executing scripts organized by category.

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__()` | None | None | Initialize paths, check dependencies, load categories |
| `check_dependencies_on_startup()` | None | None | Check and install dependencies |
| `clear_screen()` | None | None | Clear terminal (POSIX: clear, Windows: cls) |
| `print_header(title, subtitle)` | `title: str`, `subtitle: str` | None | Print formatted menu header |
| `print_menu(category)` | `category: str` | None | Print category menu with scripts |
| `print_main_menu()` | None | None | Print main category selection menu |
| `validate_script_exists(script_path)` | `script_path: str` | `bool` | Check if script file exists |
| `run_script(script_info)` | `script_info: Dict` | `bool` | Execute a script, return success status |
| `handle_category_menu(category)` | `category: str` | None | Interactive loop for category menu |
| `run()` | None | None | Main menu loop until quit |

**Function: `main()`**

Entry point that creates a ScriptMenu instance and runs it.

**Attributes:**

- `project_root`: Path to project root directory
- `scripts_dir`: Path to scripts directory
- `current_category`: Currently selected category (None at main menu)
- `categories`: Dictionary of script categories and their scripts

**Script Info Dictionary:**

```python
{
    "name": "script_name.py",       # Display name
    "description": "Description",    # Brief description
    "path": "category/script.py",   # Relative path from scripts/
    "type": "python",               # "python" or "shell"
    "args": ["--arg", "value"]      # Optional arguments
}
```

### Startup (`startup/`)

- **`start_servers.py`**: System startup with modes (full, poc, minimal)
- **`anvil_manager.py`**: Anvil blockchain node management
- **`port_manager.py`**: Port conflict resolution
- **`service_health.py`**: Service health monitoring

### Development (`development/`)

- **`manage_services.sh`**: Service manager (start/stop/status)

### Deployment (`deployment/`)

- **`deploy_contracts.py`**: Deploy SYNTH and POCRegistry contracts

### Utilities (`utilities/`)

- **`install_deps.py`**: Install system dependencies
- **`clear_state.py`**: Clear system state files

## Integration Points

- Scripts orchestrate multiple services
- Startup scripts manage service lifecycle
- Deployment scripts interact with blockchain
- Utility scripts maintain system state
- All paths resolve relative to project root

## Testing

Tests for `main.py` are in `tests/test_main_menu.py`:

- `TestScriptMenuInit`: Initialization and dependency checking
- `TestScriptValidation`: Script path validation
- `TestScriptExecution`: Script execution logic
- `TestMenuDisplay`: Output formatting methods
- `TestMenuNavigation`: Menu interaction and navigation
- `TestErrorHandling`: Error scenarios and recovery
- `TestPerformance`: Initialization and execution performance

Run tests:

```bash
pytest tests/test_main_menu.py -v
```

## Usage

```bash
# From project root
python scripts/main.py

# From scripts directory
cd scripts && python main.py
```

## Adding Scripts

Add to `self.categories` in `ScriptMenu.__init__()`:

```python
"category_name": {
    "title": "Category Title",
    "description": "Category description",
    "scripts": {
        "1": {
            "name": "script.py",
            "description": "Script description",
            "path": "category/script.py",
            "type": "python",
            "args": ["--option", "value"]
        }
    }
}
```

## Ports

| Service | Port |
|---------|------|
| PoC API | 5001 |
| RAG API | 8000 |
| Frontend | 3001 |

## Blueprint Alignment

### System Orchestration ([Blueprint §3.1](docs/Blueprint for Syntheverse))
- **PoC Pipeline Execution**: `startup/` scripts manage the complete submission → evaluation → registration → allocation workflow
- **Service Lifecycle**: `startup/start_servers.py` orchestrates multi-service startup with dependency management
- **Health Monitoring**: `startup/service_health.py` ensures system reliability and uptime

### Development Workflow ([Blueprint §7](docs/Blueprint for Syntheverse))
- **Local Development**: `startup/anvil_manager.py` provides local blockchain environment for development
- **Testing Integration**: `startup/port_manager.py` handles service coordination and conflict resolution
- **Deployment Automation**: `deployment/deploy_contracts.py` manages SYNTH and POCRegistry contract deployment

### Complete System Startup ([docs/START_WEB_UI.md](docs/START_WEB_UI.md))
- **Full System**: `startup/start_servers.py --mode full` starts all services (frontend, APIs, blockchain, Layer 2)
- **PoC Only**: `startup/start_servers.py --mode poc` starts core PoC evaluation pipeline
- **Minimal**: `startup/start_servers.py --mode minimal` starts essential services for development

### Service Management Integration
- **Dependency Management**: Scripts handle automatic installation and version compatibility
- **Environment Validation**: Pre-flight checks ensure all required components are available
- **Error Recovery**: Robust error handling and recovery mechanisms for production reliability

### Blueprint Implementation Support
- **Phase 1 Complete**: Core system startup and service orchestration fully implemented
- **Phase 2 Ready**: Deployment scripts support production environment setup
- **Development Workflow**: Complete local development environment with testing integration

## Cross-References

- **Blueprint Document**: [docs/Blueprint for Syntheverse](../docs/Blueprint for Syntheverse) - Central system vision
- **Implementation Status**: [docs/BLUEPRINT_IMPLEMENTATION_STATUS.md](../docs/BLUEPRINT_IMPLEMENTATION_STATUS.md)
- **System Startup**: [docs/START_WEB_UI.md](../docs/START_WEB_UI.md) - Complete startup guide
- **Quick Start**: [docs/QUICK_START_POC_UI.md](../docs/QUICK_START_POC_UI.md) - Getting started guide

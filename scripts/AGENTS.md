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

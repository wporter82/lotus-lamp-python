# Testing Guide

Complete guide for running and writing tests for Lotus Lamp.

## Quick Reference

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=lotus_lamp --cov-report=html

# Run specific test file
python -m pytest tests/test_config.py
```

**Current Status:** ✅ 90 tests passing | ⏭️ 4 skipped | 📈 32% coverage

## Installation

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

This installs:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-asyncio - Async test support
- black - Code formatting
- flake8 - Linting
- mypy - Type checking

## Running Tests

### Run All Tests

```bash
# Windows (if pytest not in PATH)
python -m pytest

# Linux/Mac (or if pytest is in PATH)
pytest
```

Output includes:
- Verbose test results (`-v`)
- Coverage report
- Color-coded output

### Run Specific Test File

```bash
python -m pytest tests/test_config.py
python -m pytest tests/test_modes.py
```

### Run Specific Test Class or Function

```bash
# Run specific test class
pytest tests/test_config.py::TestDeviceConfig

# Run specific test function
pytest tests/test_config.py::TestDeviceConfig::test_device_config_creation
```

### Run Tests by Marker

Tests are organized with markers (defined in [pytest.ini](pytest.ini)):

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run slow tests
python -m pytest -m slow

# Exclude slow tests
python -m pytest -m "not slow"
```

### Skip Integration Tests

Integration tests require BLE hardware or mocking infrastructure and are skipped by default:

```bash
# Run unit tests only (default behavior)
pytest -m "not integration"
```

## Coverage Reports

### Terminal Coverage

Coverage report is shown automatically after test run:

```
----------- coverage: platform win32, python 3.x -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
lotus_lamp/__init__.py               10      0   100%
lotus_lamp/config.py                 85      5    94%   123-127
lotus_lamp/modes.py                 150      0   100%
lotus_lamp/controller.py            200     25    88%   45-50, 78-82
---------------------------------------------------------------
TOTAL                               445     30    93%
```

### HTML Coverage Report

Detailed HTML report is generated in `htmlcov/`:

```bash
pytest
# Open htmlcov/index.html in browser
```

The HTML report shows:
- Line-by-line coverage
- Highlighted missing lines
- Per-file statistics
- Coverage trends

## Test Structure

### Test Files

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures
├── test_config.py           # Configuration tests
├── test_modes.py            # Mode management tests
├── test_controller.py       # Controller tests
├── test_scanner.py          # Scanner tests
└── test_advanced_scanner.py # Advanced scanner tests
```

### Fixtures (conftest.py)

Reusable test data and helpers:

```python
@pytest.fixture
def temp_dir():
    """Temporary directory for test files"""

@pytest.fixture
def sample_device_config():
    """Sample DeviceConfig object"""

@pytest.fixture
def sample_config_file(temp_dir):
    """Temporary config file with one device"""

@pytest.fixture
def multi_device_config_file(temp_dir):
    """Temporary config file with multiple devices"""
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from lotus_lamp import DeviceConfig

class TestYourFeature:
    """Test your feature"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        config = DeviceConfig(name="Test")

        # Act
        result = config.name

        # Assert
        assert result == "Test"
```

### Using Fixtures

```python
def test_with_config_file(sample_config_file):
    """Test using a fixture"""
    # sample_config_file is automatically created and cleaned up
    manager = ConfigManager(config_path=sample_config_file)
    assert len(manager.list_devices()) == 1
```

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await some_async_function()
    assert result is not None
```

### Testing Exceptions

```python
def test_raises_error():
    """Test that error is raised"""
    with pytest.raises(ValueError, match="expected error message"):
        raise_error_function()
```

### Capturing Output

```python
def test_print_output(capsys):
    """Test printed output"""
    print("Hello")
    captured = capsys.readouterr()
    assert "Hello" in captured.out
```

### Testing File Operations

```python
def test_file_creation(temp_dir):
    """Test file creation"""
    file_path = temp_dir / "test.json"
    file_path.write_text('{"test": true}')
    assert file_path.exists()
    # temp_dir automatically cleaned up
```

## Test Markers

Mark tests for organization:

```python
@pytest.mark.unit
def test_unit():
    """Unit test (no external dependencies)"""
    pass

@pytest.mark.integration
def test_integration():
    """Integration test (requires configuration)"""
    pass

@pytest.mark.slow
def test_slow():
    """Slow running test"""
    pass

@pytest.mark.requires_device
def test_with_device():
    """Test requiring physical device"""
    pass
```

## Coverage Goals

Target coverage levels:

- **Overall**: 90%+ coverage
- **Core modules** (config, modes, controller): 95%+ coverage
- **Scanner modules**: 80%+ coverage (some parts require hardware)
- **Examples**: Not covered by tests (manual testing)

### Checking Coverage

```bash
# Show missing lines
pytest --cov-report=term-missing

# Generate HTML report
pytest --cov-report=html

# Fail if coverage below threshold
pytest --cov-fail-under=90
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: pytest

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Best Practices

### Do's

✅ **Test one thing per test**
```python
def test_device_name():
    """Test getting device name"""
    config = DeviceConfig(name="Test")
    assert config.name == "Test"

def test_device_address():
    """Test getting device address"""
    config = DeviceConfig(address="AA:BB:CC:DD:EE:FF")
    assert config.address == "AA:BB:CC:DD:EE:FF"
```

✅ **Use descriptive test names**
```python
def test_config_manager_loads_from_valid_file():
    """Good: Clear what is being tested"""
    pass
```

✅ **Use fixtures for setup**
```python
@pytest.fixture
def configured_lamp(sample_device_config):
    """Fixture provides ready-to-use lamp"""
    return LotusLamp(device_config=sample_device_config)

def test_lamp_property(configured_lamp):
    """Test uses fixture"""
    assert configured_lamp.config.name == "Test Lamp"
```

✅ **Test error cases**
```python
def test_invalid_config_raises_error():
    """Test error handling"""
    with pytest.raises(FileNotFoundError):
        ConfigManager(config_path="nonexistent.json")
```

### Don'ts

❌ **Don't test multiple things**
```python
def test_everything():
    """Bad: Tests too many things"""
    config = DeviceConfig(name="Test")
    assert config.name == "Test"
    assert config.address is None
    assert config.service_uuid is not None
    # Too many assertions
```

❌ **Don't use vague names**
```python
def test_1():  # Bad
    pass

def test_config():  # Bad - what about config?
    pass
```

❌ **Don't leave tests skipped without reason**
```python
@pytest.mark.skip  # Bad - why skipped?
def test_something():
    pass

@pytest.mark.skip(reason="Requires BLE hardware")  # Good
def test_something():
    pass
```

## Troubleshooting Tests

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'lotus_lamp'`

**Solution**: Install package in development mode:
```bash
pip install -e .
```

### Async Test Errors

**Problem**: `RuntimeWarning: coroutine was never awaited`

**Solution**: Add `@pytest.mark.asyncio` decorator:
```python
@pytest.mark.asyncio
async def test_async():
    await some_async_function()
```

### Fixture Not Found

**Problem**: `fixture 'my_fixture' not found`

**Solution**: Ensure fixture is in `conftest.py` or imported properly:
```python
# In conftest.py
@pytest.fixture
def my_fixture():
    return "test data"
```

### Coverage Not Showing

**Problem**: Coverage report shows 0% or missing files

**Solution**: Check pytest.ini coverage settings:
```ini
[coverage:run]
source = lotus_lamp
```

## Adding New Tests

When adding new features:

1. **Create test file** if it doesn't exist:
   ```bash
   touch tests/test_your_feature.py
   ```

2. **Write tests first** (TDD approach):
   ```python
   def test_new_feature():
       """Test new feature"""
       # This will fail until feature is implemented
       assert new_feature() == expected_result
   ```

3. **Implement feature** until tests pass

4. **Check coverage**:
   ```bash
   pytest --cov=lotus_lamp.your_module
   ```

5. **Aim for 95%+ coverage** on new code

## See Also

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest.ini](pytest.ini) - Test configuration
- [conftest.py](tests/conftest.py) - Shared fixtures

"""
Comprehensive test suite for QRec backend. This package contains all tests for the backend application.

## Directory Structure
#### `conftest.py`
Configures fixtures for tests to utilize.

#### `api`
API endpoint tests (app, reports, verification, workers)

#### `integration` 
Integration tests (database connections, etc.)

#### `unit`
Unit tests organized by component:
- **components**: Feature-specific tests
    - **camera_verification**: Face ID, QR code, and error handling tests
    - **reports**: Report service tests
    - **utils**: Image utility tests
    - **workers**: Worker service tests
- **database**: Model tests

Run tests with: pytest
"""
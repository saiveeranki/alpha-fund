---
description: How to run the automated test suite
---
This workflow describes how to run the automated tests for both the backend and frontend.

### Prerequisites
- Python 3.10+
- Node.js 16+

### 1. Run Backend Tests
Run the following command from the root directory:
// turbo
```bash
python -m pytest tests/
```

### 2. Run Frontend Tests
Navigate to the `web` directory and run:
// turbo
```bash
cd web && npm test
```

### 3. Integrated CI
Note that these tests run automatically on GitHub for every push to the `master` branch.

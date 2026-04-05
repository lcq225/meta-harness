# Meta-Harness

> Agent Output Quality Evaluation and Experience Tracking System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-green.svg)](https://pypi.org/project/meta-harness/)

## Overview

Meta-Harness is an enterprise-grade Agent quality assurance system, based on the Stanford paper **Meta-Harness: End-to-End Optimization of Model Harnesses**.

### Core Features

| Feature | Description |
|---------|-------------|
| **Auto Evaluation** | Multi-dimensional scoring after each Agent output |
| **Experience Storage** | SQLite-based structured storage for all task executions |
| **Smart Indexing** | Auto-mark high/low score experiences |
| **Statistics** | Success rate, tool effectiveness analysis |

### Evaluation Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Correctness | 30% | Syntax, logic correctness |
| Completeness | 20% | Requirements coverage |
| Efficiency | 15% | Time/space complexity |
| Maintainability | 15% | Code structure |
| Security | 10% | No injection risks |
| Test Coverage | 10% | Has test cases |

## Installation

```bash
# PyPI (recommended)
pip install meta-harness

# From source
pip install .
```

## Quick Start

### 1. Evaluate Output

```python
from meta_harness import quick_evaluate

# Evaluate Agent output
result = quick_evaluate("Implement user login", login_code)

print(f"Score: {result.overall_score}")
print(f"Dimensions: {result.scores}")
print(f"Feedback: {result.feedback}")
```

### 2. Record Experience

```python
from meta_harness import ExperienceTracker

# Create tracker (auto-creates DB at ~/.meta_harness/)
tracker = ExperienceTracker()

# Record execution experience
record = tracker.record(
    task="Implement user login",
    output=login_code,
    evaluation={"overall_score": 85},
    tools_used=["code", "file_writer"],
    success=True,
    duration_seconds=30
)

print(f"Record ID: {record.id}")
```

### 3. Statistics

```python
# Get overall statistics
stats = tracker.get_stats(days=30)
print(f"Total: {stats['total']}")
print(f"Success Rate: {stats['success_rate']}%")
print(f"Average Score: {stats['avg_score']}")

# Tool effectiveness analysis
tool_stats = tracker.analyze_tool_effectiveness()
for tool, stat in tool_stats.items():
    print(f"{tool}: {stat['success_rate']} success rate")
```

## Advanced Features

### Batch Evaluation

```python
from meta_harness import batch_evaluate

pairs = [
    ("Task 1", "Output 1"),
    ("Task 2", "Output 2"),
    ("Task 3", "Output 3"),
]

results = batch_evaluate(pairs)
for r in results:
    print(f"{r.task}: {r.overall_score}")
```

### Experience Search

```python
# Search similar tasks
similar = tracker.search_similar("user auth", limit=5)
for r in similar:
    print(f"- {r.task} (score: {r.evaluation.get('overall_score', 'N/A')})")

# Get low score records (need improvement)
low_score = tracker.get_low_score_records(threshold=60)
```

### Data Export

```python
# Export to JSON
tracker.export_json("backup.json", days=30)

# Archive old records
tracker.archive_old(days=90)

# Cleanup (keep only recent 1000)
tracker.cleanup(keep_recent=1000)
```

## CoPaw Integration

For integration with CoPaw Agent framework, see [INTEGRATION.md](docs/INTEGRATION.md)

## Project Structure

```
meta-harness/
├── pyproject.toml
├── README.md           # English (this file)
├── README_zh.md        # 中文
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── src/
│   └── meta_harness/
│       ├── __init__.py
│       ├── evaluator/
│       └── tracker/
├── tests/
└── docs/
    └── INTEGRATION.md
```

## Dependencies

- Python >= 3.10
- SQLAlchemy >= 2.0

Optional:
- `memorycoreclaw` - For memory system integration

## License

[MIT License](LICENSE)

## Related Links

- [MemoryCoreClaw](https://github.com/lcq225/MemoryCoreClaw) - Human-like memory system
- [CoPaw](https://github.com/agentscope-ai/CoPaw) - Agent framework

---

⭐ If you find this useful, please star!
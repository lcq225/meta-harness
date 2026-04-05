# Meta-Harness

> Agent 输出质量评估与经验回溯系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/PyPI-v1.0.0-green.svg)](https://pypi.org/project/meta-harness/)

## 概述

Meta-Harness 是一个企业级 Agent 质量保障系统，基于斯坦福论文 **Meta-Harness: End-to-End Optimization of Model Harnesses** 理念实现。

### 核心功能

| 功能 | 说明 |
|------|------|
| **自动评估** | 每次 Agent 输出后多维度评分 |
| **经验存储** | SQLite 结构化存储所有任务执行 |
| **智能索引** | 高/低分经验自动标记 |
| **统计查询** | 成功率、工具效果分析 |

### 评估维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 正确性 | 30% | 语法、逻辑正确 |
| 完整性 | 20% | 覆盖需求 |
| 效率 | 15% | 时间/空间复杂度 |
| 可维护性 | 15% | 代码结构 |
| 安全性 | 10% | 无注入风险 |
| 测试覆盖 | 10% | 有测试用例 |

## 安装

```bash
# PyPI 安装（推荐）
pip install meta-harness

# 或从源码安装
pip install .
```

## 快速开始

### 1. 评估输出

```python
from meta_harness import quick_evaluate

# 评估 Agent 输出
result = quick_evaluate("实现用户登录功能", login_code)

print(f"总分: {result.overall_score}")
print(f"各维度分数: {result.scores}")
print(f"改进建议: {result.feedback}")
```

### 2. 记录经验

```python
from meta_harness import ExperienceTracker

# 创建追踪器（自动在 ~/.meta_harness/ 创建数据库）
tracker = ExperienceTracker()

# 记录执行经验
record = tracker.record(
    task="实现用户登录",
    output=login_code,
    evaluation={"overall_score": 85},
    tools_used=["code", "file_writer"],
    success=True,
    duration_seconds=30
)

print(f"记录ID: {record.id}")
```

### 3. 统计分析

```python
# 获取整体统计
stats = tracker.get_stats(days=30)
print(f"总任务数: {stats['total']}")
print(f"成功率: {stats['success_rate']}%")
print(f"平均分: {stats['avg_score']}")

# 工具效果分析
tool_stats = tracker.analyze_tool_effectiveness()
for tool, stat in tool_stats.items():
    print(f"{tool}: 成功率 {stat['success_rate']}")
```

## 高级功能

### 批量评估

```python
from meta_harness import batch_evaluate

pairs = [
    ("任务1", "输出1"),
    ("任务2", "输出2"),
    ("任务3", "输出3"),
]

results = batch_evaluate(pairs)
for r in results:
    print(f"{r.task}: {r.overall_score}")
```

### 经验搜索

```python
# 搜索相似任务
similar = tracker.search_similar("用户认证", limit=5)
for r in similar:
    print(f"- {r.task} (分数: {r.evaluation.get('overall_score', 'N/A')})")

# 获取低分记录（需要改进）
low_score = tracker.get_low_score_records(threshold=60)
```

### 数据导出

```python
# 导出为 JSON
tracker.export_json("backup.json", days=30)

# 归档旧记录
tracker.archive_old(days=90)

# 清理（只保留最近1000条）
tracker.cleanup(keep_recent=1000)
```

## CoPaw 集成

如需集成到 CoPaw Agent 框架，详见 [INTEGRATION.md](docs/INTEGRATION.md)

## 项目结构

```
meta-harness/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── meta_harness/
│       ├── __init__.py          # 包入口
│       ├── evaluator/           # 评估器
│       │   └── __init__.py
│       └── tracker/             # 经验追踪器
│           └── __init__.py
├── tests/
│   └── test_evaluator.py
└── docs/
    └── INTEGRATION.md
```

## 依赖

- Python >= 3.10
- SQLAlchemy >= 2.0

可选依赖：
- `memorycoreclaw` - 与记忆系统集成

## 许可证

[MIT License](LICENSE)

## 相关链接

- [MemoryCoreClaw](https://github.com/users/noreply/memorycoreclaw) - 类人脑记忆系统
- [CoPaw](https://github.com/agentscope-ai/CoPaw) - Agent 框架

---

⭐ 如果对你有帮助，欢迎 Star！
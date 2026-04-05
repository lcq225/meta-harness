# Meta-Harness CoPaw 集成指南

本文档说明如何将 Meta-Harness 集成到 CoPaw Agent 框架中。

## 概述

集成后实现自动：
1. 任务执行后评估输出质量
2. 记录到 SQLite 数据库  
3. 高价值经验索引到记忆系统

## 集成步骤

### 步骤1：安装 Meta-Harness

```bash
pip install meta-harness
# 或从本地安装
pip install /path/to/meta-harness
```

### 步骤2：创建集成模块

创建文件 `src/copaw/agents/harness_integration.py`：

```python
# -*- coding: utf-8 -*-
"""
Harness 自动集成模块
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# 全局配置
AUTO_EVALUATE_ENABLED = True
AUTO_RECORD_ENABLED = True
AUTO_INDEX_ENABLED = True
LOW_SCORE_THRESHOLD = 60
HIGH_SCORE_THRESHOLD = 80


class HarnessIntegration:
    def __init__(self, agent_name: str = "unknown"):
        self.agent_name = agent_name
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized:
            from meta_harness import quick_evaluate, ExperienceTracker
            from meta_harness.tracker import ExperienceTracker
            
            self.evaluator_func = quick_evaluate
            self.tracker = ExperienceTracker(
                db_path=".copaw/experiences.db"  # CoPaw 数据目录
            )
            self._initialized = True

    async def on_task_complete(self, task: str, output: Any, 
                               tools_used: list = None, context: Dict = None) -> Dict:
        """任务完成回调"""
        self._ensure_initialized()
        
        result = {"score": 0, "record_id": None, "suggestions": []}
        
        if not AUTO_EVALUATE_ENABLED and not AUTO_RECORD_ENABLED:
            return result

        output_str = str(output) if output else ""
        if not output_str or len(output_str) < 10:
            return result

        try:
            # 1. 评估
            if AUTO_EVALUATE_ENABLED:
                score = await self._evaluate(task, output_str)
                result["score"] = score

            # 2. 记录
            if AUTO_RECORD_ENABLED:
                record_id = await self._record(task, output_str, result["score"], tools_used, context)
                result["record_id"] = record_id

                # 3. 索引到 memory（可选）
                if AUTO_INDEX_ENABLED and result["score"] > 0:
                    await self._index_to_memory(task, result["score"], tools_used, record_id)

        except Exception as e:
            logger.warning(f"[Harness] Processing failed: {e}")

        return result

    async def _evaluate(self, task: str, output: str) -> float:
        try:
            eval_result = self.evaluator_func(task, output)
            return eval_result.overall_score
        except Exception as e:
            logger.warning(f"[Harness] Evaluate failed: {e}")
            return 0

    async def _record(self, task: str, output: str, score: float, 
                      tools_used: list, context: Dict) -> str:
        try:
            record = self.tracker.record(
                task=task, 
                output=output,
                evaluation={"overall_score": score} if score > 0 else None,
                tools_used=tools_used or [], 
                context=context or {}
            )
            return str(record.id)
        except Exception as e:
            logger.warning(f"[Harness] Record failed: {e}")
            return ""

    async def _index_to_memory(self, task: str, score: float, 
                               tools_used: list, record_id: str):
        """索引到记忆系统（可选，需要 memorycoreclaw）"""
        should_index = False
        importance = 0.6
        category = "experience"

        if score >= HIGH_SCORE_THRESHOLD:
            should_index = True
            importance = 0.8
            category = "success_experience"
        elif score < LOW_SCORE_THRESHOLD:
            should_index = True
            importance = 0.9
            category = "failure_lesson"

        if not should_index:
            return

        try:
            from memorycoreclaw import SafeMemory
            
            # 初始化记忆系统
            mem = SafeMemory()  # 使用默认路径
            
            tools_str = ", ".join(tools_used) if tools_used else "无"
            score_status = "成功" if score >= HIGH_SCORE_THRESHOLD else "失败"
            
            memory_content = f"任务: {task[:100]}... | 评估分数: {score} ({score_status}) | 使用工具: {tools_str} | 记录ID: {record_id}"
            
            mem.remember(memory_content, importance=importance, category=category, source="harness")
            
        except ImportError:
            logger.warning("[Harness] memorycoreclaw not installed, skipping memory index")
        except Exception as e:
            logger.warning(f"[Harness] Memory index failed: {e}")


# 便捷函数
def set_low_score_threshold(value: int):
    global LOW_SCORE_THRESHOLD
    LOW_SCORE_THRESHOLD = value

def set_high_score_threshold(value: int):
    global HIGH_SCORE_THRESHOLD
    HIGH_SCORE_THRESHOLD = value
```

### 步骤3：修改 tool_guard_mixin.py

在 `src/copaw/agents/tool_guard_mixin.py` 中：

1. 在文件顶部添加导入：
```python
from copaw.agents.harness_integration import HarnessIntegration
```

2. 在 `_init_tool_guard()` 方法中添加：
```python
if 'HarnessIntegration' in dir():
    self.harness = HarnessIntegration(agent_name=self.__class__.__name__)
```

3. 在 `_acting()` 方法末尾添加回调：
```python
if hasattr(self, 'harness'):
    await self.harness.on_task_complete(
        task=task_description,
        output=str(result),
        tools_used=[tool_name],
        context={"agent": self.__class__.__name__}
    )
```

### 步骤4：验证

```bash
python -c "from copaw.agents.tool_guard_mixin import ToolGuardMixin; print('Integration OK')"
```

## 配置选项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| AUTO_EVALUATE_ENABLED | True | 是否自动评估 |
| AUTO_RECORD_ENABLED | True | 是否自动记录 |
| AUTO_INDEX_ENABLED | True | 是否索引到 memory |
| LOW_SCORE_THRESHOLD | 60 | 低分阈值 |
| HIGH_SCORE_THRESHOLD | 80 | 高分阈值 |

修改方式：
```python
from copaw.agents.harness_integration import set_low_score_threshold
set_low_score_threshold(50)  # 改为50分
```

## 数据存储

- **experiences.db**: SQLite 数据库，位于 CoPaw 工作区
- **memory.db**: 记忆系统数据库（可选，需要 memorycoreclaw）

## 常见问题

### Q: 如何禁用自动评估？
```python
from copaw.agents.harness_integration import AUTO_EVALUATE_ENABLED
AUTO_EVALUATE_ENABLED = False
```

### Q: 如何只记录不评估？
```python
from copaw.agents.harness_integration import AUTO_EVALUATE_ENABLED
AUTO_EVALUATE_ENABLED = False  # 关闭评估
AUTO_RECORD_ENABLED = True     # 保持记录
```

### Q: 如何查看评估统计？
```python
from meta_harness import ExperienceTracker

tracker = ExperienceTracker()
stats = tracker.get_stats(days=30)
print(stats)
```
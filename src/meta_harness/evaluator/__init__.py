# -*- coding: utf-8 -*-
"""
Harness 评估器核心模块
"""
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class EvaluationResult:
    """评估结果"""
    task: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 各维度分数 (0-100)
    scores: Dict[str, float] = field(default_factory=dict)
    
    # 综合分数
    overall_score: float = 0.0
    
    # 问题列表
    issues: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # 改进建议
    feedback: List[str] = field(default_factory=list)
    
    # 原始输出
    output_length: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "task": self.task,
            "timestamp": self.timestamp,
            "scores": self.scores,
            "overall_score": self.overall_score,
            "issues": self.issues,
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "feedback": self.feedback,
            "output_length": self.output_length
        }


class HarnessEvaluator:
    """
    Harness 评估器
    
    多维度评估 Agent 输出质量
    """
    
    # 权重配置
    WEIGHTS = {
        "correctness": 0.30,
        "completeness": 0.20,
        "efficiency": 0.15,
        "maintainability": 0.15,
        "security": 0.10,
        "test_coverage": 0.10
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def evaluate(self, task: str, output: str, 
                 context: Optional[Dict] = None) -> EvaluationResult:
        """
        评估 Agent 输出
        
        Args:
            task: 任务描述
            output: Agent 输出内容
            context: 额外上下文信息
            
        Returns:
            EvaluationResult: 评估结果
        """
        context = context or {}
        
        result = EvaluationResult(task=task)
        result.output_length = len(output)
        
        # 1. 正确性评估
        result.scores["correctness"] = self._evaluate_correctness(
            task, output, context
        )
        
        # 2. 完整性评估
        result.scores["completeness"] = self._evaluate_completeness(
            task, output, context
        )
        
        # 3. 效率评估
        result.scores["efficiency"] = self._evaluate_efficiency(
            task, output, context
        )
        
        # 4. 可维护性评估
        result.scores["maintainability"] = self._evaluate_maintainability(
            task, output, context
        )
        
        # 5. 安全性评估
        result.scores["security"] = self._evaluate_security(
            task, output, context
        )
        
        # 6. 测试覆盖评估
        result.scores["test_coverage"] = self._evaluate_test_coverage(
            task, output, context
        )
        
        # 计算综合分数
        result.overall_score = self._calculate_overall(result.scores)
        
        # 生成反馈
        self._generate_feedback(result)
        
        return result
    
    def _evaluate_correctness(self, task: str, output: str, 
                              context: Dict) -> float:
        """评估正确性"""
        score = 70.0  # 基础分
        
        # 检查输出是否为空
        if not output or len(output.strip()) < 5:
            return 0.0
        
        # 检查基本语法错误（针对代码）
        if self._is_code_output(output):
            # 括号匹配
            if output.count('(') != output.count(')'):
                score -= 20
                result.critical_issues.append("括号不匹配")
            
            # 缩进检查
            lines = output.split('\n')
            indent_errors = sum(1 for line in lines[1:] 
                              if line.startswith(' ') and not line[1:].startswith(' '))
            if indent_errors > len(lines) * 0.3:
                score -= 10
        
        return max(0, min(100, score))
    
    def _evaluate_completeness(self, task: str, output: str,
                                context: Dict) -> float:
        """评估完整性"""
        score = 60.0
        
        # 检查任务关键词是否出现
        task_keywords = self._extract_keywords(task)
        matched = sum(1 for kw in task_keywords if kw.lower() in output.lower())
        
        if task_keywords:
            match_rate = matched / len(task_keywords)
            score = 60 + match_rate * 40
        
        # 检查输出长度是否合理
        if len(output) < 50:
            score = max(score - 20, 20)
        
        return max(0, min(100, score))
    
    def _evaluate_efficiency(self, task: str, output: str,
                             context: Dict) -> float:
        """评估效率"""
        score = 75.0
        
        # 代码效率检查
        if self._is_code_output(output):
            # 重复代码检测
            lines = [l.strip() for l in output.split('\n') if l.strip()]
            unique_lines = len(set(lines))
            if lines:
                repetition = 1 - (unique_lines / len(lines))
                if repetition > 0.5:
                    score -= 20
        
        return max(0, min(100, score))
    
    def _evaluate_maintainability(self, task: str, output: str,
                                   context: Dict) -> float:
        """评估可维护性"""
        score = 70.0
        
        if self._is_code_output(output):
            # 函数/方法数量
            func_count = output.count('def ') + output.count('function ')
            if func_count == 0:
                score -= 10
            
            # 注释率
            comment_lines = sum(1 for line in output.split('\n') 
                               if line.strip().startswith('#') or line.strip().startswith('//'))
            total_lines = len(output.split('\n'))
            if total_lines > 0:
                comment_rate = comment_lines / total_lines
                if comment_rate < 0.05:
                    score -= 15
                elif comment_rate > 0.3:
                    score += 10
        
        return max(0, min(100, score))
    
    def _evaluate_security(self, task: str, output: str,
                           context: Dict) -> float:
        """评估安全性"""
        score = 90.0
        
        # 检查危险模式
        dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'subprocess\s*\.\s*call\s*\(\s*[\'"]',
            r'os\s*\.\s*system\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                score -= 30
        
        return max(0, min(100, score))
    
    def _evaluate_test_coverage(self, task: str, output: str,
                                 context: Dict) -> float:
        """评估测试覆盖"""
        score = 50.0
        
        if self._is_code_output(output):
            # 检查是否有测试代码
            if 'test' in output.lower() or 'pytest' in output.lower():
                score += 30
            
            # 检查是否有断言
            if 'assert' in output.lower():
                score += 20
        
        return max(0, min(100, score))
    
    def _calculate_overall(self, scores: Dict[str, float]) -> float:
        """计算综合分数"""
        total = 0.0
        for dimension, weight in self.WEIGHTS.items():
            score = scores.get(dimension, 0)
            total += score * weight
        return round(total, 1)
    
    def _generate_feedback(self, result: EvaluationResult):
        """生成改进建议"""
        for dimension, score in result.scores.items():
            if score < 60:
                dimension_names = {
                    "correctness": "正确性",
                    "completeness": "完整性",
                    "efficiency": "效率",
                    "maintainability": "可维护性",
                    "security": "安全性",
                    "test_coverage": "测试覆盖"
                }
                result.feedback.append(
                    f"⚠️ {dimension_names.get(dimension, dimension)}偏低({score}分): 建议改进"
                )
        
        if result.overall_score >= 80:
            result.feedback.insert(0, "✅ 输出质量良好")
        elif result.overall_score >= 60:
            result.feedback.insert(0, "📝 输出质量一般，有改进空间")
        else:
            result.feedback.insert(0, "❌ 输出质量较差，需要重大改进")
    
    def _is_code_output(self, output: str) -> bool:
        """判断是否为代码输出"""
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', 'from ',
            'if ', 'else:', 'for ', 'while ', 'return ',
            'const ', 'let ', 'var ', '=>', '->',
            'public ', 'private ', 'protected '
        ]
        return any(indicator in output for indicator in code_indicators)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单提取：去除停用词后保留有意义的词
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                      'be', 'been', 'being', 'have', 'has', 'had',
                      'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'shall', 'can',
                      'to', 'of', 'in', 'for', 'on', 'with', 'at',
                      'by', 'from', 'as', 'into', 'through', 'during',
                      'and', 'or', 'but', 'not', 'no', 'that', 'this',
                      'it', 'which', 'what', 'how', 'when', 'where', 'why'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]


# 快速评估函数
def quick_evaluate(task: str, output: str) -> EvaluationResult:
    """
    快速评估（单函数调用）
    
    Args:
        task: 任务描述
        output: Agent 输出
        
    Returns:
        EvaluationResult: 评估结果
    """
    evaluator = HarnessEvaluator()
    return evaluator.evaluate(task, output)


# 批量评估
def batch_evaluate(task_output_pairs: List[tuple]) -> List[EvaluationResult]:
    """
    批量评估
    
    Args:
        task_output_pairs: [(task, output), ...]
        
    Returns:
        List[EvaluationResult]: 评估结果列表
    """
    evaluator = HarnessEvaluator()
    return [evaluator.evaluate(task, output) for task, output in task_output_pairs]
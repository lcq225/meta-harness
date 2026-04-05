# -*- coding: utf-8 -*-
"""测试 Meta-Harness 评估器"""

import pytest
from meta_harness import quick_evaluate, HarnessEvaluator


class TestEvaluator:
    """评估器测试"""
    
    def test_quick_evaluate_basic(self):
        """基本评估测试"""
        result = quick_evaluate("实现登录功能", "def login(): pass")
        
        assert result.overall_score > 0
        assert "correctness" in result.scores
        assert "completeness" in result.scores
    
    def test_quick_evaluate_empty_output(self):
        """空输出测试"""
        result = quick_evaluate("任务", "")
        
        # 空输出时正确性为0，但可能有其他维度基础分
        assert result.scores.get("correctness", 0) == 0
        assert result.overall_score < 50  # 空输出应该低分
    
    def test_quick_evaluate_with_code(self):
        """代码输出测试"""
        code = """
def calculate_sum(a, b):
    '''计算两个数的和'''
    return a + b

if __name__ == '__main__':
    print(calculate_sum(1, 2))
"""
        result = quick_evaluate("实现加法函数", code)
        
        assert result.overall_score > 0
        assert result.scores.get("correctness", 0) > 0
    
    def test_security_check(self):
        """安全检查测试"""
        dangerous_code = "eval(user_input)"
        
        result = quick_evaluate("处理用户输入", dangerous_code)
        
        # 危险代码应该降低安全性分数
        assert result.scores.get("security", 100) < 100
    
    def test_feedback_generation(self):
        """反馈生成测试"""
        result = quick_evaluate("任务", "short")
        
        assert len(result.feedback) > 0
    
    def test_task_type_detection(self):
        """任务类型检测"""
        # 代码任务
        code_result = quick_evaluate("实现函数", "def foo(): pass")
        assert "correctness" in code_result.scores
    
    def test_evaluator_with_config(self):
        """自定义配置测试"""
        evaluator = HarnessEvaluator()
        
        result = evaluator.evaluate(
            "测试任务",
            "test output",
            context={"key": "value"}
        )
        
        assert result.task == "测试任务"
        assert result.output_length > 0
    
    def test_dict_output(self):
        """字典输出测试"""
        result = quick_evaluate("返回字典", '{"key": "value"}')
        
        assert result.overall_score > 0


class TestEdgeCases:
    """边界情况测试"""
    
    def test_very_short_output(self):
        """超短输出"""
        result = quick_evaluate("任务", "a")
        
        assert result.overall_score >= 0
    
    def test_very_long_output(self):
        """超长输出"""
        long_output = "x" * 10000
        result = quick_evaluate("任务", long_output)
        
        assert result.output_length == 10000
    
    def test_unicode_content(self):
        """Unicode 内容"""
        result = quick_evaluate("测试中文", "print('你好世界')")
        
        assert result.overall_score >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
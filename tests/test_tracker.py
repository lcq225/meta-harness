# -*- coding: utf-8 -*-
"""测试 ExperienceTracker"""

import pytest
import tempfile
import os
from pathlib import Path
from meta_harness import ExperienceTracker


class TestExperienceTracker:
    """经验追踪器测试"""
    
    @pytest.fixture
    def tracker(self):
        """创建临时追踪器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield ExperienceTracker(db_path=db_path)
    
    def test_record_creation(self, tracker):
        """记录创建测试"""
        record = tracker.record(
            task="测试任务",
            output="测试输出",
            evaluation={"overall_score": 85}
        )
        
        assert record.id > 0
        assert record.task == "测试任务"
        assert record.success is True
    
    def test_get_record(self, tracker):
        """获取记录测试"""
        record = tracker.record(
            task="测试任务",
            output="测试输出"
        )
        
        retrieved = tracker.get_record(record.id)
        
        assert retrieved is not None
        assert retrieved.id == record.id
        assert retrieved.task == "测试任务"
    
    def test_search(self, tracker):
        """搜索测试"""
        # 创建多条记录
        for i in range(5):
            tracker.record(
                task=f"任务{i}",
                output=f"输出{i}",
                task_type="test"
            )
        
        results = tracker.search(task_type="test", limit=10)
        
        assert len(results) == 5
    
    def test_get_stats(self, tracker):
        """统计测试"""
        # 创建记录
        tracker.record(
            task="成功任务",
            output="输出",
            evaluation={"overall_score": 85},
            success=True
        )
        tracker.record(
            task="失败任务",
            output="输出",
            evaluation={"overall_score": 50},
            success=False
        )
        
        stats = tracker.get_stats(days=30)
        
        assert stats["total"] == 2
        assert stats["success_count"] == 1
    
    def test_task_type_stats(self, tracker):
        """任务类型统计"""
        tracker.record(task="任务1", output="输出", task_type="code")
        tracker.record(task="任务2", output="输出", task_type="code")
        tracker.record(task="任务3", output="输出", task_type="docs")
        
        types = tracker.get_task_types()
        
        assert types.get("code") == 2
        assert types.get("docs") == 1
    
    def test_tool_stats(self, tracker):
        """工具统计"""
        tracker.record(
            task="任务1",
            output="输出",
            tools_used=["code", "file_writer"],
            success=True
        )
        tracker.record(
            task="任务2", 
            output="输出",
            tools_used=["code"],
            success=False
        )
        
        tool_stats = tracker.analyze_tool_effectiveness()
        
        assert "code" in tool_stats
        assert tool_stats["code"]["total"] == 2
    
    def test_low_score_records(self, tracker):
        """低分记录"""
        tracker.record(
            task="低分任务",
            output="输出",
            evaluation={"overall_score": 50}
        )
        tracker.record(
            task="高分任务",
            output="输出", 
            evaluation={"overall_score": 90}
        )
        
        low = tracker.get_low_score_records(threshold=60)
        
        assert len(low) >= 1
    
    def test_search_similar(self, tracker):
        """相似搜索"""
        tracker.record(
            task="实现用户登录功能",
            output="代码"
        )
        tracker.record(
            task="实现用户注册",
            output="代码"
        )
        
        similar = tracker.search_similar("用户登录")
        
        assert len(similar) >= 1
    
    def test_export_json(self, tracker):
        """JSON 导出"""
        tracker.record(task="任务", output="输出")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            tracker.export_json(temp_path)
            
            import json
            with open(temp_path) as f:
                data = json.load(f)
            
            assert "records" in data
            assert data["count"] >= 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_cleanup(self, tracker):
        """清理测试"""
        # 创建超过限制的记录
        for i in range(15):
            tracker.record(task=f"任务{i}", output="输出")
        
        # 清理后只保留10条
        tracker.cleanup(keep_recent=10)
        
        stats = tracker.get_stats()
        
        assert stats["total"] <= 10


class TestEdgeCases:
    """边界情况"""
    
    def test_empty_task(self):
        """空任务"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExperienceTracker(db_path=os.path.join(tmpdir, "test.db"))
            record = tracker.record(task="", output="output")
            
            assert record.id > 0
    
    def test_special_characters(self):
        """特殊字符"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExperienceTracker(db_path=os.path.join(tmpdir, "test.db"))
            
            record = tracker.record(
                task="测试<>\"'",
                output="输出中文和emoji 🚀"
            )
            
            assert record.id > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
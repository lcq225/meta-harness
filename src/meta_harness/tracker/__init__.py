# -*- coding: utf-8 -*-
"""
经验回溯系统 v2.0 - SQLite 数据库存储

改进：
- 单文件 SQLite 数据库，高效存储和查询
- 自动归档旧数据
- 支持 SQL 查询分析
"""
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


@dataclass
class ExperienceRecord:
    """经验记录"""
    id: int = 0
    task: str = ""
    task_type: str = "general"
    timestamp: str = ""
    
    # 内容（JSON 字符串存储）
    input_data: str = "[]"
    output: str = ""
    
    # 评估（JSON 字符串存储）
    evaluation: str = "{}"
    
    # 元数据
    tools_used: str = "[]"
    context: str = "{}"
    success: bool = True
    duration_seconds: int = 0
    
    # 标签
    tags: str = "[]"
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ExperienceTracker:
    """
    经验回溯系统 v2.0
    
    使用 SQLite 数据库存储，支持高效查询和分析
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else self._get_default_db_path()
        self._init_db()
    
    def _get_default_db_path(self) -> Path:
        """获取默认数据库路径"""
        # 在用户目录下创建
        home = Path.home()
        meta_harness_dir = home / ".meta_harness"
        meta_harness_dir.mkdir(exist_ok=True)
        return meta_harness_dir / "experiences.db"
    
    @contextmanager
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库表"""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    task_type TEXT DEFAULT 'general',
                    timestamp TEXT NOT NULL,
                    input_data TEXT DEFAULT '[]',
                    output TEXT DEFAULT '',
                    evaluation TEXT DEFAULT '{}',
                    tools_used TEXT DEFAULT '[]',
                    context TEXT DEFAULT '{}',
                    success INTEGER DEFAULT 1,
                    duration_seconds INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '[]'
                )
            """)
            
            # 创建索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON experiences(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_type 
                ON experiences(task_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task 
                ON experiences(task)
            """)
            
            conn.commit()
    
    def record(
        self,
        task: str,
        output: str,
        task_type: str = "general",
        evaluation: Optional[Dict] = None,
        tools_used: Optional[List[str]] = None,
        context: Optional[Dict] = None,
        success: bool = True,
        duration_seconds: int = 0,
        tags: Optional[List[str]] = None
    ) -> ExperienceRecord:
        """
        记录经验
        
        Args:
            task: 任务描述
            output: 输出内容
            task_type: 任务类型
            evaluation: 评估结果
            tools_used: 使用的工具
            context: 上下文信息
            success: 是否成功
            duration_seconds: 执行耗时（秒）
            tags: 标签列表
            
        Returns:
            ExperienceRecord: 记录对象
        """
        evaluation = evaluation or {}
        tools_used = tools_used or []
        context = context or {}
        tags = tags or []
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO experiences (
                    task, task_type, timestamp, input_data, output,
                    evaluation, tools_used, context, success, duration_seconds, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task,
                task_type,
                datetime.now().isoformat(),
                "[]",  # input_data
                output,
                json.dumps(evaluation, ensure_ascii=False),
                json.dumps(tools_used, ensure_ascii=False),
                json.dumps(context, ensure_ascii=False),
                1 if success else 0,
                duration_seconds,
                json.dumps(tags, ensure_ascii=False)
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            
            return ExperienceRecord(
                id=record_id,
                task=task,
                task_type=task_type,
                timestamp=datetime.now().isoformat(),
                output=output,
                evaluation=json.dumps(evaluation, ensure_ascii=False),
                tools_used=json.dumps(tools_used, ensure_ascii=False),
                context=json.dumps(context, ensure_ascii=False),
                success=success,
                duration_seconds=duration_seconds,
                tags=json.dumps(tags, ensure_ascii=False)
            )
    
    def get_record(self, record_id: int) -> Optional[ExperienceRecord]:
        """获取单条记录"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM experiences WHERE id = ?",
                (record_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_record(row)
    
    def search(
        self,
        task_type: Optional[str] = None,
        success: Optional[bool] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        days: int = 30,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExperienceRecord]:
        """
        搜索经验
        
        Args:
            task_type: 任务类型过滤
            success: 成功状态过滤
            min_score: 最低分数
            max_score: 最高分数
            days: 最近天数
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[ExperienceRecord]: 记录列表
        """
        query = "SELECT * FROM experiences WHERE timestamp >= ?"
        params = [(datetime.now() - timedelta(days=days)).isoformat()]
        
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type)
        
        if success is not None:
            query += " AND success = ?"
            params.append(1 if success else 0)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit * 2)  # 多取一些，后面过滤
        
        with self._get_conn() as conn:
            cursor = conn.execute(query, params)
            records = [self._row_to_record(row) for row in cursor.fetchall()]
        
        # Python 级别过滤分数
        filtered = []
        for record in records:
            try:
                eval_data = json.loads(record.evaluation)
                score = eval_data.get("overall_score", 0)
                
                if min_score is not None and score < min_score:
                    continue
                if max_score is not None and score > max_score:
                    continue
                    
                filtered.append(record)
            except:
                if min_score is None and max_score is None:
                    filtered.append(record)
        
        # 分页
        return filtered[offset:offset + limit]
    
    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        获取统计数据
        
        Args:
            days: 统计天数
            
        Returns:
            Dict: 统计数据
        """
        with self._get_conn() as conn:
            # 总体统计
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    AVG(duration_seconds) as avg_duration
                FROM experiences 
                WHERE timestamp >= ?
            """, [(datetime.now() - timedelta(days=days)).isoformat()])
            
            row = cursor.fetchone()
            
            total = row["total"] or 0
            success_count = row["success_count"] or 0
            avg_duration = row["avg_duration"] or 0
            success_rate = (success_count / total * 100) if total > 0 else 0
            
            # 分数统计（使用正则提取）
            cursor2 = conn.execute("""
                SELECT evaluation FROM experiences 
                WHERE timestamp >= ?
            """, [(datetime.now() - timedelta(days=days)).isoformat()])
            
            scores = []
            for row2 in cursor2.fetchall():
                try:
                    eval_data = json.loads(row2["evaluation"])
                    if "overall_score" in eval_data:
                        scores.append(eval_data["overall_score"])
                except:
                    pass
            
            avg_score = sum(scores) / len(scores) if scores else 0
            
            return {
                "total": total,
                "success_count": success_count,
                "success_rate": round(success_rate, 1),
                "avg_score": round(avg_score, 1),
                "avg_duration": round(avg_duration, 1)
            }
    
    def get_task_types(self, days: int = 30) -> Dict[str, int]:
        """获取任务类型统计"""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT task_type, COUNT(*) as count
                FROM experiences
                WHERE timestamp >= ?
                GROUP BY task_type
                ORDER BY count DESC
            """, [(datetime.now() - timedelta(days=days)).isoformat()])
            
            return {row["task_type"]: row["count"] for row in cursor.fetchall()}
    
    def get_tool_stats(self, days: int = 30) -> Dict[str, Dict[str, int]]:
        """获取工具使用统计"""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT tools_used, success, COUNT(*) as count
                FROM experiences
                WHERE timestamp >= ?
                GROUP BY tools_used, success
            """, [(datetime.now() - timedelta(days=days)).isoformat()])
            
            tool_stats = {}
            for row in cursor.fetchall():
                try:
                    tools = json.loads(row["tools_used"])
                    for tool in tools:
                        if tool not in tool_stats:
                            tool_stats[tool] = {"success": 0, "total": 0}
                        tool_stats[tool]["total"] += row["count"]
                        if row["success"]:
                            tool_stats[tool]["success"] += row["count"]
                except:
                    pass
            
            # 计算成功率
            for tool, stats in tool_stats.items():
                rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
                stats["success_rate"] = f"{rate:.1f}%"
            
            return tool_stats
    
    def get_low_score_records(self, threshold: float = 60, 
                               days: int = 30) -> List[ExperienceRecord]:
        """获取低分记录"""
        return self.search(min_score=0, max_score=threshold, days=days)
    
    def get_high_score_records(self, threshold: float = 80,
                               days: int = 30) -> List[ExperienceRecord]:
        """获取高分记录"""
        return self.search(min_score=threshold, max_score=100, days=days)
    
    def export_json(self, filepath: str, days: int = 30):
        """导出为 JSON"""
        records = self.search(days=days, limit=10000)
        
        data = {
            "export_time": datetime.now().isoformat(),
            "days": days,
            "count": len(records),
            "records": [
                {
                    "id": r.id,
                    "task": r.task,
                    "task_type": r.task_type,
                    "timestamp": r.timestamp,
                    "success": r.success,
                    "evaluation": json.loads(r.evaluation),
                    "tools_used": json.loads(r.tools_used),
                    "duration_seconds": r.duration_seconds
                }
                for r in records
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def archive_old(self, days: int = 90):
        """归档旧记录（保留统计，删除详情）"""
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE experiences
                SET output = '[archived]', input_data = '[]'
                WHERE timestamp < ?
            """, [(datetime.now() - timedelta(days=days)).isoformat()])
            conn.commit()
    
    def cleanup(self, keep_recent: int = 1000):
        """清理旧记录，只保留最近 N 条"""
        with self._get_conn() as conn:
            conn.execute("""
                DELETE FROM experiences
                WHERE id NOT IN (
                    SELECT id FROM experiences
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            """, [keep_recent])
            conn.commit()
    
    def analyze_tool_effectiveness(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """分析工具效果"""
        return self.get_tool_stats(days)
    
    def _row_to_record(self, row) -> ExperienceRecord:
        """将数据库行转换为记录对象"""
        return ExperienceRecord(
            id=row["id"],
            task=row["task"],
            task_type=row["task_type"],
            timestamp=row["timestamp"],
            input_data=row["input_data"],
            output=row["output"],
            evaluation=row["evaluation"],
            tools_used=row["tools_used"],
            context=row["context"],
            success=bool(row["success"]),
            duration_seconds=row["duration_seconds"],
            tags=row["tags"]
        )
    
    def search_similar(self, task: str, limit: int = 5) -> List[ExperienceRecord]:
        """搜索相似任务（简单关键词匹配）"""
        keywords = task.lower().split()
        
        if not keywords:
            return []
        
        query = "SELECT * FROM experiences WHERE "
        conditions = []
        params = []
        
        for kw in keywords[:5]:  # 最多5个关键词
            conditions.append("task LIKE ?")
            params.append(f"%{kw}%")
        
        query += " OR ".join(conditions)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self._get_conn() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_record(row) for row in cursor.fetchall()]
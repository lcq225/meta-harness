# -*- coding: utf-8 -*-
"""
Meta-Harness 周报生成脚本

Usage:
    python weekly_report.py              # 中文（默认）
    python weekly_report.py --lang en    # English
    
    # 保存到文件
    python weekly_report.py --output report.txt
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from meta_harness import ExperienceTracker


# 中文报告模板
def generate_chinese_report(stats, task_types, tool_stats, low_records, high_records, days):
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    # Score evaluation
    if stats['avg_score'] >= 80:
        score_emoji = "🟢"
        score_comment = "表现优秀！"
    elif stats['avg_score'] >= 60:
        score_emoji = "🟡"
        score_comment = "良好，有提升空间"
    else:
        score_emoji = "🔴"
        score_comment = "需要关注"
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                 META-HARNESS 质量周报                        ║
╚══════════════════════════════════════════════════════════════╝

📅 统计周期: {start_date.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}
📊 生成时间: {today.strftime('%Y-%m-%d %H:%M:%S')}

{'─' * 62}
📈 整体统计
{'─' * 62}

  总任务数:      {stats['total']}
  成功率:       {stats['success_rate']}%  {score_emoji}
  平均分数:      {stats['avg_score']}  {score_comment}
  平均耗时:      {stats['avg_duration']}秒

{'─' * 62}
📁 任务类型分布
{'─' * 62}
"""
    
    if task_types:
        for task_type, count in sorted(task_types.items(), key=lambda x: x[1], reverse=True):
            report += f"  {task_type:20s} : {count:3d} 个任务\n"
    else:
        report += "  暂无数据\n"
    
    report += f"""
{'─' * 62}
🔧 工具使用统计
{'─' * 62}
"""
    
    if tool_stats:
        for tool, stat in sorted(tool_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
            rate = stat['success_rate']
            report += f"  {tool:20s} : {stat['total']:3d} 次调用, {stat['success']:3d} 成功 ({rate})\n"
    else:
        report += "  暂无数据\n"
    
    report += f"""
{'─' * 62}
🏆 高分任务 (>= 80分)
{'─' * 62}
"""
    
    if high_records:
        for record in high_records[:5]:
            try:
                eval_data = json.loads(record.evaluation)
                score = eval_data.get('overall_score', 'N/A')
            except:
                score = 'N/A'
            task_short = record.task[:50] + '...' if len(record.task) > 50 else record.task
            report += f"  [{score}分] {task_short}\n"
    else:
        report += "  本周暂无高分任务\n"
    
    report += f"""
{'─' * 62}
⚠️  低分任务 (< 60分) - 需要改进
{'─' * 62}
"""
    
    if low_records:
        for record in low_records[:5]:
            try:
                eval_data = json.loads(record.evaluation)
                score = eval_data.get('overall_score', 'N/A')
            except:
                score = 'N/A'
            task_short = record.task[:50] + '...' if len(record.task) > 50 else record.task
            report += f"  [{score}分] {task_short}\n"
    else:
        report += "  本周没有低分任务！做得很棒！🎉\n"
    
    report += f"""
{'─' * 62}
💡 改进建议
{'─' * 62}
"""
    
    recommendations = []
    
    if stats['success_rate'] < 70:
        recommendations.append("⚠️ 成功率低于 70%，建议回顾失败任务")
    
    if stats['avg_score'] < 60:
        recommendations.append("⚠️ 平均分低于 60，需要关注输出质量")
    
    if low_records:
        recommendations.append(f"📝 查看 {len(low_records)} 个低分任务，了解问题原因")
    
    if not recommendations:
        recommendations.append("✅ 一切正常！继续保持！")
    
    for rec in recommendations:
        report += f"  {rec}\n"
    
    report += f"""
╚══════════════════════════════════════════════════════════════╝

📊 数据位置: D:\\CoPaw\\.copaw\\experiences.db

由 Meta-Harness 自动生成
"""
    return report


# 英文报告模板
def generate_english_report(stats, task_types, tool_stats, low_records, high_records, days):
    today = datetime.now()
    start_date = today - timedelta(days=days)
    
    if stats['avg_score'] >= 80:
        score_emoji = "🟢"
        score_comment = "Excellent performance!"
    elif stats['avg_score'] >= 60:
        score_emoji = "🟡"
        score_comment = "Good, room for improvement"
    else:
        score_emoji = "🔴"
        score_comment = "Needs attention"
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║            META-HARNESS WEEKLY QUALITY REPORT               ║
╚══════════════════════════════════════════════════════════════╝

📅 Period: {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}
📊 Generated: {today.strftime('%Y-%m-%d %H:%M:%S')}

{'─' * 62}
📈 OVERALL STATISTICS
{'─' * 62}

  Total Tasks:     {stats['total']}
  Success Rate:    {stats['success_rate']}%  {score_emoji}
  Average Score:   {stats['avg_score']}  {score_comment}
  Avg Duration:    {stats['avg_duration']}s

{'─' * 62}
📁 TASK TYPES
{'─' * 62}
"""
    
    if task_types:
        for task_type, count in sorted(task_types.items(), key=lambda x: x[1], reverse=True):
            report += f"  {task_type:20s} : {count:3d} tasks\n"
    else:
        report += "  No task data\n"
    
    report += f"""
{'─' * 62}
🔧 TOOL EFFECTIVENESS
{'─' * 62}
"""
    
    if tool_stats:
        for tool, stat in sorted(tool_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
            rate = stat['success_rate']
            report += f"  {tool:20s} : {stat['total']:3d} calls, {stat['success']:3d} success ({rate})\n"
    else:
        report += "  No tool data\n"
    
    report += f"""
{'─' * 62}
🏆 HIGH SCORE TASKS (>= 80)
{'─' * 62}
"""
    
    if high_records:
        for record in high_records[:5]:
            try:
                eval_data = json.loads(record.evaluation)
                score = eval_data.get('overall_score', 'N/A')
            except:
                score = 'N/A'
            task_short = record.task[:50] + '...' if len(record.task) > 50 else record.task
            report += f"  [{score}] {task_short}\n"
    else:
        report += "  No high score tasks this week\n"
    
    report += f"""
{'─' * 62}
⚠️  LOW SCORE TASKS (< 60) - NEEDS IMPROVEMENT
{'─' * 62}
"""
    
    if low_records:
        for record in low_records[:5]:
            try:
                eval_data = json.loads(record.evaluation)
                score = eval_data.get('overall_score', 'N/A')
            except:
                score = 'N/A'
            task_short = record.task[:50] + '...' if len(record.task) > 50 else record.task
            report += f"  [{score}] {task_short}\n"
    else:
        report += "  No low score tasks this week - Great job! 🎉\n"
    
    report += f"""
{'─' * 62}
💡 RECOMMENDATIONS
{'─' * 62}
"""
    
    recommendations = []
    
    if stats['success_rate'] < 70:
        recommendations.append("⚠️ Success rate below 70% - consider reviewing failed tasks")
    
    if stats['avg_score'] < 60:
        recommendations.append("⚠️ Average score below 60 - output quality needs attention")
    
    if low_records:
        recommendations.append(f"📝 Review {len(low_records)} low-score tasks for improvement")
    
    if not recommendations:
        recommendations.append("✅ Everything looks good! Keep up the great work!")
    
    for rec in recommendations:
        report += f"  {rec}\n"
    
    report += f"""
╚══════════════════════════════════════════════════════════════╝

📊 Full data available in: experiences.db

Generated by Meta-Harness - Agent Quality Assurance System
"""
    return report


def generate_weekly_report(
    db_path: str = None,
    days: int = 7,
    output_file: str = None,
    lang: str = "zh"  # 默认中文
) -> str:
    """
    生成周报
    
    Args:
        db_path: experiences.db 路径
        days: 统计天数
        output_file: 保存到文件
        lang: 语言 "zh"=中文, "en"=英文
        
    Returns:
        报告文本
    """
    # Default CoPaw location
    if db_path is None:
        db_path = r"D:\CoPaw\.copaw\experiences.db"
    
    tracker = ExperienceTracker(db_path=db_path)
    
    stats = tracker.get_stats(days=days)
    task_types = tracker.get_task_types(days=days)
    tool_stats = tracker.analyze_tool_effectiveness(days=days)
    low_records = tracker.get_low_score_records(threshold=60, days=days)
    high_records = tracker.get_high_score_records(threshold=80, days=days)
    
    # Generate report based on language
    if lang == "en":
        report = generate_english_report(stats, task_types, tool_stats, low_records, high_records, days)
    else:
        report = generate_chinese_report(stats, task_types, tool_stats, low_records, high_records, days)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {output_file}")
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Meta-Harness 周报生成器")
    parser.add_argument("--days", type=int, default=7, help="统计天数")
    parser.add_argument("--db", type=str, help="experiences.db 路径")
    parser.add_argument("--output", type=str, help="保存报告到文件")
    parser.add_argument("--lang", type=str, choices=["zh", "en"], default="zh", 
                       help="语言: zh=中文, en=English")
    parser.add_argument("--quiet", action="store_true", help="不打印，只保存")
    
    args = parser.parse_args()
    
    report = generate_weekly_report(
        db_path=args.db,
        days=args.days,
        output_file=args.output,
        lang=args.lang
    )
    
    if not args.quiet:
        print(report)
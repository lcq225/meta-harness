import sqlite3
import json

conn = sqlite3.connect(r'D:\CoPaw\.copaw\experiences.db')
cur = conn.execute('SELECT task, evaluation, timestamp FROM experiences ORDER BY id DESC LIMIT 5')

print("=== 最近自动记录的任务 ===\n")
for row in cur:
    eval_data = json.loads(row[1]) if row[1] else {}
    score = eval_data.get('overall_score', 'N/A')
    task_short = row[0][:60] + '...' if len(row[0]) > 60 else row[0]
    print(f"任务: {task_short}")
    print(f"分数: {score}")
    print(f"时间: {row[2][:19]}")
    print("-" * 40)

conn.close()
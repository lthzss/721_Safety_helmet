from pathlib import Path
import sqlite3

# ========== 1. 项目根目录 ==========
project_root = Path(__file__).resolve().parent.parent

# ========== 2. 数据库目录与文件 ==========
db_dir = project_root / "database"
db_dir.mkdir(parents=True, exist_ok=True)

db_path = db_dir / "obu_sim.db"

print("数据库文件路径：", db_path)

# ========== 3. 连接数据库 ==========
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ========== 4. 创建 OBU 信息表 ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS obu_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obu_id TEXT NOT NULL UNIQUE,
    registered_class TEXT NOT NULL,
    note TEXT
)
""")

# ========== 5. 清空旧数据（为了避免重复插入，初始化阶段先这样做） ==========
cursor.execute("DELETE FROM obu_info")

# ========== 6. 插入模拟数据 ==========
sample_data = [
    ("OBU0001", "axle2", "两轴货车"),
    ("OBU0002", "axle2", "两轴货车"),
    ("OBU0003", "axle3", "三轴货车"),
    ("OBU0004", "axle3", "三轴货车"),
    ("OBU0005", "axle4", "四轴货车"),
    ("OBU0006", "axle4", "四轴货车"),
    ("OBU0007", "axle5", "五轴货车"),
    ("OBU0008", "axle5", "五轴货车"),
    ("OBU0009", "non_truck", "非卡车"),
    ("OBU0010", "non_truck", "非卡车")
]

cursor.executemany("""
INSERT INTO obu_info (obu_id, registered_class, note)
VALUES (?, ?, ?)
""", sample_data)

# ========== 7. 提交并关闭 ==========
conn.commit()

# ========== 8. 打印结果 ==========
cursor.execute("SELECT COUNT(*) FROM obu_info")
count = cursor.fetchone()[0]

print(f"初始化完成！当前 obu_info 表共有 {count} 条记录。")

cursor.execute("SELECT * FROM obu_info")
rows = cursor.fetchall()

print("\n当前数据如下：")
for row in rows:
    print(row)

conn.close()
print("\n数据库已创建并关闭。")
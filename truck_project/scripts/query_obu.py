from pathlib import Path
import sqlite3

# ========== 1. 项目根目录 ==========
project_root = Path(__file__).resolve().parent.parent

# ========== 2. 数据库路径 ==========
db_path = project_root / "database" / "obu_sim.db"

print("当前数据库路径：", db_path)

# ========== 3. 检查数据库文件是否存在 ==========
if not db_path.exists():
    raise FileNotFoundError(f"数据库文件不存在：{db_path}")

# ========== 4. 连接数据库 ==========
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ========== 5. 用户输入 OBU 编号 ==========
obu_id = input("请输入 OBU 编号：").strip()

# ========== 6. 查询数据库 ==========
cursor.execute("""
SELECT obu_id, registered_class, note
FROM obu_info
WHERE obu_id = ?
""", (obu_id,))

result = cursor.fetchone()

# ========== 7. 输出结果 ==========
if result is None:
    print("\n未找到该 OBU 编号，请检查输入是否正确。")
else:
    print("\n查询成功！")
    print("OBU 编号：", result[0])
    print("登记类别：", result[1])
    print("备注信息：", result[2])

# ========== 8. 关闭数据库 ==========
conn.close()
print("\n数据库连接已关闭。")
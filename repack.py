"""
Armello 汉化补丁打包脚本
将修改后的 SimplifiedChinese.csv 重新写回 resources.assets

使用方法：
  1. 修改翻译后将文件另存为 SimplifiedChinese_modified.csv（放在本项目目录下）
  2. 运行本脚本：python repack.py
  3. 脚本会自动备份并替换游戏目录中的 resources.assets

注意事项：
  - 首次运行会自动备份原文件为 resources.assets.backup
  - 如果游戏更新，需要重新提取
"""

import UnityPy
import shutil
import os

# ============ 路径配置 ============
# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 游戏目录中的 resources.assets
GAME_ASSETS = "D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets"
# 修改后的 CSV 文件（pipeline.py export 产物优先）
EXPORT_CSV = os.path.join(PROJECT_ROOT, "SimplifiedChinese_export.csv")
MODIFIED_CSV = EXPORT_CSV if os.path.exists(EXPORT_CSV) else os.path.join(PROJECT_ROOT, "SimplifiedChinese_modified.csv")
# 原始提取的 CSV（用于对照/测试）
FALLBACK_CSV = os.path.join(PROJECT_ROOT, "SimplifiedChinese.csv")
# 备份路径
BACKUP_PATH = "D:/Program Files (x86)/SteamLibrary/steamapps/common/Armello/armello_Data/resources.assets.backup"

def main():
    # 确定要写入的 CSV 文件
    if os.path.exists(MODIFIED_CSV):
        csv_path = MODIFIED_CSV
        print(f"✅ 找到修正版 CSV: {csv_path}")
    else:
        csv_path = FALLBACK_CSV
        print(f"⚠️  未找到 {MODIFIED_CSV}")
        print(f"   将使用原版 CSV 进行测试: {csv_path}")
        print(f"   如果你已经修改了翻译，请另存为 SimplifiedChinese_modified.csv")
    
    # 读取 CSV 内容
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        csv_content = f.read()
    
    print(f"CSV 文件大小: {len(csv_content):,} 字符 ({len(csv_content.encode('utf-8')):,} 字节)")
    print(f"CSV 行数: {csv_content.count(chr(10)):,}")
    
    # 检查游戏 assets 文件是否存在
    if not os.path.exists(GAME_ASSETS):
        print(f"❌ 找不到游戏 assets 文件: {GAME_ASSETS}")
        print("   请检查游戏安装路径是否正确")
        return
    
    print(f"\n正在加载 resources.assets...")
    print(f"  路径: {GAME_ASSETS}")
    
    env = UnityPy.load(GAME_ASSETS)
    
    # 查找 SimplifiedChinese TextAsset
    target_obj = None
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        try:
            data = obj.read()
            name = getattr(data, 'm_Name', '')
            if name == 'SimplifiedChinese':
                target_obj = obj
                print(f"✅ 找到 SimplifiedChinese TextAsset")
                print(f"   原大小: {len(getattr(data, 'm_Script', b''))} 字节")
                break
        except:
            pass
    
    if target_obj is None:
        print("❌ 在 resources.assets 中找不到 SimplifiedChinese TextAsset")
        print("   可能游戏文件结构已变化，或 UnityPy 版本不兼容")
        return
    
    # 备份原文件
    if not os.path.exists(BACKUP_PATH):
        print(f"\n📦 备份原文件...")
        shutil.copy2(GAME_ASSETS, BACKUP_PATH)
        print(f"   备份至: {BACKUP_PATH}")
    else:
        print(f"\n📦 备份已存在: {BACKUP_PATH} (跳过)")
    
    # 修改 TextAsset 内容（read_typetree 返回真文本 str，save_typetree 会按 UTF-8 编码落盘）
    print(f"\n✏️  正在写入修正后的翻译...")
    tt = target_obj.read_typetree()
    tt["m_Script"] = csv_content

    # 保存
    print(f"💾 保存 resources.assets...")
    try:
        target_obj.save_typetree(tt)
        packed = env.file.save()
        with open(GAME_ASSETS + ".new", "wb") as f:
            f.write(packed)
        # 用新文件替换原文件
        if os.path.exists(GAME_ASSETS + ".new"):
            os.replace(GAME_ASSETS + ".new", GAME_ASSETS)
            print(f"✅ 成功！resources.assets 已更新")
            print(f"   游戏路径: {GAME_ASSETS}")
            print(f"\n下次启动游戏时，汉化补丁即可生效！")
            print(f"   如果游戏崩溃，恢复备份：将 resources.assets.backup 改名回 resources.assets")
        else:
            print("❌ 保存失败：未生成新文件")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        print("\n尝试备用方案（导出后手动替换）...")
        # UnityPy 某些版本 save_packed 有限制，尝试导出单独文件再替换
        print("请查看脚本内的 manual_repack() 函数了解手动方案")

if __name__ == '__main__':
    main()

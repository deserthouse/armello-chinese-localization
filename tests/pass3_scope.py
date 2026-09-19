"""pass3 准备：被驳回改写的条目队列（移交 deepseek pro+思考接手）。"""
import json

# 用户驳回的文学性改写条目（原文/旧译保留，由 pro 三方研判重新处理）
DEFERRED = {
    # 名称定名类
    "CARD_CON06_NAME": "Moon Juice（月浆提案驳回，现译月亮果汁）",
    "CARD_ITM31_NAME": "Bastard Sword（手半剑提案驳回，现译混种剑）",
    "CARD_MAG06_NAME": "Syphon（虹吸提案驳回，现译虹吸管）",
    "CARD_BRW02_NAME": "Curse of Blood（血之咒提案驳回，现译血源之咒）",
    "CARD_PPN001_NAME": "Mother's Maze（母之迷宫提案驳回，现译母亲迷宫）",
    "CARD_KING02_NAME": "Wyldhide（怀尔德皮甲提案驳回，现译怀尔德隐披）",
    "CARD_TRK21_NAME": "Expendables（炮灰提案驳回，现译消耗品）",
    # 句病/双错类
    "INV_HERORAT03_DESCRIPTION": "与彼岸世界…（驳回，现译沿用官中病句）",
    "INV_HERORAT04_DESCRIPTION": "两面派老鼠双关（驳回）",
    "INV_HEROBANDIT03_DESCRIPTION": "too skilled to die 句式（驳回）",
    "INV_S3_2201_CHEST_DESCRIPTION": "know one knows 句序（驳回）",
    "INV_S3_2202_KEY_DESCRIPTION": "tricky trick 双关（驳回）",
    "UI_GDPR_MESSAGE_DESCRIPTION": "GDPR 句（驳回）",
    "INV_DICE_1008_BEARCLANLEGEND_DESCRIPTION": "born and bounced（驳回）",
    "INV_DICE_1010_RATCLANLEGEND_DESCRIPTION": "cubes of chance（驳回）",
    "INV_SKIN_10051_WOLF02_DESCRIPTION": "Rangers of the Veil（驳回）",
    "INV_SKIN_10091_WOLF03_DESCRIPTION": "Shieldfury（驳回）",
    # 效果文
    "CARD_MAG03_DESCRIPTION": "per Wound 措辞（驳回）",
    "ACH_100_019_DESCRIPTION": "3 Shields 措辞（驳回）",
    "ACH_100_024_DESCRIPTION": "3 Kills 措辞（驳回）",
    "INV_SIGNET22_DESCRIPTION": "折扣动词（驳回）",
    # 风味文
    "CARD_FOL06_FLAVORTEXT": "NOTHING! 强调（驳回）",
    "CARD_TRK43_FLAVORTEXT": "desecration 句（驳回）",
    "CARD_ITM27_FLAVORTEXT": "wielder's favour（驳回）",
    "CARD_TRK36_FLAVORTEXT": "or three 数量（驳回）",
}
json.dump(DEFERRED, open("tests/pass3_deferred.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"驳回队列 {len(DEFERRED)} 条已存 tests/pass3_deferred.json")

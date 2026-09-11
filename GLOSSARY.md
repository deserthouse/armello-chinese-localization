# Armello 中文本地化 · 译名规范总表

> 版本 1.1 ｜ 2026-09-11 ｜ 用途：作为 DeepSeek 翻译流水线的权威参照（机读版见 `glossary_master.json`）
> 来源：脚本固化术语（TERM_MAP / TERM_FIXES）+ 项目记忆 + 历次人工审计里程碑，三方合并去重。
> v1.1：新增全量重审/终审/盲审轮裁决的术语（见 §十二/§十三）。风格规范另见 `STYLE_GUIDE.md`。

---

## ⚠️ 冲突裁决（需你最终确认）

合并三方来源时发现以下互相打架的条目，我按"最新人工决策优先"裁决如下。**请你重点核对这 9 条**：

| 词条 | 旧译（废弃） | 采用 | 裁决依据 |
|---|---|---|---|
| Reprieve | 缓期执行 | **缓刑** | 06-16 最新决策；旧脚本里 `缓刑↔缓期执行` 存在循环替换，已消除 |
| Traitor | 叛徒 | **叛国者** | 最新术语决策 |
| Fugitive | 逃犯 | **亡命徒** | 最新术语决策 |
| King's Guard | 国王卫队 / 国王的卫队 | **国王守卫** | 最新统一 |
| Rot（数值） | 腐化值 | **腐化** | 数值语境也不加"值" |
| Hero vs Warrior | 一刀切"勇士→英雄" | **Hero→英雄 / Warrior→勇士** | 按英文原文逐条判断，禁止误伤正当的"勇士" |
| Thane | 萨恩 | **塞恩** | 脚本固化 HERO_NAMES |
| Armello | 阿尔玛洛 | **阿门罗** | 脚本固化（Crown of Armello→阿门罗之冕） |
| Clan | 一律"部族"或一律"族" | **分两套**：`[动物] Clan→[动物]族`（狼族/熊族）；独立 `Clan / Clan Bonus / Clan Grounds→部族（部族加成/部族领地）` | 两种语境并存 |

---

## 一、四大属性
| EN | 中文 |
|---|---|
| Fight | 战力 |
| Body | 体力 |
| Wits | 智力 |
| Spirit | 灵力 |

> 数值不加"值"：写"战力"而非"战力值"。

## 二、资源
| EN | 中文 |
|---|---|
| Health | 生命 |
| Gold | 金币 |
| Magic | 魔法（仅指资源；卡牌语境的 spell→法术） |
| Rot | 腐化 |
| Action Points / AP | 行动点数 |
| XP | 经验值 |
| Prestige | 声望 |

## 三、战斗机制
| EN | 中文 |
|---|---|
| Stealth | 潜行 |
| Evade | 闪避 |
| Scout | 侦察 |
| Pierce / Piercing | 贯穿 |
| Reflect / Reflecting | 反射 |
| Explode Pool | 爆发池 |
| Fortified | 设防 |
| Wards | 结界 |
| Stone Wards | 石阵结界 |
| Terrorised | 摧毁 |
| Rout / Routed | 溃退 |

## 四、状态
| EN | 中文 |
|---|---|
| Poison / Poisoned | 中毒 |
| Bane | 贝恩 |
| Rot | 腐化 |
| Infected | 已感染 |
| Corrupted | 已堕落 |

> **HUD 图标标签（HEADINGTEXT）**用"X中"表持续状态：闪避中 / 侦察中 / 潜行中 / 悬赏中。
> **卡牌正文（BODYTEXT）**用能力本身：获得闪避 / 获得侦察。
> Corrupted=已堕落、Infected=已感染（已用"已X"格式，不加"中"）。

## 五、世界 / 时间 / 地形
| EN | 中文 |
|---|---|
| Peril | 陷阱 |
| Settlement | 聚落 |
| Dungeon | 地牢 |
| Palace | 王宫 |
| Tile | 地块 |
| Dawn / Dusk | 黎明 / 黄昏 |
| Day / Night | 白天 / 黑夜 |
| Spirit Stone(s) | 灵石 |
| Pact | 契约 |
| Stone Circle | 石环 |
| Consecrate / Purge / Cleanse | 祝圣 / 涤除 / 净化 |
| Forest / Plains / Swamp / Mountain / Desert | 森林 / 平原 / 沼泽 / 山脉 / 沙漠 |

## 六、阵营 / 角色 / 身份
| EN | 中文 |
|---|---|
| Hero / Heroes | 英雄 |
| Warrior / Warriors | 勇士 |
| King's Guard | 国王守卫 |
| Merchant | 商人 |
| Spirit Walker | 灵界行者 |
| Follower | 随从 |
| Deck | 卡组 |
| Bounty | 悬赏 |
| Bounty Dice | 悬赏骰子 |
| Reprieve | 缓刑 |
| Traitor | 叛国者 |
| Fugitive | 亡命徒 |
| Wanted | 通缉犯 |
| Alchemist | 炼金术士 |
| Bard | 吟游诗人 |
| Shield Maiden | 盾卫 |
| Royal | 皇家 |
| Clan Bonus / Clan Grounds | 部族加成 / 部族领地 |

## 七、部族（动物 + Clan）
Wolf 狼族 ｜ Bear 熊族 ｜ Rabbit 兔族 ｜ Rat 鼠族 ｜ Bandit 强盗族 ｜ Dragon 龙族

## 八、英雄人名（24 位）
塞恩(Thane) 萨娜(Sana) 安布尔(Amber) 墨丘里奥(Mercurio) 里弗(River) 布朗(Brun) 佐沙(Zosha) 巴纳比(Barnaby) 戈尔(Ghor) 萨尔贡(Sargon) 马格努斯(Magnus) 伊莱莎(Elyssia) 哈格雷夫(Hargrave) 格莉奥特(Griotte) 尤尔达娜(Yordana) 斯卡蕾特(Scarlet) 塞拉斯(Sylas) 霍拉斯(Horace) 阿格尼亚(Agniya) 方(Fang) 沃洛达(Volodar) 奥克萨娜(Oxana) 特维斯(Twiss)

## 九、Wyld 系列卡片
怀尔德药草(Wyld Weed) 怀尔德树汁(Wyldsap) 怀尔德焰杖(Wyldfyre Staff) 怀尔德护符(Wyld Talisman) 怀尔德隐披(Wyldhide) 怀尔德之仪(Rite of Wyld) 怀尔德之诫(Wyld's Warning) 怀尔德净域(The Cleansing Wyld) 怀尔德之裔(Wyld Born)

## 十、BRW 诅咒卡（尤尔达娜系列）
怯懦之咒(Curse of Valour) 血源之咒(Curse of Blood) 障目之咒(Curse of Eye) 厄运之咒(Curse of Fate) 窃技之咒(Curse of Skill)

## 十一、专有名词
Armello 阿门罗 ｜ Wyld 怀尔德 ｜ Worm 蠕虫 ｜ Bane 贝恩 ｜ Ravid 独爪蜃 ｜ Ashen Forest 灰烬森林

## 十二、v1.1 新增（全量重审 / 终审 / 盲审裁决）

### 角色/身份
Squire 侍从 ｜ Cauldron Crone 坩埚老妪 ｜ shield-sister 持盾姐妹

### 装备（意译优先）
Mirror Cape 明镜披风 ｜ Royal Shield 御盾 ｜ Morning Star 晨星锤 ｜ Winged Boots 翅靴

### 机制名（同机制族同词根）
Scarcasting 疤痕施法 ｜ Scarcaster 疤痕施法者

## 十三、废弃变体表（出现即为错误）

| 废弃 | 正确 | 废弃 | 正确 |
|---|---|---|---|
| 默丘里奥 | 墨丘里奥 | 镜角 | 明镜披风 |
| 萨那 | 萨娜 | 怀尔德之火法杖 | 怀尔德焰杖 |
| 牌组 | 卡组 | 强盗家族 | 强盗族 |
| 石圈 | 石环 | 缓期执行 | 缓刑 |
| 腐化值 | 腐化 | 战力值 | 战力 |

---

## 翻译原则
1. 逐条对照英文原文，不盲从原有官中；以本表为准绳。
2. 术语全文统一，优先四字节奏。
3. 风味文（斜体/引文）追求文学品质：保留韵脚、双关、戏仿、口语腔，不生硬直译。
4. **人称代词**：指代英雄/守卫/有名角色的 it·its·they → 他/她/他们；指代物件/卡牌/陷阱的 it 仍用"它"。
5. Hero→英雄、Warrior→勇士，按原文区分，禁止统改。
6. 动词 roll dice → 投掷骰子（不用"滚动"）。
7. spell/magic 卡牌语境 → 法术（避免咒语/符咒/魔法卡混用；"魔法"专指资源）。
8. 数值属性不加"值"。
9. **保留原文换行符 `\n`、占位符（`{0}` 等）、富文本标签（`<special>` 等）原样不动。**
10. 不确定的专有名词宁可保留英文并标注，不臆造。

## 标点规范
- 风味文前后加中文引号""。
- 署名 `—— 角色名`；书名出处 `——《书名》`；非书出处 `—— 出处名`；摘录 `——《书名》摘录`。
- 中文与英文/数字之间加空格；中文标点间不加空格。
- 省略号统一为中文"……"。

## 禁止翻译（破坏会导致 repack 后崩溃/乱码）
占位符 `{0}`/`%s` ｜ 富文本标签 `<special>`/`<sprite>`/`<color>` ｜ 换行符 `\n` ｜ 可交易物品·皮肤·骰子内部代号 ｜ 纯 ID/代码/版本号/URL

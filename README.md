# Armello 简体中文重译汉化补丁

Armello（阿门罗）官方简体中文的社区重译项目。对游戏内全部 **10,867 条**文本完成了整库重译、四版本对照终审与程序化 QA，最终打包为可直接使用的 `resources.assets` 补丁。

## 使用方法

1. 将 `SimplifiedChinese_export.csv` 的内容通过 `repack.py` 写入游戏（或直接下载我们打好的补丁文件，见 Release）
2. 备份并替换游戏目录下的 `resources.assets`
3. 启动游戏即可

> ⚠️ 首次运行 `repack.py` 会自动备份原文件为 `resources.assets.backup`；如遇问题，将备份改名回 `resources.assets` 即可还原。

## 项目架构

```
English.csv                               英文原文（对照源）
SimplifiedChinese_export.csv              汉化成果（10,867 条终版全文）
master.jsonl                              真源数据：全部条目与决策留痕（provenance）
pipeline.py                               流水线入口：init/translate/review_split/review_merge/export
flash_translate.py                        DeepSeek 初翻脚本（哨兵化占位符保护）
repack.py                                 打包写回（UnityPy）
GLOSSARY.md / glossary_master.json        译名规范总表（人读/机读）
STYLE_GUIDE.md                            风格指南
```

## 质量保障

- 全部 10,867 条文本逐条对照英文原文重译与审校，官中优秀译文予以保留
- 术语与风格执行统一规范（见 GLOSSARY.md / STYLE_GUIDE.md）
- 占位符、格式标签经程序化校验，补丁打包前全部通过


## 标准资产

- **GLOSSARY.md**：术语表 v1.1（含 9 条冲突裁决、废弃变体表）
- **STYLE_GUIDE.md**：风格指南（人称/状态句模板/标点/专名风格/判决纪律）

## 归属与声明

- 《Armello》及其全部原始文本版权归 **League of Geeks** 所有
- 本补丁为非商业社区项目，仅供已购买游戏的玩家个人使用，禁止二次分发游戏文本
- 翻译质量反馈欢迎提 Issue

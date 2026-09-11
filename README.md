# Armello 简体中文重译汉化补丁

非官方简体中文全量重译。基于官方中文的机翻问题，对游戏内 **10,867 条**文本逐条对照英文原文重新翻译与审校，覆盖任务剧情、卡牌、物品、UI、成就、对话等全部内容。

## 📦 下载

前往 [**Releases 页面**](https://github.com/deserthouse/armello-chinese-localization/releases) 下载最新版 `armello-zh-patch-v1.0.zip`。

## 🎮 安装（三步）

1. 解压压缩包，得到 `resources.assets`
2. 找到游戏目录（Steam 库中右键 Armello → 管理 → 浏览本地文件，进入 `armello_Data` 文件夹）
3. 将 `resources.assets` 复制进去，**覆盖**同名文件，启动游戏

> 建议覆盖前先把原文件备份一份（或复制一份改名为 `resources.assets.backup`）。

## ↩️ 还原官方中文

进入 `armello_Data` 文件夹，删除补丁的 `resources.assets`，把你备份的原文件名改回 `resources.assets` 即可。

## ❓ 常见问题

**Q：游戏更新后补丁会失效吗？**
游戏大版本更新后文本结构可能变化，届时需要等本补丁适配新版。若更新后出现异常，先还原官方中文。

**Q：会影响成就或联机吗？**
不会。补丁只替换显示文本，不修改任何游戏逻辑与数值。

**Q：遇到错别字或翻译问题？**
欢迎提 Issue，注明大概位置（哪个界面/哪张卡/哪段剧情）即可。

## ✅ 质量保障

- 全部文本逐条对照英文原文重译与审校，官中优秀译文予以保留
- 术语与风格执行统一规范（见 GLOSSARY.md / STYLE_GUIDE.md）
- 占位符、格式标签经程序化校验，打包前全部通过

## 🔧 给开发者

流水线与源数据在本仓库内：`master.jsonl`（全部条目及决策留痕）、`pipeline.py`（审计/导出入口）、`repack.py`（打包）、`GLOSSARY.md` + `STYLE_GUIDE.md`（标准资产）。详见各文件头部说明。

## 归属声明

《Armello》及全部原始文本版权归 **League of Geeks** 所有。本补丁为非商业社区项目，仅供已购买游戏的玩家个人使用；如权利方认为本仓库侵犯权益，请联系删除。

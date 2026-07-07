# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

班级近视率分析静态页面。整站只有一个 `index.html`(内联 CSS/JS,无构建步骤、无框架),数据由 `update_page_data.py` 从 `近视率.xlsx` 注入。推送到 main 后由 Cloudflare Pages 自动发布(`CNAME` 是历史 GitHub Pages 遗留,线上域名以 Cloudflare Pages 配置为准)。

仓库规范详见 `AGENTS.md`(中文文案、UTF-8、Python 4 空格缩进 + snake_case、中文动宾结构提交信息等)。

## 常用命令

```powershell
python update_page_data.py            # 从 Excel 重新生成页面数据,输出总人数/近视人数/近视率
python -m py_compile update_page_data.py   # Python 语法检查
```

- 脚本依赖 `openpyxl`,通过 `pip install -r requirements.txt` 安装。
- 无测试框架。改脚本后跑上面两条命令;改页面后直接用浏览器打开 `index.html` 检查(无需本地服务器),重点看整体近视率、人数、性别对比和移动端布局。

## 架构与数据流

```
近视率.xlsx (仅本地,已被 .gitignore 忽略)
  → update_page_data.py 读取「性别」「近视」两列
  → 替换 index.html 中 id="records-data" 的 JSON 数据岛(<script type="application/json">)
  → 页面加载时由内联 JS JSON.parse 该数据块,完成全部统计计算和 DOM 渲染
```

关键耦合点与约束:

- **`近视率.xlsx` 不进版本库**。克隆后本地没有该文件时脚本无法运行,但页面数据已以 JSON 形式存在于 `index.html` 中,页面本身始终可用。更新数据时改 Excel 再跑脚本,不要手工编辑 HTML 里的数据。
- **数据岛锚点不可破坏**:数据存放在 `<script type="application/json" id="records-data">…</script>` 中,`update_html()` 以该标签为正则锚点做恰好一次的替换,页面 JS 通过 `JSON.parse` 读取。不要重命名该 id、拆改标签或引入第二处同名标签,否则脚本报错。
- **统计口径**(改动需在页脚注和 PR 中同步说明):「近视」列严格等于 `是` 才计入近视,空白或其他值计入"未标记近视";「性别」列为空的整行跳过。脚本会对「是/否/空」之外的近视值、「男/女」之外的性别值逐行打印警告,但不中断执行。
- **Python 只负责注入数据,不做统计**;总人数、近视率、性别对比、基准对比全部在 `index.html` 内联 JS 中计算。基准常量也硬编码在那里:`NATIONAL_PRIMARY_RATE = 35.6`(国家卫健委 2023 全国小学生近视率)、`SZ_TARGET_RATE = 38`(深圳 2030 防控目标)。
- **隐私**:`records` 只含 `gender`、`myopia` 两个匿名字段,禁止把学生姓名等个人信息写入 `index.html`。

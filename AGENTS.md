# Repository Guidelines

## 项目结构与模块组织

本仓库用于生成和展示班级近视率分析页面。核心文件如下：

- `index.html`：静态分析页面，包含样式、前端计算逻辑和由脚本注入的数据。
- `update_page_data.py`：从 `近视率.xlsx` 读取 `性别`、`近视` 两列，并更新 `index.html` 中的 `records` 数据块。
- `近视率.xlsx`：原始数据表。更新数据时优先修改此文件，不要手工改 HTML 中的数据。
- `CNAME`：GitHub Pages 自定义域名配置，当前域名为 `js.468024.xyz`；修改域名时以此文件内容为准，并同步 GitHub Pages 设置与 DNS 配置。
- `.gitignore`：忽略本地或生成文件。

当前没有独立的 `src/`、`tests/` 或资源目录；新增代码时保持结构简单，除非确实需要拆分。

## 构建、测试与本地开发命令

- `python update_page_data.py`：从 Excel 重新生成页面数据，并输出总人数、近视人数和近视率。
- `python -m py_compile update_page_data.py`：检查 Python 脚本语法。
- 直接用浏览器打开 `index.html`：查看页面效果；本项目不需要本地开发服务器。
- 线上部署使用 GitHub Pages；更新静态文件并推送后，由 GitHub Pages 根据仓库的发布配置自动部署，自定义域名以 `CNAME` 为准。

更新数据后的常规流程：

```powershell
python update_page_data.py
python -m py_compile update_page_data.py
```

## 编码风格与命名规范

所有文档和界面文案使用中文。文件统一使用 UTF-8。Python 使用 4 空格缩进、`snake_case` 命名，并保持函数职责单一。HTML、CSS、JS 保持当前单文件风格；新增 DOM `id` 应语义清晰，例如 `overallRate`、`genderHint`。不要把学生姓名等个人信息写入 `index.html`，页面只保留匿名统计字段。

## 测试指南

当前没有测试框架。修改脚本后至少运行 `python update_page_data.py` 和 `python -m py_compile update_page_data.py`。修改页面后手动打开 `index.html`，检查整体近视率、人数、性别对比和移动端布局。若后续引入测试，建议放在 `tests/`，命名为 `test_*.py`。

## 提交与 Pull Request 规范

现有提交使用中文描述式信息，例如 `添加 .gitignore、CNAME 文件和初始 HTML 页面`、`更新 CNAME 文件以更改域名`。继续使用简短的动宾结构，说明主要变更。

PR 应包含：变更目的、数据口径是否变化、已运行的命令、页面截图或关键数值对比。涉及 Excel 数据更新时，说明总人数、近视人数和近视率。涉及部署配置时，说明 GitHub Pages 的发布来源、自定义域名（`CNAME`）和 DNS 配置是否变化。

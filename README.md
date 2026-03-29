# PaperAlert - 学术期刊订阅系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

自动追踪学术期刊最新文章，AI 翻译摘要，智能推送到 Notion 数据库。让你轻松掌握领域内的最新研究进展。

## ✨ 功能特性

- 🔄 **自动化抓取** - 从 Crossref 数据库自动获取期刊最新文章
- 🌐 **AI 智能翻译** - 支持任意 OpenAI 兼容 API（Claude、Qwen 等），翻译标题和摘要为中文
- 📊 **Notion 集成** - 自动推送到 Notion 数据库，方便管理和阅读
- 📈 **增量更新** - 智能记录更新历史，避免重复抓取
- 🧹 **自动清理** - 自动归档 30 天前的旧文章，保持数据库整洁
- ⏰ **定时运行** - 支持 GitHub Actions 自动化，无需本地服务器
- 🎯 **灵活订阅** - 支持订阅任意数量的学术期刊
- 📝 **期刊小结** - 自动生成每期期刊的研究趋势总结
- 💰 **成本优化** - 仅翻译核心内容，大幅降低 API 费用

## 🚀 部署方式选择

| | 本地运行 | GitHub Actions |
|--|---------|---------------|
| 适合场景 | 调试、临时运行 | 长期自动化，无需本地服务器 |
| 配置方式 | `config.json` 文件 | GitHub Secrets |
| 运行触发 | 手动执行 | 定时自动（每周一 8 点）+ 手动触发 |

两种方式共用同一套 Notion 数据库，按需选择或两者并用。

---

## 🎬 快速开始

### 第一步：准备 Notion

> 无论本地运行还是 Actions，都需要先完成此步骤。

#### 1. 创建 Notion Integration

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 **+ New integration**，名称填 `PaperAlert`，选择你的工作区
3. 复制生成的 **Internal Integration Token**（以 `ntn_` 或 `secret_` 开头）

#### 2. 创建三个 Notion 数据库

在 Notion 中新建三个数据库（可放在同一页面下），按下表配置属性：

**📚 期刊订阅表**

| 属性名 | 类型 |
|--------|------|
| Journal | 标题(Title) |
| 是否启用订阅 | 复选框(Checkbox) |
| Online ISSN | 文本(Text) |
| Print ISSN | 文本(Text) |
| 起始抓取日期 | 日期(Date) |
| 最后更新日期 | 日期(Date) |
| 最近处理日期 | 日期(Date) |
| 最近处理状态 | 文本(Text) |

**📄 文章推送库**

| 属性名 | 类型 |
|--------|------|
| Title | 标题(Title) |
| 标题 | 文本(Text) |
| Journal | 文本(Text) |
| Volume | 文本(Text) |
| Issue | 文本(Text) |
| Year | 数字(Number) |
| Year-Month | 文本(Text) |
| YearQuarter | 文本(Text) |
| Author | 文本(Text) |
| Abstract | 文本(Text) |
| 摘要 | 文本(Text) |
| Link | URL |
| 上传日期 | 日期(Date) |

**📋 期刊小结库**

| 属性名 | 类型 |
|--------|------|
| Journal | 标题(Title) |
| Volume | 文本(Text) |
| Issue | 文本(Text) |
| Year | 数字(Number) |
| 文章数量 | 数字(Number) |
| 小结 | 文本(Text) |
| 小结生成日期 | 日期(Date) |

#### 3. 连接 Integration 到数据库

对**每个**数据库执行：点击右上角 `...` → **Add connections** → 选择 `PaperAlert`

#### 4. 获取 Database ID

打开数据库页面，从浏览器地址栏复制 ID：

```
https://www.notion.so/workspace/DatabaseName-c98ca17d606b4028a74e3c513f101921?v=...
                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                              这就是 Database ID（32位）
```

#### 5. 添加期刊订阅

在"期刊订阅表"中添加要追踪的期刊：

| Journal | 是否启用订阅 | Online ISSN | 起始抓取日期 |
|---------|-------------|-------------|-------------|
| Nature Genetics | ✅ | 1546-1718 | 2024-01-01 |
| Cell | ✅ | 1097-4172 | 2024-01-01 |

> **查找期刊 ISSN**：访问期刊官网、[JCR](https://jcr.clarivate.com/)，或 Google 搜索"期刊名 ISSN"

---

### 方式一：本地运行

#### 1. 克隆并安装依赖

```bash
git clone https://github.com/你的用户名/PaperAlert.git
cd PaperAlert
pip install -r requirements.txt
```

#### 2. 配置 config.json

```bash
cp config.template.json config.json
```

编辑 `config.json`，填入你的 API Key 和 Database ID：

```json
{
  "notion": {
    "api_key": "ntn_你的Notion_API_Key",
    "databases": {
      "subscriptions": "期刊订阅表的Database_ID",
      "articles": "文章推送库的Database_ID",
      "summaries": "期刊小结库的Database_ID"
    }
  },
  "anthropic": {
    "api_key": "sk-ant-你的API_Key"
  }
}
```

使用其他 OpenAI 兼容服务时，额外指定 `base_url` 和 `model`：

```json
{
  "notion": { "..." },
  "anthropic": {
    "api_key": "sk-你的API_Key",
    "base_url": "https://你的服务端点/v1",
    "model": "your-model-name"
  }
}
```

> `config.json` 已加入 `.gitignore`，不会被提交到 Git。

#### 3. 验证配置

```bash
python test_config.py
```

确保所有检查通过再继续。

#### 4. 运行

```bash
python journal_subscription_v2.py
```

程序将依次：
1. 归档 30 天前的旧文章
2. 读取所有启用的期刊订阅
3. 从 Crossref 抓取新文章
4. 调用 AI 翻译标题和摘要
5. 推送到 Notion 文章库
6. 生成每期期刊小结
7. 更新订阅状态

---

### 方式二：GitHub Actions 自动化

每周一北京时间 8:00 自动运行，无需本地服务器。

#### 1. Fork 仓库

将本仓库 Fork 到你的 GitHub 账号。

#### 2. 配置 GitHub Secrets

进入你的仓库 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，逐一添加：

**必需：**

| Secret 名称 | 填入内容 |
|------------|---------|
| `NOTION_API_KEY` | Notion Integration Token |
| `NOTION_DB_SUBSCRIPTIONS` | 期刊订阅表 Database ID |
| `NOTION_DB_ARTICLES` | 文章推送库 Database ID |
| `NOTION_DB_SUMMARIES` | 期刊小结库 Database ID |
| `ANTHROPIC_API_KEY` | AI 服务的 API Key |

**可选（使用非默认 AI 服务时填写）：**

| Secret 名称 | 填入内容 |
|------------|---------|
| `ANTHROPIC_BASE_URL` | 自定义 API 端点，如 `https://api.siliconflow.cn/v1` |
| `ANTHROPIC_MODEL` | 自定义模型名称，如 `Qwen/Qwen3-235B-A22B` |

> 不填 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_MODEL` 时，默认使用 Anthropic 官方 API 和 `claude-sonnet-4-20250514` 模型。

#### 3. 启用 Actions

进入仓库的 **Actions** 标签，点击 **I understand my workflows, go ahead and enable them**。

#### 4. 首次手动触发测试

1. **Actions** → 左侧选择 **期刊订阅自动同步**
2. 右侧点击 **Run workflow** → **Run workflow**
3. 等待完成，绿色勾号表示成功

之后每周一 8:00 会自动运行。

#### 修改运行频率

编辑 `.github/workflows/journal-sync.yml`，修改 cron 表达式（GitHub Actions 使用 UTC 时间，北京时间 = UTC + 8）：

```yaml
on:
  schedule:
    - cron: '0 0 * * 1'   # 每周一 08:00 北京时间
    # - cron: '0 0 * * *'  # 每天 08:00 北京时间
    # - cron: '0 0 1 * *'  # 每月1日 08:00 北京时间
```

## 🔧 工作原理

### 系统架构

```
┌─────────────┐      ┌──────────────┐      ┌──────────────────┐
│  Crossref   │─────>│    Python    │─────>│  AI 翻译服务      │
│  Database   │      │    脚本       │      │ (任意 OpenAI 兼容) │
└─────────────┘      └──────────────┘      └──────────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Notion    │
                     │  3 个数据库  │
                     └─────────────┘
```

### 增量更新机制

系统采用智能增量更新：

1. **首次运行**：从"起始抓取日期"开始抓取
2. **后续运行**：从"最后更新日期"开始抓取
3. **状态更新**：
   - ✅ 成功推送文章 → 更新"最后更新日期"
   - ⚠️ 无新文章 → 不更新"最后更新日期"
   - ❌ 推送失败 → 不更新"最后更新日期"

这样可以避免重复抓取，节省 API 调用和时间。

## ❓ 常见问题

### 找不到文章怎么办？

可能的原因和解决方案：

1. **ISSN 错误** - 检查 Online ISSN 和 Print ISSN 都试一下
2. **日期太久远** - 建议起始日期设置为最近 6 个月内
3. **期刊不在 Crossref** - 有些期刊可能不收录在 Crossref 数据库
4. **查看日志** - 检查"最近处理状态"中的错误信息

### 如何降低 API 费用？

本项目已优化为仅翻译标题和摘要，成本估算：

- **Crossref API**：完全免费
- **Claude API**：每篇文章约 500-1000 tokens
  - 订阅 10 个期刊，每周约 $1-3
  - 订阅 30 个期刊，每周约 $3-8

### 可以订阅多少期刊？

- 技术上无限制
- 建议 10-30 个期刊（平衡时间和成本）
- 单个期刊处理时间约 1-3 分钟

### 如何自定义翻译？

修改 `journal_subscription_v2.py` 中的 `translate_and_extract()` 函数，调整 `prompt` 内容即可。

### GitHub Actions 运行失败？

1. **检查 Secrets** - 确保所有必需的 Secrets 都已配置
2. **查看日志** - 在 Actions 标签页查看详细错误信息
3. **Notion 连接** - 确认数据库已添加 Integration 连接
4. **API 额度** - 检查 API Key 是否有效、是否有足够额度

## 🛠️ 高级配置

### 修改抓取数量限制

在 `journal_subscription_v2.py` 的 `fetch_articles_by_issn()` 函数中：

```python
works = cr.works(
    filter={...},
    limit=100,  # 修改为需要的数量，最大 1000
    ...
)
```

### 添加自定义 Notion 字段

在 Notion 数据库中：
1. 直接添加新属性列
2. **不要**修改现有属性的名称和类型
3. 脚本会自动忽略自定义字段

### 使用其他 AI 服务

系统使用 OpenAI 兼容协议，只需在配置文件中修改 `base_url` 和 `model`：

```json
{
  "anthropic": {
    "api_key": "你的API_Key",
    "base_url": "https://your-ai-service.com/v1",
    "model": "your-model-name"
  }
}
```

或通过环境变量 `AI_BASE_URL` / `AI_MODEL` 设置（与 `ANTHROPIC_BASE_URL` / `ANTHROPIC_MODEL` 等效）。

## 📊 技术栈

- **Python 3.8+**
- **[habanero](https://github.com/sckott/habanero)** - Crossref API 客户端
- **[openai](https://github.com/openai/openai-python)** - OpenAI 兼容 SDK（支持 Claude、Qwen 等任意兼容服务）
- **[requests](https://requests.readthedocs.io/)** - HTTP 请求库
- **Notion API** - Notion 数据库操作

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.1.0 (2026-03-29)

- 🔄 切换为 OpenAI 兼容 SDK，支持任意兼容服务
- 🧹 新增自动清理功能，归档 30 天前的旧文章
- 🌐 新增 `AI_BASE_URL` / `AI_MODEL` 环境变量别名

### v2.0.0 (2026-01-31)

- ✨ 重构为使用 Notion 官方 API
- 🚀 添加 GitHub Actions 自动化支持
- 📈 实现增量更新机制
- 💰 优化 AI 翻译，仅翻译标题和摘要
- 🔐 支持环境变量配置，保护敏感信息
- 📖 完善文档和配置指南

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- 灵感来源于学术订阅需求
- 感谢 Crossref 提供免费的学术文献数据库
- 感谢 Anthropic 提供强大的 AI 翻译能力

## 📧 联系方式

如有问题或建议，欢迎：
- 提交 [Issue](https://github.com/你的用户名/PaperAlert/issues)
- 发起 [Discussion](https://github.com/你的用户名/PaperAlert/discussions)

---

⭐ 如果这个项目对你有帮助，欢迎 Star 支持！

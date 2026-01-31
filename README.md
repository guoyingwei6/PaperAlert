# PaperAlert - 学术期刊订阅系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

自动追踪学术期刊最新文章，AI 翻译摘要，智能推送到 Notion 数据库。让你轻松掌握领域内的最新研究进展。

## ✨ 功能特性

- 🔄 **自动化抓取** - 从 Crossref 数据库自动获取期刊最新文章
- 🌐 **AI 智能翻译** - 使用 Claude AI 翻译标题和摘要为中文
- 📊 **Notion 集成** - 自动推送到 Notion 数据库，方便管理和阅读
- 📈 **增量更新** - 智能记录更新历史，避免重复抓取
- ⏰ **定时运行** - 支持 GitHub Actions 自动化，无需本地服务器
- 🎯 **灵活订阅** - 支持订阅任意数量的学术期刊
- 📝 **期刊小结** - 自动生成每期期刊的研究趋势总结
- 💰 **成本优化** - 仅翻译核心内容，大幅降低 API 费用

## 🎬 快速开始

### 前置要求

1. **Notion 账号** - [免费注册](https://www.notion.so/)
2. **AI API Key** - 支持以下任一服务：
   - [Anthropic Claude](https://console.anthropic.com/)（推荐）
   - [阿里云百炼](https://dashscope.aliyuncs.com/)（国内访问更快）
3. **GitHub 账号**（用于自动化运行，可选）

### 安装步骤

#### 1️⃣ 克隆仓库

```bash
git clone https://github.com/你的用户名/PaperAlert.git
cd PaperAlert
```

#### 2️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

#### 3️⃣ 配置 Notion

##### 3.1 创建 Notion Integration

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 **+ New integration**
3. 设置名称为 `PaperAlert`，选择关联的工作区
4. 复制生成的 **Internal Integration Token**（以 `ntn_` 或 `secret_` 开头）

##### 3.2 创建 Notion 数据库

在 Notion 中创建以下三个数据库（可以在同一个页面下）：

**📚 期刊订阅表**

| 属性名 | 类型 | 说明 |
|--------|------|------|
| Journal | 标题(Title) | 期刊名称 |
| 是否启用订阅 | 复选框(Checkbox) | 控制是否抓取 |
| Online ISSN | 文本(Text) | 在线ISSN |
| Print ISSN | 文本(Text) | 印刷ISSN（备用） |
| 起始抓取日期 | 日期(Date) | 首次抓取起始日期 |
| 最后更新日期 | 日期(Date) | 上次成功抓取日期 |
| 最近处理日期 | 日期(Date) | 最近运行日期 |
| 最近处理状态 | 文本(Text) | 运行状态信息 |

**📄 文章推送库**

| 属性名 | 类型 | 说明 |
|--------|------|------|
| Title | 标题(Title) | 英文标题 |
| 标题 | 文本(Text) | 中文标题 |
| Journal | 文本(Text) | 期刊名 |
| Volume | 文本(Text) | 卷号 |
| Issue | 文本(Text) | 期号 |
| Year | 数字(Number) | 年份 |
| Year-Month | 文本(Text) | 年月 |
| YearQuarter | 文本(Text) | 年季度 |
| Author | 文本(Text) | 作者 |
| Abstract | 文本(Text) | 英文摘要 |
| 摘要 | 文本(Text) | 中文摘要 |
| Link | URL | 文章链接 |
| 上传日期 | 日期(Date) | 推送日期 |

**📋 期刊小结库**

| 属性名 | 类型 | 说明 |
|--------|------|------|
| Journal | 标题(Title) | 期刊名 |
| Volume | 文本(Text) | 卷号 |
| Issue | 文本(Text) | 期号 |
| Year | 数字(Number) | 年份 |
| 文章数量 | 数字(Number) | 文章数 |
| 小结 | 文本(Text) | AI小结 |
| 小结生成日期 | 日期(Date) | 生成日期 |

##### 3.3 连接 Integration 到数据库

对每个数据库：
1. 点击数据库右上角 `...` 按钮
2. 选择 **Add connections**
3. 找到并选择你的 `PaperAlert` integration

##### 3.4 获取 Database ID

在 Notion 中打开数据库，复制浏览器地址栏中的 ID：

```
https://www.notion.so/workspace/DatabaseName-c98ca17d606b4028a74e3c513f101921?v=...
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          这部分就是 Database ID
```

#### 4️⃣ 配置 API Keys

##### 方式一：配置文件（本地运行）

复制模板文件：

```bash
cp config.template.json config.json
```

编辑 `config.json`：

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
    "api_key": "sk-ant-你的Anthropic_API_Key"
  }
}
```

**使用阿里云百炼（可选）：**

```json
{
  "notion": { ... },
  "anthropic": {
    "api_key": "sk-你的阿里云API_Key",
    "base_url": "https://dashscope.aliyuncs.com/apps/anthropic",
    "model": "qwen3-max-2026-01-23"
  }
}
```

##### 方式二：环境变量（GitHub Actions）

在 GitHub 仓库设置中配置 Secrets：

1. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret** 添加以下变量：

| Secret 名称 | 值 |
|------------|-----|
| `NOTION_API_KEY` | 你的 Notion API Key |
| `NOTION_DB_SUBSCRIPTIONS` | 期刊订阅表 ID |
| `NOTION_DB_ARTICLES` | 文章推送库 ID |
| `NOTION_DB_SUMMARIES` | 期刊小结库 ID |
| `ANTHROPIC_API_KEY` | 你的 AI API Key |
| `ANTHROPIC_BASE_URL` | （可选）自定义 API 端点 |
| `ANTHROPIC_MODEL` | （可选）自定义模型名称 |

详细配置说明请查看 [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

## 📖 使用指南

### 本地运行

#### 1. 添加期刊订阅

在 Notion 的"期刊订阅表"中添加期刊：

| Journal | 是否启用订阅 | Online ISSN | 起始抓取日期 |
|---------|-------------|-------------|-------------|
| Nature Genetics | ✅ | 1546-1718 | 2024-01-01 |
| Cell | ✅ | 1097-4172 | 2024-01-01 |

**如何查找期刊 ISSN？**
- 访问期刊官网查看
- 在 [JCR (Journal Citation Reports)](https://jcr.clarivate.com/) 搜索
- Google 搜索 "期刊名 + ISSN"

#### 2. 测试配置

```bash
python test_config.py
```

确保所有测试通过后再运行主程序。

#### 3. 运行主程序

```bash
python journal_subscription_v2.py
```

程序将：
1. ✅ 读取所有启用订阅的期刊
2. ✅ 从 Crossref 抓取新文章
3. ✅ 使用 AI 翻译标题和摘要
4. ✅ 推送到 Notion 文章库
5. ✅ 生成期刊小结
6. ✅ 更新订阅状态

### GitHub Actions 自动化

项目已配置 GitHub Actions，每周一早上 8 点自动运行。

#### 启用自动化

1. **Fork 本仓库**到你的 GitHub 账号
2. **配置 Secrets**（参见上方"配置 API Keys"）
3. **启用 Actions**：
   - 进入 **Actions** 标签
   - 点击 **I understand my workflows, go ahead and enable them**

#### 手动触发

1. 进入 **Actions** 标签
2. 选择 **期刊订阅自动同步**
3. 点击 **Run workflow** → **Run workflow**

#### 修改运行频率

编辑 `.github/workflows/journal-sync.yml`：

```yaml
on:
  schedule:
    # 每周一早上8点 (UTC 00:00 = 北京时间 08:00)
    - cron: '0 0 * * 1'
```

Cron 表达式示例：
- `0 0 * * 1` - 每周一早上 8 点
- `0 0 * * *` - 每天早上 8 点
- `0 0 1 * *` - 每月1号早上 8 点

## 🔧 工作原理

### 系统架构

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Crossref   │─────>│    Python    │─────>│  Claude AI  │
│  Database   │      │    脚本       │      │   翻译服务   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Notion    │
                     │   Database  │
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

修改 `journal_subscription_v2.py` 中的 `translate_and_extract()` 函数：

```python
prompt = f"""请将以下学术文章的标题和摘要翻译成中文：

标题：{title}
摘要：{abstract}

要求：
1. 翻译准确、符合学术规范
2. 保留专业术语
3. 符合中文表达习惯

..."""
```

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

只需在配置文件中修改 `base_url` 和 `model`：

```json
{
  "anthropic": {
    "api_key": "你的API_Key",
    "base_url": "https://your-ai-service.com/v1",
    "model": "your-model-name"
  }
}
```

## 📊 技术栈

- **Python 3.8+**
- **[habanero](https://github.com/sckott/habanero)** - Crossref API 客户端
- **[anthropic](https://github.com/anthropics/anthropic-sdk-python)** - Claude API SDK
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

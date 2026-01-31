# GitHub Actions 自动化配置指南

本文档将指导你如何配置 GitHub Actions，使项目每天自动运行期刊订阅同步。

## 📋 前置要求

在配置 GitHub Actions 之前，请确保你已经：

1. ✅ 获取了 Notion API Key 和 Database IDs
2. ✅ 获取了 Anthropic API Key（或阿里云 DashScope API Key）
3. ✅ 本地运行测试成功

## 🔐 配置 GitHub Secrets

为了保护你的敏感信息，需要在 GitHub 仓库中配置 Secrets。这些 Secrets 不会被公开，只在 GitHub Actions 运行时使用。

### 步骤 1: 进入 Secrets 设置页面

1. 打开你的 GitHub 仓库页面
2. 点击顶部菜单的 **Settings**（设置）
3. 在左侧菜单中找到 **Secrets and variables** → **Actions**
4. 点击 **New repository secret** 按钮

### 步骤 2: 添加必需的 Secrets

按照以下列表，逐一添加 Secret（点击 "New repository secret" 按钮，填写 Name 和 Secret 值）：

#### Notion 相关配置（必需）

| Secret Name | 说明 | 示例值 |
|------------|------|--------|
| `NOTION_API_KEY` | Notion Integration 的 API Key | `ntn_xxxxxxxxxxxxx` 或 `secret_xxxxxxxxxxxxx` |
| `NOTION_DB_SUBSCRIPTIONS` | 期刊订阅表的 Database ID | `c98ca17d606b4028a74e3c513f101921` |
| `NOTION_DB_ARTICLES` | 文章推送库的 Database ID | `9dd8fb5ad12e49bbbbedfc91c864cdbd` |
| `NOTION_DB_SUMMARIES` | 期刊小结库的 Database ID | `b053e2cae8b64b3e8d258c79d2542fc5` |

#### Anthropic AI 配置（必需）

| Secret Name | 说明 | 示例值 |
|------------|------|--------|
| `ANTHROPIC_API_KEY` | Anthropic API Key 或阿里云 API Key | `sk-ant-xxxxx` 或 `sk-xxxxx` |

#### 自定义 AI 端点配置（可选）

如果你使用阿里云 DashScope 或其他第三方 AI 服务，需要添加这两个 Secret：

| Secret Name | 说明 | 示例值 |
|------------|------|--------|
| `ANTHROPIC_BASE_URL` | 自定义 API 端点 URL | `https://dashscope.aliyuncs.com/apps/anthropic` |
| `ANTHROPIC_MODEL` | 使用的模型名称 | `qwen3-max-2026-01-23` |

**注意**：
- 如果使用 Anthropic 官方 API，**不需要**添加 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_MODEL`
- 如果使用阿里云等第三方服务，**必须**添加这两个配置

### 步骤 3: 验证配置

添加完所有 Secrets 后，你的 Secrets 列表应该包含：

**使用 Anthropic 官方 API：**
- ✅ NOTION_API_KEY
- ✅ NOTION_DB_SUBSCRIPTIONS
- ✅ NOTION_DB_ARTICLES
- ✅ NOTION_DB_SUMMARIES
- ✅ ANTHROPIC_API_KEY

**使用阿里云等第三方服务：**
- ✅ NOTION_API_KEY
- ✅ NOTION_DB_SUBSCRIPTIONS
- ✅ NOTION_DB_ARTICLES
- ✅ NOTION_DB_SUMMARIES
- ✅ ANTHROPIC_API_KEY
- ✅ ANTHROPIC_BASE_URL
- ✅ ANTHROPIC_MODEL

## ⚙️ GitHub Actions 配置说明

项目中的 `.github/workflows/journal-sync.yml` 文件配置了自动化任务：

```yaml
on:
  schedule:
    # 每天北京时间上午9点运行 (UTC+8 = UTC 01:00)
    - cron: '0 1 * * *'

  # 允许手动触发
  workflow_dispatch:
```

### 运行时间

- **自动运行**：每天北京时间上午 9 点
- **手动触发**：随时可以在 GitHub Actions 页面手动运行

### 修改运行时间

如果想修改运行时间，编辑 `.github/workflows/journal-sync.yml` 文件中的 cron 表达式：

```yaml
# 每周一上午9点运行
- cron: '0 1 * * 1'

# 每天下午3点运行
- cron: '7 0 * * *'  # UTC 00:07 = 北京时间 08:07

# 每周一和周四上午9点运行
- cron: '0 1 * * 1,4'
```

**注意**：GitHub Actions 使用 UTC 时间，北京时间需要减去 8 小时转换。

## 🧪 测试 GitHub Actions

配置完成后，建议先手动触发一次测试：

1. 进入仓库页面
2. 点击顶部的 **Actions** 标签
3. 在左侧选择 "期刊订阅自动同步" workflow
4. 点击右上角的 **Run workflow** 按钮
5. 点击 **Run workflow** 确认

等待几分钟后，可以查看运行日志：
- ✅ 绿色勾号表示成功
- ❌ 红色叉号表示失败，点击查看详细日志

## 🔍 如何获取 Database ID

如果你不确定 Notion Database ID，可以按照以下步骤获取：

1. 在 Notion 中打开数据库页面
2. 点击右上角的 **Share** 按钮
3. 复制分享链接，格式类似：`https://notion.so/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=...`
4. Database ID 就是 URL 中的那串 32 位字符（去掉中间的短横线）

或者，直接从浏览器地址栏复制：
```
https://www.notion.so/workspace/DatabaseName-c98ca17d606b4028a74e3c513f101921
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                这部分就是 Database ID
```

## ❓ 常见问题

### 1. Actions 运行失败怎么办？

- 检查所有 Secrets 是否正确配置
- 查看 Actions 运行日志中的错误信息
- 确认 Notion 数据库已添加 Integration 连接

### 2. 如何查看运行日志？

1. 进入 **Actions** 标签页
2. 点击具体的运行记录
3. 点击 "运行期刊同步" 步骤查看详细日志
4. 也可以在 **Artifacts** 中下载完整日志文件

### 3. 如何暂停自动运行？

有两种方式：
1. 在 Notion 期刊订阅表中，取消勾选"是否启用订阅"
2. 禁用 GitHub Actions workflow：
   - 进入 **Actions** 标签页
   - 选择 "期刊订阅自动同步"
   - 点击右上角的 **...** → **Disable workflow**

## 📝 本地测试

在推送到 GitHub 之前，建议先在本地测试：

```bash
# 运行配置测试
python test_config.py

# 运行主程序
python journal_subscription_v2.py
```

## 🎉 完成

配置完成后，你的期刊订阅系统将：
- ✅ 每天自动运行
- ✅ 自动抓取新文章
- ✅ 自动翻译和分析
- ✅ 自动推送到 Notion
- ✅ 所有敏感信息安全存储

如有问题，请查看项目的 README.md 或提交 Issue。

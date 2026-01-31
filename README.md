# 期刊订阅系统

自动抓取学术期刊最新文章，翻译摘要，提取研究信息，推送到Notion数据库。

## 功能特性

- ✅ 自动从Crossref抓取期刊文章元数据
- ✅ 使用Claude API翻译标题和摘要
- ✅ 智能提取研究动机、问题和方法
- ✅ 生成每期期刊小结
- ✅ 自动推送到Notion数据库
- ✅ 支持定时运行和状态追踪

## 系统架构

```
Crossref API → Python脚本 → Claude API → Notion API
     ↓              ↓            ↓           ↓
  文章元数据     翻译提取      内容生成    数据存储
```

## 前置准备

### 1. Notion配置

已为你创建了三个数据库：
- **期刊订阅表**: https://www.notion.so/c98ca17d606b4028a74e3c513f101921
- **文章推送库**: https://www.notion.so/9dd8fb5ad12e49bbbbedfc91c864cdbd
- **期刊小结库**: https://www.notion.so/b053e2cae8b64b3e8d258c79d2542fc5

需要获取Notion API Key：
1. 访问 https://www.notion.so/my-integrations
2. 点击 "New integration"
3. 命名为 "Journal Subscription"
4. 复制 "Internal Integration Token"
5. 在每个数据库页面点击右上角 "..." → "Add connections" → 选择你的integration

### 2. Anthropic API Key

1. 访问 https://console.anthropic.com/
2. 在 API Keys 页面创建新密钥
3. 复制密钥

### 3. Python环境

要求 Python 3.8+

```bash
# 安装依赖
pip install -r requirements.txt
```

## 配置

### 方法1：使用配置文件（推荐）

复制模板并填写：

```bash
cp config.template.json config.json
```

编辑 `config.json`：

```json
{
  "notion": {
    "api_key": "secret_xxxxxxxxxxxxx",
    "databases": {
      "subscriptions": "bae82198-66b5-4ec5-a789-6839b1fc8e6f",
      "articles": "88b9dc7d-f5fc-4bbb-9fbe-940788a24d2e",
      "summaries": "0efabfe0-a199-4892-bf2c-9cd56eae7619"
    }
  },
  "anthropic": {
    "api_key": "sk-ant-xxxxxxxxxxxxx"
  }
}
```

### 方法2：使用环境变量

```bash
export NOTION_API_KEY="secret_xxxxxxxxxxxxx"
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"
export NOTION_DB_SUBSCRIPTIONS="bae82198-66b5-4ec5-a789-6839b1fc8e6f"
export NOTION_DB_ARTICLES="88b9dc7d-f5fc-4bbb-9fbe-940788a24d2e"
export NOTION_DB_SUMMARIES="0efabfe0-a199-4892-bf2c-9cd56eae7619"
```

## 使用方法

### 第一步：添加期刊订阅

在Notion的"期刊订阅表"中添加期刊：

| 字段 | 说明 | 示例 |
|------|------|------|
| Journal | 期刊名 | Nature Genetics |
| 是否启用订阅 | 勾选启用 | ✅ |
| Online ISSN | 在线ISSN | 1546-1718 |
| Print ISSN | 印刷ISSN（备选） | 1061-4036 |
| 起始抓取日期 | 从何时开始抓取 | 2024-01-01 |

**如何查找ISSN**：
- 访问期刊官网
- 或在 https://jcr.clarivate.com/jcr/home 搜索

### 第二步：运行脚本

```bash
# 手动运行一次
python journal_subscription_v2.py
```

运行过程：
1. 读取启用的期刊订阅
2. 从Crossref抓取文章元数据
3. 调用Claude翻译和提取信息
4. 推送到Notion文章库
5. 生成期刊小结
6. 更新订阅状态

### 第三步：查看结果

在Notion中查看：
- **文章推送库**：所有文章详情（含中文翻译）
- **期刊小结库**：每期期刊总结
- **期刊订阅表**：更新状态和日期

## 定时运行（可选）

### 使用 cron（Linux/Mac）

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每周一上午9点）
0 9 * * 1 cd /path/to/journal_subscription && /usr/bin/python3 journal_subscription_v2.py >> logs/cron.log 2>&1
```

### 使用 GitHub Actions

创建 `.github/workflows/journal-sync.yml`：

```yaml
name: 期刊订阅同步

on:
  schedule:
    - cron: '0 1 * * 1'  # 每周一北京时间9点
  workflow_dispatch:  # 手动触发

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: 安装依赖
        run: pip install -r requirements.txt
      
      - name: 运行同步
        env:
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          NOTION_DB_SUBSCRIPTIONS: ${{ secrets.NOTION_DB_SUBSCRIPTIONS }}
          NOTION_DB_ARTICLES: ${{ secrets.NOTION_DB_ARTICLES }}
          NOTION_DB_SUMMARIES: ${{ secrets.NOTION_DB_SUMMARIES }}
        run: python journal_subscription_v2.py
```

在GitHub仓库设置 Secrets：
- `NOTION_API_KEY`
- `ANTHROPIC_API_KEY`
- `NOTION_DB_SUBSCRIPTIONS`
- `NOTION_DB_ARTICLES`
- `NOTION_DB_SUMMARIES`

## 数据库字段说明

### 期刊订阅表

| 字段 | 类型 | 说明 |
|------|------|------|
| Journal | 标题 | 期刊名称 |
| 是否启用订阅 | 复选框 | 控制是否抓取该期刊 |
| Online ISSN | 文本 | 在线ISSN（主要） |
| Print ISSN | 文本 | 印刷ISSN（备用） |
| 起始抓取日期 | 日期 | 开始抓取的日期 |
| 最近处理日期 | 日期 | 系统最后运行时间 |
| 最近处理状态 | 文本 | 运行结果（成功/失败） |
| 最后更新日期 | 日期 | 最后一次抓到新文章的时间 |

### 文章推送库

| 字段 | 类型 | 说明 |
|------|------|------|
| Title | 标题 | 英文标题 |
| 标题 | 文本 | 中文标题（AI翻译） |
| Journal | 文本 | 期刊名 |
| Volume/Issue | 文本 | 卷号/期号 |
| Year | 数字 | 年份 |
| Year-Month | 文本 | 年-月 |
| YearQuarter | 文本 | 年-季度 |
| Author | 文本 | 作者列表 |
| Abstract | 文本 | 英文摘要 |
| 摘要 | 文本 | 中文摘要（AI翻译） |
| 研究动机和问题 | 文本 | AI提取 |
| 研究方法 | 文本 | AI提取 |
| Link | URL | 原文链接 |
| 上传日期 | 日期 | 推送日期 |

### 期刊小结库

| 字段 | 类型 | 说明 |
|------|------|------|
| Journal | 标题 | 期刊名 |
| Volume/Issue | 文本 | 卷号/期号 |
| Year | 数字 | 年份 |
| 文章数量 | 数字 | 该期文章数 |
| 小结 | 文本 | AI生成的小结 |
| 小结生成日期 | 日期 | 生成日期 |

## 常见问题

### Q: 抓不到文章怎么办？

**A:** 检查以下几点：
1. ISSN是否正确（尝试Online和Print两个）
2. 起始日期是否太久远（建议最多回溯6个月）
3. 该期刊是否在Crossref数据库中
4. 查看"最近处理状态"的错误信息

### Q: 翻译质量如何？

**A:** 使用Claude Sonnet 4，学术翻译质量很高。如需调整：
- 修改 `translate_and_extract()` 函数中的prompt
- 可以增加专业术语词典

### Q: 如何添加自定义字段？

**A:** 在Notion数据库中：
1. 直接添加新属性
2. **不要修改**现有属性的名称和类型
3. 脚本会忽略自定义字段，不影响运行

### Q: API调用费用？

**A:** 
- Crossref API：免费
- Claude API：按token计费
  - 翻译每篇文章约 500-2000 tokens
  - 每期小结约 500 tokens
  - 估算：订阅10个期刊，每周约$2-5

### Q: 可以订阅多少期刊？

**A:** 
- 技术上无限制
- 建议：10-30个（考虑运行时间和API费用）
- 单次运行时间：每个期刊约1-3分钟

## 高级配置

### 修改抓取数量

在 `fetch_articles_by_issn()` 函数中：

```python
works = cr.works(
    filter={...},
    limit=100,  # 改为需要的数量，最大1000
    ...
)
```

### 自定义翻译prompt

修改 `translate_and_extract()` 函数中的prompt，例如：

```python
prompt = f"""你是一个专业的{领域}学术翻译专家...
（根据你的研究领域定制）
"""
```

### 添加邮件通知

在 `main()` 函数末尾添加：

```python
import smtplib
from email.mime.text import MIMEText

def send_notification(summary):
    # 配置SMTP...
    pass
```

## 技术栈

- Python 3.8+
- [habanero](https://github.com/sckott/habanero) - Crossref API客户端
- [anthropic](https://github.com/anthropics/anthropic-sdk-python) - Claude API
- [requests](https://requests.readthedocs.io/) - Notion API调用

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 致谢

灵感来源于原Lucid期刊订阅项目。

# 快速开始指南

## 5分钟快速部署

### Step 1: 获取API密钥（2分钟）

#### Notion API Key
1. 打开 https://www.notion.so/my-integrations
2. 点击 "+ New integration"
3. 名称：`Journal Subscription`
4. 类型：Internal
5. 能力：勾选 "Read content", "Update content", "Insert content"
6. 点击 "Submit"
7. **复制 "Internal Integration Token"**（格式：secret_xxxx）

#### Anthropic API Key  
1. 打开 https://console.anthropic.com/
2. 注册/登录账号
3. 点击 "API Keys" → "+ Create Key"
4. **复制密钥**（格式：sk-ant-xxxx）

### Step 2: 连接数据库（1分钟）

打开你的三个Notion数据库，分别操作：

1. 点击右上角 "..."
2. 找到 "Add connections"
3. 搜索并选择 "Journal Subscription"

需要连接的数据库：
- ✅ 期刊订阅表
- ✅ 文章推送库  
- ✅ 期刊小结库

### Step 3: 配置脚本（1分钟）

```bash
# 克隆或下载代码
cd journal_subscription

# 创建配置文件
cp config.template.json config.json

# 编辑config.json，填入你的API密钥
nano config.json
```

`config.json` 内容：

```json
{
  "notion": {
    "api_key": "secret_你的Notion密钥",
    "databases": {
      "subscriptions": "bae82198-66b5-4ec5-a789-6839b1fc8e6f",
      "articles": "88b9dc7d-f5fc-4bbb-9fbe-940788a24d2e",
      "summaries": "0efabfe0-a199-4892-bf2c-9cd56eae7619"
    }
  },
  "anthropic": {
    "api_key": "sk-ant-你的Anthropic密钥"
  }
}
```

### Step 4: 安装依赖（30秒）

```bash
pip install -r requirements.txt
```

### Step 5: 添加期刊订阅（30秒）

在Notion的"期刊订阅表"中添加一个测试期刊：

- **Journal**: Nature Genetics
- **是否启用订阅**: ✅ 勾选
- **Online ISSN**: 1546-1718
- **起始抓取日期**: 2024-11-01

### Step 6: 运行！

```bash
python journal_subscription_v2.py
```

第一次运行可能需要几分钟，你会看到：

```
============================================================
期刊订阅系统 - 开始运行
运行时间: 2025-01-30 22:30:00
============================================================
找到 1 个启用的订阅

处理期刊: Nature Genetics (ISSN: 1546-1718)
抓取日期: 2024-11-01 至今
  找到 15 篇文章
  处理: Large-scale genomic analysis reveals...
  处理: CRISPR-based genome editing in...
  ...
  成功推送 15/15 篇文章
  生成小结: Volume 57, Issue 1

============================================================
运行完成
============================================================
```

### Step 7: 查看结果！

打开Notion，查看：
- **文章推送库**：看到15篇文章，含中文翻译
- **期刊小结库**：看到该期的小结

## 成功了！现在你可以：

### ✅ 添加更多期刊

常用期刊ISSN：

| 期刊 | Online ISSN |
|------|-------------|
| Nature | 1476-4687 |
| Science | 1095-9203 |
| Cell | 1097-4172 |
| Nature Genetics | 1546-1718 |
| PLOS Genetics | 1553-7404 |
| Genome Research | 1549-5469 |

### ✅ 设置定时运行

**Mac/Linux cron:**

```bash
# 每周一上午9点运行
0 9 * * 1 cd ~/journal_subscription && python3 journal_subscription_v2.py
```

**GitHub Actions（推荐）:**

1. Fork这个仓库到你的GitHub
2. 在仓库Settings → Secrets添加：
   - `NOTION_API_KEY`
   - `ANTHROPIC_API_KEY`
   - 其他数据库ID secrets
3. 启用Actions

### ✅ 自定义Notion视图

在文章推送库中：
- 创建看板视图：按期刊或季度分组
- 创建筛选：只看特定关键词
- 添加自定义属性：打标签、做笔记

## 常见问题

**Q: 报错 "Invalid API key"**  
A: 检查config.json中的密钥格式和权限

**Q: 找不到文章**  
A: 检查ISSN是否正确，可以在 https://www.crossref.org/ 验证

**Q: 翻译错误**  
A: Claude API可能临时故障，稍后重试

**Q: Notion写入失败**  
A: 确认数据库已连接integration

## 下一步

- 📖 阅读完整 [README.md](README.md)
- ⚙️ 了解高级配置和自定义
- 🚀 设置自动化运行

祝你使用愉快！如有问题欢迎提Issue。

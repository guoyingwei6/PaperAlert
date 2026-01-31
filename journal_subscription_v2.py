#!/usr/bin/env python3
"""
期刊订阅系统 v2.0 - 使用Notion官方API
自动抓取和推送学术期刊文章
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import anthropic
from habanero import Crossref
import requests

# ============== 配置加载 ==============
def load_config():
    """加载配置文件"""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    else:
        # 从环境变量读取配置
        anthropic_config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY', '')
        }

        # 支持自定义 base_url 和 model（可选）
        if os.getenv('ANTHROPIC_BASE_URL'):
            anthropic_config['base_url'] = os.getenv('ANTHROPIC_BASE_URL')
        if os.getenv('ANTHROPIC_MODEL'):
            anthropic_config['model'] = os.getenv('ANTHROPIC_MODEL')

        return {
            'notion': {
                'api_key': os.getenv('NOTION_API_KEY', ''),
                'databases': {
                    'subscriptions': os.getenv('NOTION_DB_SUBSCRIPTIONS', ''),
                    'articles': os.getenv('NOTION_DB_ARTICLES', ''),
                    'summaries': os.getenv('NOTION_DB_SUMMARIES', '')
                }
            },
            'anthropic': anthropic_config
        }

CONFIG = load_config()

# 验证配置
if not CONFIG['notion']['api_key']:
    raise ValueError("请设置Notion API Key")
if not CONFIG['anthropic']['api_key']:
    raise ValueError("请设置Anthropic API Key")

# 初始化客户端
cr = Crossref()

# 初始化Claude客户端（支持自定义base_url）
anthropic_config = {'api_key': CONFIG['anthropic']['api_key']}
if 'base_url' in CONFIG['anthropic']:
    anthropic_config['base_url'] = CONFIG['anthropic']['base_url']
claude_client = anthropic.Anthropic(**anthropic_config)

# 获取模型名称（使用配置中的模型或默认值）
CLAUDE_MODEL = CONFIG['anthropic'].get('model', 'claude-sonnet-4-20250514')

NOTION_VERSION = "2022-06-28"
NOTION_HEADERS = {
    "Authorization": f"Bearer {CONFIG['notion']['api_key']}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

# ============== Notion API 操作函数 ==============

def notion_query_database(database_id: str, filter_obj: Optional[Dict] = None) -> List[Dict]:
    """查询Notion数据库"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    
    payload = {}
    if filter_obj:
        payload['filter'] = filter_obj
    
    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"查询数据库失败: {response.text}")
        return []
    
    return response.json().get('results', [])

def notion_create_page(database_id: str, properties: Dict) -> bool:
    """在Notion数据库中创建页面"""
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    
    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"创建页面失败: {response.text}")
        return False
    
    return True

def notion_update_page(page_id: str, properties: Dict) -> bool:
    """更新Notion页面"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {"properties": properties}
    
    response = requests.patch(url, headers=NOTION_HEADERS, json=payload)
    
    return response.status_code == 200

def read_subscriptions() -> List[Dict]:
    """读取启用的期刊订阅"""
    db_id = CONFIG['notion']['databases']['subscriptions']
    
    # 查询启用订阅的期刊
    filter_obj = {
        "property": "是否启用订阅",
        "checkbox": {
            "equals": True
        }
    }
    
    pages = notion_query_database(db_id, filter_obj)
    
    subscriptions = []
    for page in pages:
        props = page['properties']
        
        sub = {
            'page_id': page['id'],
            'Journal': get_notion_title(props.get('Journal', {})),
            'Online ISSN': get_notion_rich_text(props.get('Online ISSN', {})),
            'Print ISSN': get_notion_rich_text(props.get('Print ISSN', {})),
            '起始抓取日期': get_notion_date(props.get('起始抓取日期', {})),
            '是否启用订阅': True
        }
        
        subscriptions.append(sub)
    
    return subscriptions

def write_article(article_data: Dict) -> bool:
    """写入文章到文章推送库"""
    db_id = CONFIG['notion']['databases']['articles']
    
    properties = {
        "Title": {"title": [{"text": {"content": article_data['title'][:2000]}}]},
        "标题": {"rich_text": [{"text": {"content": article_data.get('title_cn', '')[:2000]}}]},
        "Journal": {"rich_text": [{"text": {"content": article_data['journal'][:2000]}}]},
        "Volume": {"rich_text": [{"text": {"content": str(article_data.get('volume', ''))[:100]}}]},
        "Issue": {"rich_text": [{"text": {"content": str(article_data.get('issue', ''))[:100]}}]},
        "Year": {"number": article_data.get('year')},
        "Year-Month": {"rich_text": [{"text": {"content": article_data.get('year_month', '')[:50]}}]},
        "YearQuarter": {"rich_text": [{"text": {"content": article_data.get('quarter', '')[:50]}}]},
        "Author": {"rich_text": [{"text": {"content": article_data.get('author', '')[:2000]}}]},
        "Abstract": {"rich_text": [{"text": {"content": article_data.get('abstract', '')[:2000]}}]},
        "摘要": {"rich_text": [{"text": {"content": article_data.get('abstract_cn', '')[:2000]}}]},
        "研究动机和问题": {"rich_text": [{"text": {"content": article_data.get('motivation', '')[:2000]}}]},
        "研究方法": {"rich_text": [{"text": {"content": article_data.get('method', '')[:2000]}}]},
        "Link": {"url": article_data.get('url', '')[:2000] if article_data.get('url') else None},
        "上传日期": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
    }
    
    return notion_create_page(db_id, properties)

def write_summary(summary_data: Dict) -> bool:
    """写入期刊小结到小结库"""
    db_id = CONFIG['notion']['databases']['summaries']
    
    properties = {
        "Journal": {"title": [{"text": {"content": summary_data['journal'][:2000]}}]},
        "Volume": {"rich_text": [{"text": {"content": str(summary_data.get('volume', ''))[:100]}}]},
        "Issue": {"rich_text": [{"text": {"content": str(summary_data.get('issue', ''))[:100]}}]},
        "Year": {"number": summary_data.get('year')},
        "文章数量": {"number": summary_data.get('article_count', 0)},
        "小结": {"rich_text": [{"text": {"content": summary_data.get('summary', '')[:2000]}}]},
        "小结生成日期": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
    }
    
    return notion_create_page(db_id, properties)

def update_subscription_status(page_id: str, journal: str, status: str, last_update: Optional[str] = None):
    """更新期刊订阅表状态"""
    properties = {
        "最近处理日期": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
        "最近处理状态": {"rich_text": [{"text": {"content": status[:2000]}}]}
    }
    
    if last_update:
        properties["最后更新日期"] = {"date": {"start": last_update}}
    
    notion_update_page(page_id, properties)

# ============== Notion数据提取辅助函数 ==============

def get_notion_title(prop: Dict) -> str:
    """从Notion title属性提取文本"""
    if 'title' in prop and prop['title']:
        return prop['title'][0]['text']['content']
    return ''

def get_notion_rich_text(prop: Dict) -> str:
    """从Notion rich_text属性提取文本"""
    if 'rich_text' in prop and prop['rich_text']:
        return prop['rich_text'][0]['text']['content']
    return ''

def get_notion_date(prop: Dict) -> Optional[str]:
    """从Notion date属性提取日期"""
    if 'date' in prop and prop['date']:
        return prop['date']['start']
    return None

# ============== Crossref API 函数 ==============
# (保持之前的实现不变)

def fetch_articles_by_issn(issn: str, from_date: str, until_date: Optional[str] = None) -> List[Dict]:
    """根据ISSN抓取文章"""
    if not until_date:
        until_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        works = cr.works(
            filter={
                'issn': issn,
                'from-pub-date': from_date,
                'until-pub-date': until_date
            },
            limit=100,
            select=['DOI', 'title', 'author', 'abstract', 'published-print', 
                   'published-online', 'volume', 'issue', 'URL', 'container-title']
        )
        
        articles = []
        if works and 'message' in works and 'items' in works['message']:
            for item in works['message']['items']:
                article = parse_crossref_item(item)
                if article:
                    articles.append(article)
        
        return articles
        
    except Exception as e:
        print(f"抓取ISSN {issn} 文章失败: {e}")
        return []

def parse_crossref_item(item: Dict) -> Optional[Dict]:
    """解析Crossref返回的单篇文章数据"""
    try:
        title = item.get('title', [''])[0] if 'title' in item else ''
        
        authors = []
        if 'author' in item:
            for author in item['author'][:3]:
                given = author.get('given', '')
                family = author.get('family', '')
                authors.append(f"{given} {family}".strip())
        author_str = ', '.join(authors) if authors else ''
        if len(item.get('author', [])) > 3:
            author_str += ' et al.'
        
        abstract = item.get('abstract', '')
        
        pub_date = None
        if 'published-print' in item:
            date_parts = item['published-print'].get('date-parts', [[]])[0]
            if len(date_parts) >= 1:
                pub_date = f"{date_parts[0]}"
                if len(date_parts) >= 2:
                    pub_date += f"-{date_parts[1]:02d}"
        elif 'published-online' in item:
            date_parts = item['published-online'].get('date-parts', [[]])[0]
            if len(date_parts) >= 1:
                pub_date = f"{date_parts[0]}"
                if len(date_parts) >= 2:
                    pub_date += f"-{date_parts[1]:02d}"
        
        volume = item.get('volume', '')
        issue = item.get('issue', '')
        journal = item.get('container-title', [''])[0] if 'container-title' in item else ''
        doi = item.get('DOI', '')
        url = item.get('URL', f"https://doi.org/{doi}" if doi else '')
        
        year = int(pub_date.split('-')[0]) if pub_date else None
        year_month = pub_date if pub_date else ''
        quarter = None
        if year and '-' in pub_date:
            month = int(pub_date.split('-')[1])
            quarter = f"{year}Q{(month-1)//3 + 1}"
        else:
            quarter = f"{year}Q1" if year else ''
        
        return {
            'title': title,
            'author': author_str,
            'abstract': abstract,
            'journal': journal,
            'volume': volume,
            'issue': issue,
            'year': year,
            'year_month': year_month,
            'quarter': quarter,
            'doi': doi,
            'url': url,
            'pub_date': pub_date
        }
        
    except Exception as e:
        print(f"解析文章数据失败: {e}")
        return None

# ============== Claude API 函数 ==============
# (保持之前的实现不变)

def translate_and_extract(title: str, abstract: str) -> Dict[str, str]:
    """使用Claude翻译标题和摘要，并提取研究动机、问题、方法"""
    if not abstract:
        prompt = f"""请将以下英文标题翻译成中文：

标题：{title}

要求：
1. 翻译准确、符合学术规范
2. 直接输出中文标题，不要其他内容"""
        
        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        title_cn = response.content[0].text.strip()
        
        return {
            'title_cn': title_cn,
            'abstract_cn': '',
            'motivation': '',
            'method': ''
        }
    
    prompt = f"""请完成以下任务：

1. 将标题翻译成中文
2. 将摘要翻译成中文
3. 从摘要中提取研究动机和问题（2-3句话概括）
4. 从摘要中提取研究方法（2-3句话概括）

标题：{title}

摘要：{abstract}

请按以下JSON格式输出：
{{
  "title_cn": "中文标题",
  "abstract_cn": "中文摘要",
  "motivation": "研究动机和问题",
  "method": "研究方法"
}}

只输出JSON，不要其他内容。"""
    
    try:
        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text.strip()
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        return result
        
    except Exception as e:
        print(f"Claude API调用失败: {e}")
        return {
            'title_cn': title,
            'abstract_cn': abstract,
            'motivation': '',
            'method': ''
        }

def generate_issue_summary(articles: List[Dict]) -> str:
    """生成某一期的小结"""
    if len(articles) > 10:
        articles = articles[:10]
    
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"\n{i}. {article.get('title', '')}\n"
        if article.get('abstract'):
            articles_text += f"   摘要：{article['abstract'][:200]}...\n"
    
    prompt = f"""请为这一期期刊撰写一份小结（150-200字），内容包括：

1. 本期文章的主要研究主题和方向
2. 使用的主要研究方法
3. 整体研究趋势或特点

本期文章列表：{articles_text}

要求：
- 简洁概括，突出重点
- 客观中立
- 直接输出小结文本，不要前缀和标题"""
    
    try:
        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()
        
    except Exception as e:
        print(f"生成小结失败: {e}")
        return f"本期共收录{len(articles)}篇文章。"

# ============== 主流程 ==============

def process_journal(journal_data: Dict):
    """处理单个期刊的订阅"""
    journal_name = journal_data['Journal']
    page_id = journal_data['page_id']
    issn = journal_data.get('Online ISSN') or journal_data.get('Print ISSN')
    from_date = journal_data['起始抓取日期']
    
    if not issn:
        print(f"期刊 {journal_name} 缺少ISSN，跳过")
        update_subscription_status(page_id, journal_name, "错误：缺少ISSN")
        return
    
    if not from_date:
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"\n处理期刊: {journal_name} (ISSN: {issn})")
    print(f"抓取日期: {from_date} 至今")
    
    articles = fetch_articles_by_issn(issn, from_date)
    
    if not articles:
        print(f"  未找到新文章")
        update_subscription_status(page_id, journal_name, "成功：无新文章")
        return
    
    print(f"  找到 {len(articles)} 篇文章")
    
    success_count = 0
    for article in articles:
        try:
            print(f"  处理: {article['title'][:50]}...")
            enriched = translate_and_extract(article['title'], article['abstract'])
            
            article_data = {
                **article,
                **enriched
            }
            
            if write_article(article_data):
                success_count += 1
            
        except Exception as e:
            print(f"    处理文章失败: {e}")
            continue
    
    print(f"  成功推送 {success_count}/{len(articles)} 篇文章")
    
    # 按issue分组生成小结
    issue_groups = {}
    for article in articles:
        key = (article.get('volume', ''), article.get('issue', ''))
        if key not in issue_groups:
            issue_groups[key] = []
        issue_groups[key].append(article)
    
    for (volume, issue), issue_articles in issue_groups.items():
        if volume and issue:
            print(f"  生成小结: Volume {volume}, Issue {issue}")
            summary = generate_issue_summary(issue_articles)
            
            summary_data = {
                'journal': journal_name,
                'volume': volume,
                'issue': issue,
                'year': issue_articles[0].get('year'),
                'article_count': len(issue_articles),
                'summary': summary
            }
            
            write_summary(summary_data)
    
    status = f"成功：推送{success_count}篇文章"
    update_subscription_status(page_id, journal_name, status, datetime.now().strftime("%Y-%m-%d"))

def main():
    """主函数"""
    print("=" * 60)
    print("期刊订阅系统 - 开始运行")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    subscriptions = read_subscriptions()
    
    if not subscriptions:
        print("未找到启用的期刊订阅")
        return
    
    print(f"找到 {len(subscriptions)} 个启用的订阅")
    
    for sub in subscriptions:
        try:
            process_journal(sub)
        except Exception as e:
            print(f"处理期刊失败: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("运行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

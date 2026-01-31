#!/usr/bin/env python3
"""
配置测试脚本 - 验证API密钥和数据库连接
"""

import os
import json
import sys
import requests

def load_config():
    """加载配置"""
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    else:
        return {
            'notion': {
                'api_key': os.getenv('NOTION_API_KEY', ''),
                'databases': {
                    'subscriptions': os.getenv('NOTION_DB_SUBSCRIPTIONS', ''),
                    'articles': os.getenv('NOTION_DB_ARTICLES', ''),
                    'summaries': os.getenv('NOTION_DB_SUMMARIES', '')
                }
            },
            'anthropic': {
                'api_key': os.getenv('ANTHROPIC_API_KEY', '')
            }
        }

def test_notion_api(api_key):
    """测试Notion API连接"""
    print("\n📝 测试Notion API...")
    
    if not api_key:
        print("   ❌ 未配置Notion API Key")
        return False
    
    if not api_key.startswith('secret_') and not api_key.startswith('ntn_'):
        print(f"   ⚠️  API Key格式可能不正确（应该以'secret_'或'ntn_'开头）")
    
    # 测试API调用
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json={"page_size": 1}
        )
        
        if response.status_code == 200:
            print("   ✅ Notion API连接成功")
            return True
        elif response.status_code == 401:
            print("   ❌ Notion API Key无效")
            return False
        else:
            print(f"   ❌ Notion API错误: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

def test_notion_database(api_key, db_id, db_name):
    """测试Notion数据库连接"""
    print(f"\n🗄️  测试数据库: {db_name}...")
    
    if not db_id:
        print(f"   ❌ 未配置 {db_name} ID")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # 尝试查询数据库
        response = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers=headers,
            json={"page_size": 1}
        )
        
        if response.status_code == 200:
            print(f"   ✅ {db_name} 连接成功")
            return True
        elif response.status_code == 404:
            print(f"   ❌ 找不到 {db_name}（可能未添加integration连接）")
            print(f"   提示: 在Notion数据库页面点击'...' → 'Add connections' → 选择你的integration")
            return False
        elif response.status_code == 401:
            print(f"   ❌ {db_name} 权限不足")
            return False
        else:
            print(f"   ❌ {db_name} 错误: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

def test_anthropic_api(config_anthropic):
    """测试Anthropic API连接"""
    print("\n🤖 测试Anthropic API...")

    api_key = config_anthropic.get('api_key', '')
    base_url = config_anthropic.get('base_url', '')
    model = config_anthropic.get('model', 'claude-sonnet-4-20250514')

    if not api_key:
        print("   ❌ 未配置Anthropic API Key")
        return False

    # 检查是否使用自定义base_url（如阿里云）
    if base_url:
        print(f"   ℹ️  使用自定义API端点: {base_url}")
        print(f"   ℹ️  使用模型: {model}")
    elif not api_key.startswith('sk-ant-'):
        print(f"   ⚠️  API Key格式可能不正确（官方应该以'sk-ant-'开头）")

    try:
        import anthropic

        # 支持自定义base_url
        client_config = {'api_key': api_key}
        if base_url:
            client_config['base_url'] = base_url

        client = anthropic.Anthropic(**client_config)

        # 发送简单测试请求
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        if response.content:
            print("   ✅ Anthropic API连接成功")
            return True
        else:
            print("   ❌ Anthropic API响应异常")
            return False

    except Exception as e:
        error_msg = str(e)
        if 'authentication' in error_msg.lower() or 'api key' in error_msg.lower():
            print("   ❌ Anthropic API Key无效")
        else:
            print(f"   ❌ Anthropic API错误: {e}")
        return False

def test_crossref():
    """测试Crossref API连接"""
    print("\n🔬 测试Crossref API...")
    
    try:
        from habanero import Crossref
        
        cr = Crossref()
        
        # 测试查询
        result = cr.works(filter={'issn': '1546-1718'}, limit=1)
        
        if result and 'message' in result:
            print("   ✅ Crossref API连接成功")
            return True
        else:
            print("   ❌ Crossref API响应异常")
            return False
            
    except Exception as e:
        print(f"   ❌ Crossref API错误: {e}")
        return False

def main():
    """主测试流程"""
    print("=" * 60)
    print("期刊订阅系统 - 配置测试")
    print("=" * 60)
    
    # 加载配置
    print("\n📋 加载配置...")
    config = load_config()
    
    if os.path.exists('config.json'):
        print("   ✅ 找到 config.json")
    else:
        print("   ⚠️  未找到 config.json，使用环境变量")
    
    # 测试各个组件
    results = {
        'notion_api': False,
        'notion_db_subscriptions': False,
        'notion_db_articles': False,
        'notion_db_summaries': False,
        'anthropic_api': False,
        'crossref_api': False
    }
    
    # Notion API
    results['notion_api'] = test_notion_api(config['notion']['api_key'])
    
    # Notion数据库
    if results['notion_api']:
        results['notion_db_subscriptions'] = test_notion_database(
            config['notion']['api_key'],
            config['notion']['databases']['subscriptions'],
            "期刊订阅表"
        )
        results['notion_db_articles'] = test_notion_database(
            config['notion']['api_key'],
            config['notion']['databases']['articles'],
            "文章推送库"
        )
        results['notion_db_summaries'] = test_notion_database(
            config['notion']['api_key'],
            config['notion']['databases']['summaries'],
            "期刊小结库"
        )
    
    # Anthropic API
    results['anthropic_api'] = test_anthropic_api(config['anthropic'])
    
    # Crossref API
    results['crossref_api'] = test_crossref()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    if all_passed:
        print("\n🎉 所有测试通过！你可以开始运行脚本了。")
        print("\n运行命令:")
        print("  python journal_subscription_v2.py")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
        print("\n帮助:")
        print("  - 查看 QUICKSTART.md 获取详细配置步骤")
        print("  - 确保已获取正确的API密钥")
        print("  - 确保Notion数据库已添加integration连接")
        sys.exit(1)

if __name__ == "__main__":
    main()

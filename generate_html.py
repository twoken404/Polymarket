import json
from datetime import datetime, timezone

# 读取数据
with open('data.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# 开始生成 HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket 活跃事件</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #1a1a1a; }}
        .update-time {{ color: #666; margin-bottom: 30px; }}
        .event {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .event-title {{ font-size: 1.4rem; font-weight: 600; color: #0b5e8e; margin-bottom: 15px; }}
        .event-meta {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 15px; background: #f8fafc; padding: 12px; border-radius: 8px; }}
        .meta-item {{ flex: 1 1 200px; }}
        .meta-label {{ font-weight: 500; color: #2c3e50; }}
        .description {{ color: #374151; line-height: 1.6; margin-bottom: 20px; }}
        .markets-title {{ font-weight: 600; margin: 20px 0 10px; color: #1e293b; }}
        .market {{ background: #f1f5f9; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 15px; }}
        .market-question {{ font-weight: 500; color: #0f172a; margin-bottom: 10px; }}
        .outcomes {{ display: flex; gap: 15px; margin: 10px 0; flex-wrap: wrap; }}
        .outcome {{ padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: 500; }}
        .outcome.Yes {{ background: #dbeafe; color: #1e40af; }}
        .outcome.No {{ background: #fee2e2; color: #991b1b; }}
        .market-volume {{ color: #475569; font-size: 0.9rem; }}
        hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 15px 0; }}
        .footer {{ text-align: center; margin-top: 40px; color: #6b7280; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Polymarket 活跃事件</h1>
        <div class="update-time">更新于：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div>
"""

for event in events:
    # 事件基本信息
    title = event.get('title') or event.get('ticker') or '未知事件'
    start = event.get('startDate', '')[:10]
    end = event.get('endDate', '')[:10]
    liquidity = event.get('liquidity', 0)
    volume_24h = event.get('volume24hr', 0)
    description = event.get('description', '')[:200] + ('...' if len(event.get('description', '')) > 200 else '')

    # 确保数字格式正确
    try:
        liquidity = float(liquidity) if liquidity else 0
    except (ValueError, TypeError):
        liquidity = 0
        
    try:
        volume_24h = float(volume_24h) if volume_24h else 0
    except (ValueError, TypeError):
        volume_24h = 0

    html += f"""
        <div class="event">
            <div class="event-title">{title}</div>
            <div class="event-meta">
                <div class="meta-item"><span class="meta-label">开始：</span>{start}</div>
                <div class="meta-item"><span class="meta-label">结束：</span>{end}</div>
                <div class="meta-item"><span class="meta-label">流动性：</span>${liquidity:,.2f}</div>
                <div class="meta-item"><span class="meta-label">24h 交易量：</span>${volume_24h:,.2f}</div>
            </div>
            <div class="description">{description}</div>
    """

    # 子市场
    markets = event.get('markets', [])
    if markets:
        html += '<div class="markets-title">📈 子市场</div>'
        for market in markets:
            question = market.get('question', '未知问题')
            volume = market.get('volume', 0)
            
            # 确保交易量是数字
            try:
                volume = float(volume) if volume else 0
            except (ValueError, TypeError):
                volume = 0
            
            outcome_prices = market.get('outcomePrices', '[]')
            outcomes = market.get('outcomes', '["Yes","No"]')
            
            try:
                # 解析 JSON 字符串
                if isinstance(outcome_prices, str):
                    prices = json.loads(outcome_prices)
                else:
                    prices = outcome_prices
                    
                if isinstance(outcomes, str):
                    outcomes_list = json.loads(outcomes)
                else:
                    outcomes_list = outcomes
            except:
                prices = [0, 0]
                outcomes_list = ['Yes', 'No']

            outcomes_html = ''
            for i, outcome in enumerate(outcomes_list):
                if i < len(prices):
                    try:
                        # 确保价格是数字
                        price = float(prices[i])
                        prob = price * 100
                    except (ValueError, TypeError):
                        prob = 0
                else:
                    prob = 0
                    
                outcomes_html += f'<span class="outcome {outcome}">{outcome}: {prob:.1f}%</span>'

            html += f"""
            <div class="market">
                <div class="market-question">{question}</div>
                <div class="outcomes">{outcomes_html}</div>
                <div class="market-volume">📊 交易量：${volume:,.2f}</div>
            </div>
            """
    else:
        html += '<p>无子市场信息</p>'

    html += '</div>'

html += """
        <hr>
        <div class="footer">
            ⚡ 数据每日自动更新 · 原始 JSON 文件：<a href="data.json" target="_blank">data.json</a>
        </div>
    </div>
</body>
</html>
"""

# 写入文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ index.html 生成成功")
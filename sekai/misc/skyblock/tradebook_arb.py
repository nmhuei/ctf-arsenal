#!/usr/bin/env python3
"""
Tradebook arbitrage calculator for Sekai CTF Skyblock.
Parses tradebook data and finds mispriced items.
"""
import re

def parse_tradebook_list(text):
    """Parse tradebook list output to extract buy/sell orders."""
    lines = text.strip().split('\n')
    trades = []

    for line in lines:
        # Pattern 1: "[ID:1] [Diamond] x64 for $100 - /tradebook buy 1"
        m = re.search(r'\[ID:(\d+)\]\s+\[(.+?)\]\s+x(\d+)\s+for\s+\$?(\d+)', line)
        if m:
            trades.append({
                'id': int(m.group(1)),
                'item': m.group(2).strip(),
                'amount': int(m.group(3)),
                'price': int(m.group(4)),
                'type': 'offer'
            })
            continue

        # Pattern 2: "Buying Diamond x64 for $80 - /tradebook sell 5"
        m = re.search(r'(Buying|Selling)\s+(.+?)\s+x(\d+)\s+for\s+\$?(\d+)', line, re.I)
        if m:
            trades.append({
                'type': m.group(1).lower(),
                'item': m.group(2).strip(),
                'amount': int(m.group(3)),
                'price': int(m.group(4)),
            })
            continue

    return trades


def find_arbitrage(trades):
    """
    Find items where buying price < selling price (inverted pricing).
    Returns (buy, sell) pairs per item.
    """
    sells = {}  # item -> list of sell offers (price, amount)
    buys = {}   # item -> list of buy orders (price, amount)

    for t in trades:
        item = t['item'].lower()
        if t['type'] == 'selling' or 'offer' in str(t.get('type', '')):
            if item not in sells:
                sells[item] = []
            sells[item].append(t)
        elif t['type'] == 'buying':
            if item not in buys:
                buys[item] = []
            buys[item].append(t)

    opportunities = []
    all_items = set(sells.keys()) | set(buys.keys())

    for item in all_items:
        item_sells = sells.get(item, [])
        item_buys = buys.get(item, [])

        for sell in item_sells:
            for buy in item_buys:
                if buy['price'] > sell['price']:
                    profit_per_unit = buy['price'] - sell['price']
                    max_units = min(sell['amount'], buy['amount'])
                    total_profit = profit_per_unit * max_units

                    opportunities.append({
                        'item': item,
                        'buy_price': sell['price'],
                        'sell_price': buy['price'],
                        'profit_per_unit': profit_per_unit,
                        'max_units': max_units,
                        'total_profit': total_profit,
                        'buy_id': sell.get('id', '?'),
                        'sell_id': buy.get('id', '?'),
                    })

    opportunities.sort(key=lambda x: x['total_profit'], reverse=True)
    return opportunities


if __name__ == '__main__':
    # Test with sample data
    sample = """
[ID:1] [Diamond] x64 for $100 - /tradebook buy 1
Buying Diamond x64 for $80 - /tradebook sell 5
[ID:3] [Iron Ingot] x64 for $20 - /tradebook buy 3
Buying Iron Ingot x32 for $50 - /tradebook sell 6
"""
    print("=== Sample parse ===")
    trades = parse_tradebook_list(sample)
    for t in trades:
        print(f"  {t['type']:8s} {t['item']:15s} x{t['amount']:<4d} @ ${t['price']:<5d}")

    print("\n=== Arbitrage ===")
    ops = find_arbitrage(trades)
    if ops:
        for o in ops:
            print(f"  {o['item']}: buy @ ${o['buy_price']} / sell @ ${o['sell_price']} = ${o['profit_per_unit']}/unit profit")
    else:
        print("  No arbitrage found")
        # Inverted pricing would be: selling at $20, buying at $50 -> $30 profit per unit
        print("  (iron ingot example: sell to server @ $50, buy from player @ $20)")

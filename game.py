#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币大冒险 - 文字冒险游戏
玩家从1000元本金开始，在加密货币世界里闯荡
"""

import json
import os
import random
import sys
import time

# ============================================================
# 存档路径
# ============================================================
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")

# ============================================================
# ASCII 艺术
# ============================================================
TITLE_ART = r"""
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║    ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗        ║
  ║   ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗      ║
  ║   ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║      ║
  ║   ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║      ║
  ║   ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝      ║
  ║    ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝       ║
  ║                                                              ║
  ║          💰  加 密 货 币 大 冒 险  💰                        ║
  ║                                                              ║
  ║       "从1000块到财富自由，或者一无所有"                      ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
"""

WALLET_ART = r"""
    ┌─────────────────────────┐
    │  💰 数字钱包             │
    │  ─────────────────────  │
    │  余额: {balance:>10.2f} CNY   │
    │  持仓: {holdings}          │
    │  荣誉: {reputation}          │
    └─────────────────────────┘
"""

ENDING_ART = r"""
  ╔══════════════════════════════════════════════════════════════╗
  ║                     🏁 游戏结束 🏁                          ║
  ╚══════════════════════════════════════════════════════════════╝
"""

# 各种结局 ASCII
ENDINGS = {
    "暴富": """
    ┌────────────────────────────────────────┐
    │          🎉 恭喜！你暴富了！🎉         │
    │                                        │
    │        💰💰💰💰💰💰💰💰💰💰           │
    │       💰  财 富 自 由 达 成  💰         │
    │        💰💰💰💰💰💰💰💰💰💰           │
    │                                        │
    │   你从1000块起步，现在身价百万。         │
    │   辞职、买房、环球旅行，人生赢家！       │
    │                                        │
    │   但记住：赚到的钱，守不住也是白搭。     │
    └────────────────────────────────────────┘
    """,
    "破产": """
    ┌────────────────────────────────────────┐
    │           💀 你破产了... 💀             │
    │                                        │
    │        ┌─────────────────┐             │
    │        │   余额: 0.00    │             │
    │        │   负债: 一大堆   │             │
    │        └─────────────────┘             │
    │                                        │
    │   1000块打了水漂，还欠了一屁股债。      │
    │   回去老老实实上课吧，韭菜。             │
    └────────────────────────────────────────┘
    """,
    "被割韭菜": """
    ┌────────────────────────────────────────┐
    │         🥬 你被割韭菜了 🥬              │
    │                                        │
    │        ✂️ ~~~~~~🥬 ~~~~~~              │
    │                                        │
    │   "老师"跑路了，群解散了，               │
    │   你的钱跟着一起消失了。                 │
    │                                        │
    │   教训：天上不会掉馅饼，                 │
    │   但会掉镰刀。                           │
    └────────────────────────────────────────┘
    """,
    "大佬": """
    ┌────────────────────────────────────────┐
    │       👑 你成了币圈大佬 👑              │
    │                                        │
    │        🏆 Hall of Crypto 🏆            │
    │                                        │
    │   你不仅赚到了钱，还建立了               │
    │   自己的项目和社区。                     │
    │   Twitter粉丝十万，每次发推               │
    │   都能带飞一个币。                       │
    │                                        │
    │   "在币圈，最重要的是认知。" — 你        │
    └────────────────────────────────────────┘
    """,
    "钻石手": """
    ┌────────────────────────────────────────┐
    │       💎 钻石手成就达成！💎             │
    │                                        │
    │        💎🙌💎🙌💎🙌💎                  │
    │                                        │
    │   你HODL住了！在所有人恐慌抛售时         │
    │   你纹丝不动。三年后，你的               │
    │   BTC翻了20倍。                         │
    │                                        │
    │   钻石手不是死拿，是看懂了周期。         │
    └────────────────────────────────────────┘
    """,
    "监管": """
    ┌────────────────────────────────────────┐
    │       ⚖️ 被请去喝茶了 ⚖️               │
    │                                        │
    │        🍵 + 👮 = 😰                    │
    │                                        │
    │   你的交易所账户被冻结，                 │
    │   银行卡也被风控了。                     │
    │   虽然最后没事，但钱取不出来，           │
    │   等于白忙一场。                         │
    │                                        │
    │   教训：合规很重要，别踩红线。           │
    └────────────────────────────────────────┘
    """,
    "教授": """
    ┌────────────────────────────────────────┐
    │     🎓 你成了加密货币教授 🎓            │
    │                                        │
    │        📚 + 💻 = 🧠                    │
    │                                        │
    │   你发现自己真正热爱的是技术本身。       │
    │   从生物科学跨行到区块链研究，           │
    │   发了几篇论文，在大学开了课。           │
    │                                        │
    │   钱没赚多少，但找到了人生方向。         │
    └────────────────────────────────────────┘
    """,
    "归零": """
    ┌────────────────────────────────────────┐
    │          🔥 归零了... 🔥                │
    │                                        │
    │     ┌──────────────────────┐           │
    │     │  ██████████████████  │           │
    │     │  █  1000 → 0.00   █  │           │
    │     │  ██████████████████  │           │
    │     └──────────────────────┘           │
    │                                        │
    │   合约爆仓，一夜回到解放前。             │
    │   记住：合约是赌场，不是投资。           │
    └────────────────────────────────────────┘
    """,
}


# ============================================================
# 游戏状态
# ============================================================
class GameState:
    """管理玩家状态"""

    def __init__(self):
        self.balance = 1000.0  # 现金余额（人民币）
        self.holdings = {}  # 持仓 {币种: 数量}
        self.reputation = 0  # 声望值
        self.knowledge = 0  # 加密知识等级
        self.items = []  # 背包物品
        self.chapter = 1  # 当前章节
        self.history = []  # 选择历史
        self.flags = {}  # 剧情标记
        self.name = "无名氏"
        self.day = 1  # 游戏内天数
        self.stress = 0  # 压力值
        self.ending = None  # 结局类型

    def add_item(self, item):
        """添加物品到背包"""
        if item not in self.items:
            self.items.append(item)
            return True
        return False

    def has_item(self, item):
        """检查是否拥有某物品"""
        return item in self.items

    def remove_item(self, item):
        """移除物品"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def get_holdings_str(self):
        """获取持仓字符串"""
        if not self.holdings:
            return "空仓"
        parts = []
        for coin, amount in self.holdings.items():
            if amount > 0:
                parts.append(f"{coin}: {amount:.4f}")
        return ", ".join(parts) if parts else "空仓"

    def total_value(self):
        """估算总资产（简化版）"""
        # 简化估价
        prices = {"BTC": 450000, "ETH": 25000, "DOGE": 0.8, "SHIB": 0.0001,
                  "SOL": 800, "MATIC": 5, "BNB": 3500, "山寨币": 1}
        total = self.balance
        for coin, amount in self.holdings.items():
            total += amount * prices.get(coin, 1)
        return total

    def save(self):
        """保存游戏"""
        data = {
            "balance": self.balance,
            "holdings": self.holdings,
            "reputation": self.reputation,
            "knowledge": self.knowledge,
            "items": self.items,
            "chapter": self.chapter,
            "history": self.history,
            "flags": self.flags,
            "name": self.name,
            "day": self.day,
            "stress": self.stress,
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True

    @classmethod
    def load(cls):
        """加载存档"""
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            state = cls()
            for k, v in data.items():
                if hasattr(state, k):
                    setattr(state, k, v)
            return state
        except (json.JSONDecodeError, KeyError):
            return None


# ============================================================
# 工具函数
# ============================================================
def clear_screen():
    """清屏"""
    os.system("cls" if os.name == "nt" else "clear")


def slow_print(text, delay=0.03):
    """逐字打印，营造氛围"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def show_status(state):
    """显示玩家状态"""
    print("\n" + "─" * 50)
    print(f"  📅 第{state.day}天 | 💰 余额: ¥{state.balance:.2f} | "
          f"📊 知识: Lv.{state.knowledge} | ⚡ 压力: {state.stress}")
    if state.holdings:
        print(f"  📦 持仓: {state.get_holdings_str()}")
    if state.items:
        print(f"  🎒 背包: {', '.join(state.items)}")
    print("─" * 50)


def show_inventory(state):
    """显示详细背包"""
    print("\n" + "=" * 50)
    print("  🎒 背包系统")
    print("=" * 50)
    print(f"  💵 现金: ¥{state.balance:.2f}")
    print(f"  📊 知识等级: Lv.{state.knowledge}")
    print(f"  ⭐ 声望: {state.reputation}")
    print(f"  ⚡ 压力值: {state.stress}/100")
    print(f"  📅 第{state.day}天")
    print(f"\n  📦 数字资产:")
    if state.holdings:
        for coin, amount in state.holdings.items():
            if amount > 0:
                print(f"     • {coin}: {amount:.6f}")
    else:
        print("     （空仓）")
    print(f"\n  🎒 物品:")
    if state.items:
        for item in state.items:
            print(f"     • {item}")
    else:
        print("     （空的）")
    print("=" * 50)


def get_choice(max_val):
    """获取玩家选择，支持特殊命令"""
    while True:
        try:
            raw = input("\n👉 你的选择: ").strip()
            if raw.lower() == "q":
                confirm = input("确定退出？(y/n): ").strip().lower()
                if confirm == "y":
                    state.save()
                    print("游戏已保存，下次见！👋")
                    sys.exit(0)
            elif raw.lower() == "s":
                state.save()
                print("✅ 游戏已保存！")
                continue
            elif raw.lower() == "i":
                show_inventory(state)
                continue
            elif raw.lower() == "h":
                print("\n💡 提示:")
                print("  输入数字做选择 | s=存档 | i=背包 | h=帮助 | q=退出")
                continue
            choice = int(raw)
            if 1 <= choice <= max_val:
                return choice
            print(f"请输入 1-{max_val} 之间的数字")
        except ValueError:
            print("输入数字，或者 s=存档 i=背包 h=帮助 q=退出")


def random_event(state):
    """随机事件，增加不确定性"""
    events = [
        ("📱 手机推送：BTC突然暴涨10%！", lambda s: setattr(s, "balance",
            s.balance + s.holdings.get("BTC", 0) * 45000)),
        ("📉 市场闪崩！所有币跌了15%", lambda s: [
            s.holdings.update({k: v * 0.85 for k, v in s.holdings.items()}),
            setattr(s, "stress", min(100, s.stress + 15))
        ]),
        ("🎉 你之前关注的空投项目发币了！", lambda s: [
            s.add_item("空投代币 x1000"),
            setattr(s, "balance", s.balance + 200)
        ]),
        ("😵 连续熬夜看盘，你感冒了", lambda s: setattr(s, "stress",
            min(100, s.stress + 20))),
        ("📰 你写的加密科普文章火了", lambda s: setattr(s, "reputation",
            s.reputation + 10)),
        ("🎲 朋友拉你玩链游，你赢了点小钱", lambda s: setattr(s, "balance",
            s.balance + 50)),
    ]
    if random.random() < 0.3:  # 30% 概率触发随机事件
        event = random.choice(events)
        print(f"\n🎲 随机事件: {event[0]}")
        event[1](state)


# ============================================================
# 章节内容
# ============================================================

def chapter1_intro(state):
    """第一章：初入币圈"""
    clear_screen()
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║           第一章：初入币圈                           ║
  ║           "室友靠比特币买了辆车"                      ║
  ╚══════════════════════════════════════════════════════╝
    """)
    show_status(state)

    slow_print("\n你是一个普通大学生，每个月生活费1500。")
    slow_print("有一天，室友小王开着新车来接你。")
    slow_print('「靠，你哪来的钱？」你问。')
    slow_print('「比特币啊兄弟！去年投了5000，现在翻了好几倍！」')
    slow_print("\n你心动了。你存了1000块，准备试试运气。")
    slow_print("但是，该怎么开始呢？\n")

    print("  [1] 直接去币安注册，买BTC（正规交易所）")
    print('  [2] 跟着小王买他说的「百倍币」（听朋友的）')
    print("  [3] 先学习再说，去B站看教程（稳一手）")
    print('  [4] 加一个「币圈老师」的微信群（找组织）')
    print("  [5] 把钱存着，观望观望（保守派）")

    choice = get_choice(5)
    state.history.append(f"1-{choice}")

    if choice == 1:
        slow_print("\n你打开手机，注册了币安账户。")
        slow_print("KYC认证花了半小时，终于搞定了。")
        slow_print("你用1000块买了 0.0022 个BTC。")
        state.holdings["BTC"] = 0.0022
        state.balance = 0
        state.add_item("币安账户")
        state.knowledge += 1
        state.flags["交易所"] = "币安"
        print("\n💡 获得知识：KYC = Know Your Customer，交易所的身份验证")

    elif choice == 2:
        slow_print('\n小王给你推荐了一个叫「火星币」的山寨币。')
        slow_print('「这个项目方很有实力的，肯定能涨！」')
        slow_print("你用1000块买了一堆火星币。")
        state.holdings["山寨币"] = 1000
        state.balance = 0
        state.add_item("小王的推荐笔记")
        state.flags["山寨币"] = True
        print("\n💡 获得知识：山寨币 = Altcoin，非比特币的加密货币")

    elif choice == 3:
        slow_print("\n你打开B站，搜了'比特币入门'。")
        slow_print("看了3个小时的视频，你大概搞懂了：")
        slow_print("- BTC是数字黄金，总量2100万枚")
        slow_print("- ETH是智能合约平台，可以跑程序")
        slow_print("- 交易所是买卖币的地方")
        state.knowledge += 3
        state.add_item("B站学习笔记")
        state.day += 3
        print("\n💡 获得知识：区块链、公钥私钥、交易所的基本概念")

    elif choice == 4:
        slow_print('\n你加了一个叫「币圈暴富群」的微信群。')
        slow_print('「老师」每天发K线分析，推荐买入时机。')
        slow_print('群里天天有人晒收益截图，看起来都很赚钱。')
        state.add_item("微信币圈群")
        state.flags["骗子群"] = True
        state.reputation -= 5
        print("\n💡 获得知识：杀猪盘 = 先给你甜头，再让你加大投入，最后跑路")

    elif choice == 5:
        slow_print("\n你觉得这事儿不靠谱，决定先观望。")
        slow_print("但是每天看室友赚的钱越来越多，你心里痒痒的...")
        state.stress += 10
        state.flags["观望"] = True
        print("\n💡 获得知识：FOMO = Fear Of Missing Out，害怕错过")

    state.day += 1
    state.save()


def chapter2_first_trade(state):
    """第二章：第一次操作"""
    clear_screen()
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║           第二章：第一次操作                         ║
  ║           "涨了！我是不是天才？"                      ║
  ╚══════════════════════════════════════════════════════╝
    """)
    show_status(state)

    # 根据第一章的选择推进剧情
    if state.has_item("币安账户"):
        slow_print("\n你在币安买的BTC涨了5%！你的1000变成了1050。")
        slow_print("你兴奋得睡不着觉，脑子里全是K线图。")
        state.balance = 1050
        state.holdings = {}
    elif state.has_item("山寨币"):
        slow_print("\n你的火星币...跌了40%。")
        slow_print("小王说「没事，抄底加仓！」")
        slow_print("你的1000变成了600。")
        state.balance = 600
        state.holdings = {}
    elif state.has_item("B站学习笔记"):
        slow_print("\n经过三天的学习，你终于准备出手了。")
        slow_print("你对市场有了基本了解，知道不能All in。")
        state.knowledge += 2
    elif state.has_item("微信币圈群"):
        slow_print('\n「老师」说有个新币要上交易所，现在买入翻十倍。')
        slow_print("群里已经有人晒了大额买入截图。")
    else:
        slow_print("\n观望了一周，BTC涨了15%。你后悔了。")
        slow_print("你决定不能再等了。")
        state.stress += 15

    print(f"\n你的余额: ¥{state.balance:.2f}")
    print("\n接下来你要怎么做？\n")

    print("  [1] 把所有钱买BTC，然后卸载APP（长线持有）")
    print("  [2] 学习合约交易，加杠杆搏一搏（高风险）")
    print("  [3] 分散投资：50% BTC + 30% ETH + 20% 山寨币")
    if state.flags.get("骗子群"):
        print("  [4] 跟着'老师'买他推荐的新币")
    else:
        print("  [4] 参加币安的新币挖矿（质押挖矿）")
    print("  [5] 研究一下空投，白嫖它一波")

    choice = get_choice(5)
    state.history.append(f"2-{choice}")

    if choice == 1:
        slow_print("\n你用所有钱买了BTC，然后卸载了币安APP。")
        slow_print("室友说你傻，但你觉得长期持有才是王道。")
        state.holdings["BTC"] = state.balance / 450000
        state.balance = 0
        state.add_item("硬件钱包（模拟）")
        state.flags["HODL"] = True
        print("\n💡 获得知识：HODL = Hold On for Dear Life，死拿不卖")

    elif choice == 2:
        slow_print("\n你打开合约交易页面，研究了半天。")
        slow_print("看起来很简单：看涨就做多，看跌就做空。")
        slow_print("你决定开一个20倍杠杆的多单。")
        if random.random() < 0.4:
            slow_print("运气不错！涨了2%，你的钱翻了一番！")
            state.balance *= 2
            state.knowledge += 1
        else:
            slow_print("市场一个回调，你被强制平仓了。")
            slow_print("20倍杠杆意味着跌5%你就归零。")
            state.balance *= 0.1
            state.stress += 30
            print("\n💡 获得知识：强制平仓 = 爆仓，杠杆越高风险越大")
        state.add_item("合约交易经验（血泪教训）")
        state.flags["合约"] = True

    elif choice == 3:
        slow_print("\n你做了个简单的配置：")
        half = state.balance * 0.5
        eth_part = state.balance * 0.3
        alt_part = state.balance * 0.2
        state.holdings["BTC"] = half / 450000
        state.holdings["ETH"] = eth_part / 25000
        state.holdings["山寨币"] = alt_part
        state.balance = 0
        state.knowledge += 2
        state.add_item("投资组合方案")
        print("\n💡 获得知识：分散投资可以降低风险，但也会稀释收益")

    elif choice == 4:
        if state.flags.get("骗子群"):
            slow_print('\n你跟着「老师」买了推荐的新币。')
            slow_print("第一天涨了50%！你兴奋极了！")
            slow_print('「老师」说再加仓，肯定能翻倍。')
            state.balance *= 1.5
            state.flags["上钩"] = True
            print("\n💡 获得知识：这就是'拉盘'，先让你赚钱，后面才是收割")
        else:
            slow_print("\n你参加了币安的新币挖矿（Launchpool）。")
            slow_print("质押BNB就能免费挖新币，年化还不错。")
            state.add_item("Launchpool经验")
            state.knowledge += 2
            state.balance += 100
            print("\n💡 获得知识：质押挖矿 = Staking，把币锁起来赚收益")

    elif choice == 5:
        slow_print("\n你研究了空投（Airdrop）的概念。")
        slow_print("有些新项目为了推广，会免费发代币给用户。")
        slow_print("你花了一晚上做了几个测试网交互。")
        state.knowledge += 3
        state.add_item("空投猎手指南")
        state.balance += 50  # 小回报
        state.flags["空投"] = True
        print("\n💡 获得知识：空投 = Airdrop，项目方免费发的代币")

    state.day += 3
    random_event(state)
    state.save()


def chapter3_market_crash(state):
    """第三章：市场风暴"""
    clear_screen()
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║           第三章：市场风暴                           ║
  ║           "一天跌了30%，世界末日"                     ║
  ╚══════════════════════════════════════════════════════╝
    """)
    show_status(state)

    slow_print("\n凌晨3点，你被手机震醒了。")
    slow_print("打开行情APP，满屏的红色。")
    slow_print("BTC一天跌了25%，ETH跌了35%。")
    slow_print("社交媒体上全是'牛市结束了'的帖子。")
    slow_print("\n你的心脏在狂跳。你的持仓在疯狂缩水。\n")

    # 资产大幅缩水
    if state.holdings:
        for coin in state.holdings:
            state.holdings[coin] *= 0.6
        slow_print(f"你的持仓缩水了40%！")
    if state.balance > 0:
        pass  # 现金不受影响

    state.stress += 25

    print(f"\n当前余额: ¥{state.balance:.2f}")
    print(f"当前持仓: {state.get_holdings_str()}")
    print("\n你会怎么做？\n")

    print("  [1] 恐慌抛售！清仓止损！（割肉离场）")
    print("  [2] 死拿不卖，相信牛市会回来（HODL）")
    print("  [3] 别人恐惧我贪婪，抄底加仓！（逆向操作）")
    print("  [4] 关掉APP，去操场跑两圈冷静一下")
    print("  [5] 去论坛看看大家怎么说再决定")

    choice = get_choice(5)
    state.history.append(f"3-{choice}")

    if choice == 1:
        slow_print("\n你颤抖着手指，一键清仓。")
        total = state.balance + sum(state.holdings.values())
        state.balance = total * 0.6  # 亏损卖出
        state.holdings = {}
        slow_print(f"你止损了，拿回了 ¥{state.balance:.2f}")
        state.stress -= 10
        print("\n💡 获得知识：止损 = Cut Loss，控制亏损是生存技能")

    elif choice == 2:
        slow_print("\n你咬着牙，决定死拿。")
        slow_print("你关掉了行情APP，强迫自己不看。")
        if state.flags.get("HODL"):
            slow_print("你之前就是长线策略，这次考验你的信念。")
            state.knowledge += 2
            state.flags["钻石手考验"] = True
        else:
            state.stress += 20
        print("\n💡 获得知识：真正的HODLer经历过无数次暴跌")

    elif choice == 3:
        slow_print("\n你想起巴菲特的话：别人恐惧我贪婪。")
        if state.balance > 200:
            invest = state.balance * 0.5
            state.holdings["BTC"] = state.holdings.get("BTC", 0) + invest / 450000
            state.balance -= invest
            slow_print(f"你抄底了 ¥{invest:.2f} 的BTC。")
            state.knowledge += 2
            state.flags["抄底"] = True
        else:
            slow_print("但是你已经没什么钱了...")
            state.stress += 15
        print("\n💡 获得知识：抄底需要勇气，也需要资金管理")

    elif choice == 4:
        slow_print("\n你关掉手机，穿着拖鞋就冲向操场。")
        slow_print("跑了3圈，大汗淋漓。")
        slow_print("你突然觉得，一个软件里的数字，不值得你失眠。")
        state.stress = max(0, state.stress - 30)
        state.knowledge += 1
        print("\n💡 获得知识：心理健康 > 一切投资收益")

    elif choice == 5:
        slow_print("\n你打开了推特和Reddit。")
        slow_print("满屏都是'抄底''割肉''归零'的讨论。")
        slow_print("你看到一个老韭菜的帖子：")
        slow_print('「2018年我亏了80%，但我没卖。2021年我回本了还赚了10倍。」')
        slow_print("你决定...再想想。")
        state.knowledge += 2
        state.stress += 5
        print("\n💡 获得知识：加密市场有周期，牛熊交替是常态")

    state.day += 1
    state.save()


def chapter4_opportunity(state):
    """第四章：机遇与陷阱"""
    clear_screen()
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║           第四章：机遇与陷阱                         ║
  ║           "这个机会看起来太好了"                      ║
  ╚══════════════════════════════════════════════════════╝
    """)
    show_status(state)

    slow_print("\n暴跌之后的一个月，市场慢慢回暖了。")
    slow_print("你的邮箱里收到了好几封'投资机会'的邮件。")
    slow_print("朋友圈也有人开始晒收益了。\n")

    # 根据之前的剧情分支
    if state.flags.get("上钩"):
        slow_print('"老师"在群里说：')
        slow_print('「兄弟们，更大的机会来了！这次是真的百倍币！」')
        slow_print("你有些犹豫，上次赚了钱，但总觉得不对劲...")

    total = state.total_value()
    slow_print(f"\n你目前的资产总值约为: ¥{total:.2f}")

    print("\n你面前有几个选择：\n")

    print("  [1] 参加一个DeFi挖矿项目，年化200%（高收益）")
    print("  [2] 加入一个NFT社群，铸造/交易NFT（新玩法）")
    print("  [3] 学习链上分析，跟踪大户钱包（提升认知）")
    if state.flags.get("上钩"):
        print("  [4] 继续跟'老师'操作，加大投入（高风险）")
    else:
        print("  [4] 用自己的知识做一级市场投资（研究型）")
    print("  [5] 提取所有资金，暂时退出市场（保平安）")

    choice = get_choice(5)
    state.history.append(f"4-{choice}")

    if choice == 1:
        slow_print("\n你找到了一个DeFi项目，存币进去就能赚利息。")
        slow_print("年化200%，存1000每天能赚5块多。")
        if state.knowledge >= 5:
            slow_print("但你之前学过知识，知道这种高收益有风险。")
            slow_print("你只投了一小部分试水。")
            state.balance -= 200
            state.add_item("DeFi挖矿经验")
            state.balance += 250  # 小赚
            print("\n💡 获得知识：DeFi = 去中心化金融，高收益=高风险")
        else:
            slow_print("你把大部分钱都投进去了。")
            if random.random() < 0.5:
                slow_print("项目跑路了！这就是传说中的'Rug Pull'！")
                state.balance *= 0.3
                state.add_item("Rug Pull受害者证书")
                print("\n💡 获得知识：Rug Pull = 项目方卷款跑路")
            else:
                slow_print("运气不错，项目还行，你赚了一些。")
                state.balance += 300
                state.add_item("DeFi挖矿收益")

    elif choice == 2:
        slow_print("\n你进入了一个NFT社群。")
        slow_print("有人花2000买的NFT现在涨到了20000！")
        slow_print("你也想试试，但NFT到底是什么？")
        slow_print("\n你花0.1 ETH铸造了一个像素猴子NFT。")
        cost = 250
        state.balance -= cost
        state.add_item("像素猴子 NFT")
        if random.random() < 0.3:
            slow_print("你的NFT被一个大佬看中了！出了3倍价格！")
            state.balance += cost * 3
            state.reputation += 10
        else:
            slow_print("NFT市场遇冷，你的猴子现在只值50块。")
            state.balance += 50
        print("\n💡 获得知识：NFT = 非同质化代币，独一无二的数字资产")

    elif choice == 3:
        slow_print("\n你开始学习链上数据分析。")
        slow_print("你知道了：")
        slow_print("- 可以通过Etherscan查看任何钱包的交易记录")
        slow_print("- 大户的买卖行为往往预示着市场走向")
        slow_print("- 链上数据不会骗人，但K线图会")
        state.knowledge += 5
        state.add_item("链上分析工具")
        state.add_item("Etherscan书签")
        print("\n💡 获得知识：DYOR = Do Your Own Research，自己研究最重要")

    elif choice == 4:
        if state.flags.get("上钩"):
            slow_print('\n「老师」让你把所有钱打进一个「内部账户」。')
            slow_print('「保证一周翻倍，不翻倍全额退款。」')
            slow_print("\n你犹豫了很久...")
            if state.knowledge >= 3:
                slow_print("你的知识告诉你这是骗局！")
                slow_print("你决定退出这个群。")
                state.remove_item("微信币圈群")
                state.flags["上钩"] = False
                state.knowledge += 3
                print("\n💡 识破骗局！你的知识救了你一命")
            else:
                slow_print("你把钱转过去了。")
                slow_print("第二天，群解散了。'老师'消失了。")
                slow_print("你的钱，也没了。")
                state.balance = 0
                state.holdings = {}
                state.ending = "被割韭菜"
                print("\n💡 教训：永远不要把钱转给陌生人")
        else:
            slow_print("\n你开始研究一级市场（ICO/IDO）。")
            slow_print("找到一个靠谱的项目，投了一点。")
            state.balance -= 300
            if random.random() < 0.4:
                slow_print("项目上线后涨了5倍！你小赚一笔！")
                state.balance += 1500
                state.reputation += 15
            else:
                slow_print("项目上线就破发，你亏了。")
                state.balance += 100
            print("\n💡 获得知识：ICO/IDO = 首次代币发行，风险极高")

    elif choice == 5:
        slow_print("\n你决定先把钱取出来，冷静一段时间。")
        total = state.total_value()
        state.balance = total
        state.holdings = {}
        slow_print(f"你提取了 ¥{state.balance:.2f}，暂时告别币圈。")
        state.stress = max(0, state.stress - 20)
        state.flags["退出"] = True
        print("\n💡 获得知识：知道什么时候退出，比知道什么时候进入更重要")

    state.day += 7
    random_event(state)
    state.save()


def chapter5_final(state):
    """第五章：最终命运"""
    clear_screen()
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║           第五章：最终命运                           ║
  ║           "一切都有代价"                             ║
  ╚══════════════════════════════════════════════════════╝
    """)
    show_status(state)

    total = state.total_value()
    slow_print(f"\n一年过去了。你的资产总值: ¥{total:.2f}")
    slow_print(f"你的知识等级: Lv.{state.knowledge}")
    slow_print(f"你的压力值: {state.stress}/100\n")

    # 已经有结局的直接跳转
    if state.ending:
        show_ending(state)
        return

    slow_print("毕业季到了，你需要做最后一个决定。")
    slow_print("你面前有几条路：\n")

    print("  [1] 全职做加密货币交易/投资（全职韭菜）")
    print("  [2] 找份区块链公司的工作（正规军）")
    print("  [3] 用你学到的知识创业做一个区块链项目")
    print("  [4] 彻底离开加密世界，找个普通工作")
    print("  [5] 继续兼职做，等更好的时机")

    choice = get_choice(5)
    state.history.append(f"5-{choice}")

    if choice == 1:
        if total >= 50000 and state.knowledge >= 5:
            slow_print("\n你用一年的经验和积累，开始全职交易。")
            slow_print("你不再是那个什么都不懂的大学生了。")
            state.ending = "暴富"
        elif total >= 10000:
            slow_print("\n全职交易压力很大，你的情绪随着K线起伏。")
            if state.stress > 60:
                slow_print("压力太大了，你开始失眠、焦虑...")
                state.ending = "破产"
            else:
                slow_print("你勉强维持着，不温不火。")
                state.ending = "钻石手"
        else:
            slow_print("你的本金太少了，全职交易不现实。")
            slow_print("你只能继续做，等待机会。")
            state.ending = "归零"

    elif choice == 2:
        if state.knowledge >= 4:
            slow_print("\n你的知识和经验帮你拿到了一家区块链公司的offer。")
            slow_print("起薪不高，但能学到更多东西。")
            if state.reputation >= 15:
                slow_print("公司很看重你的社区经验，给了你不错的职位。")
                state.ending = "大佬"
            else:
                slow_print("你从底层做起，但方向对了。")
                state.ending = "教授"
        else:
            slow_print("你的知识储备不够，面试被刷了。")
            slow_print("你决定先学习再找机会。")
            state.ending = "教授"

    elif choice == 3:
        if total >= 30000 and state.knowledge >= 6:
            slow_print("\n你有了一个想法：做一个简化DeFi操作的工具。")
            slow_print("你找了两个朋友一起干。")
            if random.random() < 0.4:
                slow_print("项目渐渐有了用户，投资机构找上门了。")
                state.ending = "大佬"
            else:
                slow_print("创业太难了，资金链断了，项目黄了。")
                state.ending = "破产"
        else:
            slow_print("你的资金和知识都不够支撑创业。")
            slow_print("你决定先积累再说。")
            state.ending = "教授"

    elif choice == 4:
        slow_print("\n你关闭了所有交易所账户。")
        slow_print("删掉了推特、Discord、Telegram。")
        slow_print("你发现，没有K线图的日子，睡眠好了很多。")
        if total > 2000:
            slow_print(f"你带着 ¥{total:.2f} 的积蓄，开始了新生活。")
        state.ending = "教授"

    elif choice == 5:
        slow_print("\n你决定先找份工作，加密货币作为副业。")
        slow_print("这种'两条腿走路'的策略很稳。")
        if state.knowledge >= 4:
            slow_print("随着你的知识越来越深，你在圈子里小有名气。")
            state.ending = "大佬"
        else:
            slow_print("你慢慢积累，不急不躁。")
            state.ending = "钻石手"

    state.day += 30
    state.save()
    show_ending(state)


def show_ending(state):
    """显示结局"""
    clear_screen()
    print(ENDING_ART)

    ending = state.ending or "破产"
    if ending in ENDINGS:
        print(ENDINGS[ending])

    total = state.total_value()
    print(f"\n  📊 最终统计:")
    print(f"  ├── 游戏天数: {state.day}天")
    print(f"  ├── 最终资产: ¥{total:.2f}")
    print(f"  ├── 知识等级: Lv.{state.knowledge}")
    print(f"  ├── 声望值: {state.reputation}")
    print(f"  ├── 收集物品: {len(state.items)}个")
    print(f"  └── 结局: {ending}")

    # 评分
    score = 0
    score += min(total / 100, 50)
    score += state.knowledge * 5
    score += state.reputation
    score += len(state.items) * 3

    print(f"\n  🏆 综合评分: {score:.0f}/100")

    if score >= 80:
        print("  评级: ⭐⭐⭐⭐⭐ 传奇玩家！")
    elif score >= 60:
        print("  评级: ⭐⭐⭐⭐ 老韭菜了")
    elif score >= 40:
        print("  评级: ⭐⭐⭐ 有潜力")
    elif score >= 20:
        print("  评级: ⭐⭐ 新手村出来的")
    else:
        print("  评级: ⭐ 菜鸟")

    # 彩蛋：根据知识等级给建议
    print(f"\n  📚 游戏中你学到了:")
    knowledge_tips = {
        1: "KYC认证是交易所的标配",
        2: "分散投资可以降低风险",
        3: "止损是生存技能",
        4: "HODL需要真正的信念",
        5: "链上数据不会骗人",
        6: "DeFi高收益=高风险",
        7: "DYOR自己研究最重要",
        8: "加密市场有周期规律",
        9: "知道何时退出比进入更重要",
        10: "认知才是最大的财富",
    }
    for level in range(1, min(state.knowledge + 1, 11)):
        if level in knowledge_tips:
            print(f"     Lv.{level}: {knowledge_tips[level]}")

    print("\n  感谢游玩《加密货币大冒险》！")
    print("  记住：游戏里亏钱不要紧，现实中要谨慎。")
    print("  币圈有风险，投资需谨慎。\n")

    # 询问是否重新开始
    print("  [1] 重新开始")
    print("  [2] 退出游戏")
    choice = get_choice(2)
    if choice == 1:
        main()
    else:
        print("\n再见！👋\n")
        sys.exit(0)


# ============================================================
# 主菜单
# ============================================================
def main_menu():
    """主菜单"""
    clear_screen()
    print(TITLE_ART)
    print("""
    ┌──────────────────────────────────────┐
    │                                      │
    │   [1] 🎮 开始新游戏                  │
    │   [2] 📂 读取存档                    │
    │   [3] 📖 游戏说明                    │
    │   [4] 🚪 退出游戏                    │
    │                                      │
    └──────────────────────────────────────┘
    """)

    while True:
        try:
            choice = int(input("👉 请选择: ").strip())
            if choice in [1, 2, 3, 4]:
                return choice
        except ValueError:
            pass
        print("请输入 1-4")


def show_help():
    """显示游戏说明"""
    clear_screen()
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║                   📖 游戏说明                       ║
  ╚══════════════════════════════════════════════════════╝

  🎯 游戏目标:
     从1000元本金开始，在加密货币世界里闯荡
     最终达成不同的结局

  🎮 操作指南:
     输入数字做选择
     s = 随时存档
     i = 查看背包
     h = 显示帮助
     q = 保存并退出

  📊 核心属性:
     💰 余额   - 你的现金
     📦 持仓   - 你持有的加密货币
     📊 知识   - 对加密货币的理解程度
     ⭐ 声望   - 在圈子里的名气
     ⚡ 压力   - 炒币带来的精神压力
     🎒 物品   - 你收集的各种东西

  🏆 结局一览:
     💰 暴富   - 财富自由，人生赢家
     💀 破产   - 亏得裤衩都不剩
     🥬 被割韭菜 - 被骗子骗光
     👑 大佬   - 成为币圈意见领袖
     💎 钻石手 - 耐心持有最终获胜
     ⚖️ 监管   - 被请去喝茶
     🎓 教授   - 转型区块链研究
     🔥 归零   - 合约爆仓

  ⚠️ 免责声明:
     这只是一个游戏！
     现实中的加密货币投资风险极高
     本游戏不构成任何投资建议
     币圈有风险，投资需谨慎！

  💡 小贴士:
     - 知识等级越高，越容易做出正确判断
     - 压力值过高会影响结局
     - 多收集物品，有些关键时刻会派上用场
     - 随机事件增加了游戏的不确定性
    """)

    input("\n按回车返回主菜单...")


# ============================================================
# 游戏主流程
# ============================================================
def game_loop(state):
    """游戏主循环"""
    chapters = [
        chapter1_intro,
        chapter2_first_trade,
        chapter3_market_crash,
        chapter4_opportunity,
        chapter5_final,
    ]

    # 从存档的章节继续
    start = state.chapter - 1

    for i, chapter in enumerate(chapters[start:], start=start):
        state.chapter = i + 1
        chapter(state)
        if state.ending:
            break

    # 如果没有触发结局，显示默认结局
    if not state.ending:
        total = state.total_value()
        if total >= 50000:
            state.ending = "暴富"
        elif total >= 20000:
            state.ending = "钻石手"
        elif total >= 5000:
            state.ending = "大佬"
        elif total >= 1000:
            state.ending = "教授"
        elif total > 0:
            state.ending = "破产"
        else:
            state.ending = "归零"
        state.save()
        show_ending(state)


def main():
    """主函数"""
    global state

    while True:
        choice = main_menu()

        if choice == 1:
            # 新游戏
            state = GameState()
            clear_screen()
            print("\n  🎮 新游戏开始！\n")
            name = input("  给自己取个名字（直接回车用默认）: ").strip()
            if name:
                state.name = name
            slow_print(f"\n  欢迎，{state.name}！你的冒险即将开始...\n")
            time.sleep(1)
            game_loop(state)

        elif choice == 2:
            # 读取存档
            loaded = GameState.load()
            if loaded:
                state = loaded
                print(f"\n  ✅ 存档已加载！欢迎回来，{state.name}！")
                time.sleep(1)
                game_loop(state)
            else:
                print("\n  ❌ 没有找到存档文件！")
                time.sleep(1)

        elif choice == 3:
            show_help()

        elif choice == 4:
            print("\n  再见！👋\n")
            sys.exit(0)


# ============================================================
# 全局状态（用于函数间共享）
# ============================================================
state = GameState()

if __name__ == "__main__":
    main()

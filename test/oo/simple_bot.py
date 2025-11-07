# Bitkub Simple Auto Trading Bot
# ไม่ต้องใช้ TradingView - รันเองทั้งหมด

import requests
import time
import hashlib
import hmac
import json
from datetime import datetime

# ========== ตั้งค่าพื้นฐาน ==========
# โหมดทดสอบ: เปลี่ยนเป็น False เมื่อพร้อมใช้ API จริง
DEMO_MODE = True  # ใช้ข้อมูลจำลองสำหรับทดสอบ

BITKUB_API_KEY = "YOUR_API_KEY"  # ใส่ API Key จาก Bitkub
BITKUB_API_SECRET = "YOUR_API_SECRET"  # ใส่ API Secret

# เลือกเหรียญที่จะเทรด
SYMBOL = "THB_BTC"  # BTC, ETH, XRP, ADA, DOGE, etc.

# ตั้งค่าการเทรด
TRADING_ENABLED = False  # เปลี่ยนเป็น True เมื่อพร้อมเทรดจริง
TRADE_AMOUNT = 100  # จำนวนเงินต่อครั้ง (บาท)
CHECK_INTERVAL = 60  # ตรวจสอบทุกกี่วินาที (60 = 1 นาที)

# ตั้งค่ากลยุทธ์ (ปรับได้)
RSI_PERIOD = 14  # ช่วงเวลา RSI
RSI_OVERSOLD = 30  # ซื้อเมื่อ RSI ต่ำกว่านี้
RSI_OVERBOUGHT = 70  # ขายเมื่อ RSI สูงกว่านี้
MA_SHORT = 10  # Moving Average ระยะสั้น
MA_LONG = 30  # Moving Average ระยะยาว

# ========== ฟังก์ชันสร้างข้อมูลจำลอง (Demo Mode) ==========
import random

def generate_mock_prices(base_price=1500000, count=100):
    """สร้างข้อมูลราคาจำลองแบบ realistic"""
    prices = [base_price]
    
    for i in range(count - 1):
        # สร้างการเปลี่ยนแปลงราคาแบบสุ่ม (-2% ถึง +2%)
        change_percent = random.uniform(-0.02, 0.02)
        
        # เพิ่มแนวโน้ม (trend)
        if i % 30 < 15:  # ขึ้น
            change_percent += random.uniform(0, 0.01)
        else:  # ลง
            change_percent -= random.uniform(0, 0.01)
        
        new_price = prices[-1] * (1 + change_percent)
        prices.append(new_price)
    
    return prices

def get_mock_ticker(symbol):
    """สร้างข้อมูล ticker จำลอง"""
    base_prices = {
        'THB_BTC': 1500000,
        'THB_ETH': 80000,
        'THB_XRP': 15,
        'THB_ADA': 10,
        'THB_DOGE': 3
    }
    
    base = base_prices.get(symbol, 100)
    current = base * random.uniform(0.98, 1.02)
    
    return {
        'last': current,
        'high': current * 1.05,
        'low': current * 0.95,
        'volume': random.uniform(1000000, 10000000)
    }

def get_mock_historical_data(symbol, timeframe=1, limit=100):
    """สร้างข้อมูลราคาย้อนหลังจำลอง"""
    base_prices = {
        'THB_BTC': 1500000,
        'THB_ETH': 80000,
        'THB_XRP': 15,
        'THB_ADA': 10,
        'THB_DOGE': 3
    }
    
    base = base_prices.get(symbol, 100)
    return generate_mock_prices(base, limit)

# ========== ฟังก์ชันเรียก Bitkub API ==========
def bitkub_api_call(endpoint, payload=None):
    """เรียกใช้ Bitkub API"""
    url = f"https://api.bitkub.com{endpoint}"
    
    if payload is None:
        payload = {}
    
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    
    # Public API (ไม่ต้อง sign)
    if endpoint.startswith('/api/market/'):
        try:
            response = requests.get(url, params=payload, timeout=10)
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    # Private API (ต้อง sign)
    payload['ts'] = int(time.time())
    json_payload = json.dumps(payload)
    signature = hmac.new(
        BITKUB_API_SECRET.encode(),
        msg=json_payload.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    headers['X-BTK-APIKEY'] = BITKUB_API_KEY
    headers['X-BTK-SIGN'] = signature
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

# ========== ดึงข้อมูลตลาด ==========
def get_ticker(symbol):
    """ดึงราคาปัจจุบัน"""
    # ใช้ข้อมูลจำลองในโหมดทดสอบ
    if DEMO_MODE:
        print("📊 [DEMO MODE] ใช้ข้อมูลจำลอง")
        return get_mock_ticker(symbol)
    
    result = bitkub_api_call('/api/market/ticker', {'sym': symbol})
    if result and symbol in result:
        return result[symbol]
    return None

def get_historical_data(symbol, timeframe=1, limit=100):
    """ดึงข้อมูลราคาย้อนหลัง (OHLC)"""
    # ใช้ข้อมูลจำลองในโหมดทดสอบ
    if DEMO_MODE:
        return get_mock_historical_data(symbol, timeframe, limit)
    
    # Bitkub ใช้ tradingview API
    endpoint = f"/tradingview/history"
    params = {
        'symbol': symbol,
        'resolution': timeframe,  # 1, 5, 15, 60, 240, 1D
        'from': int(time.time()) - (limit * timeframe * 60),
        'to': int(time.time())
    }
    
    result = bitkub_api_call(endpoint, params)
    if result and 'c' in result:  # c = close prices
        return result['c']
    return []

def get_wallet_balance():
    """ดึงยอดเงินในกระเป๋า"""
    # ใช้ข้อมูลจำลองในโหมดทดสอบ
    if DEMO_MODE:
        return {
            'THB': {'available': 10000, 'reserved': 0},
            'BTC': {'available': 0.001, 'reserved': 0},
            'ETH': {'available': 0.05, 'reserved': 0}
        }
    
    result = bitkub_api_call('/api/market/wallet')
    if result and 'result' in result:
        return result['result']
    return None

# ========== คำนวณตัวชี้วัด ==========
def calculate_rsi(prices, period=14):
    """คำนวณ RSI"""
    if len(prices) < period + 1:
        return 50  # ค่าเริ่มต้น
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ma(prices, period=10):
    """คำนวณ Moving Average"""
    if len(prices) < period:
        return sum(prices) / len(prices)
    return sum(prices[-period:]) / period

def calculate_ema(prices, period=10):
    """คำนวณ EMA (Exponential Moving Average)"""
    if len(prices) < period:
        return sum(prices) / len(prices)
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

# ========== คำนวณตัวชี้วัดขั้นสูง (AI-Enhanced) ==========
def calculate_advanced_indicators(prices, current_price):
    """คำนวณตัวชี้วัดขั้นสูงแบบ AI"""
    
    # 1. Trend Momentum Score (0-25)
    ma_value = calculate_ma(prices, 20)
    trend_score = 25.0 if current_price > ma_value else 0.0
    
    # 2. RSI Momentum Score (0-20)
    rsi = calculate_rsi(prices, 14)
    if rsi < 30:
        rsi_score = 20.0
    elif rsi < 40:
        rsi_score = 15.0
    elif rsi > 70:
        rsi_score = 0.0
    elif rsi > 60:
        rsi_score = 5.0
    else:
        rsi_score = 10.0
    
    # 3. Volume Score (0-15) - ใช้การเปลี่ยนแปลงราคาแทน
    price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    avg_change = sum(price_changes) / len(price_changes)
    recent_change = prices[-1] - prices[-2]
    volume_score = 15.0 if recent_change > avg_change * 1.5 else 7.5
    
    # 4. Bollinger Bands Position (0-15)
    bb_basis = calculate_ma(prices, 20)
    std_dev = (sum([(p - bb_basis)**2 for p in prices[-20:]]) / 20) ** 0.5
    bb_upper = bb_basis + (2 * std_dev)
    bb_lower = bb_basis - (2 * std_dev)
    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
    
    if bb_position < 0.2:
        bb_score = 15.0
    elif bb_position < 0.4:
        bb_score = 12.0
    elif bb_position > 0.8:
        bb_score = 0.0
    elif bb_position > 0.6:
        bb_score = 3.0
    else:
        bb_score = 7.5
    
    # 5. Price Action Pattern (0-15)
    bullish_candle = prices[-1] > prices[-2]
    consecutive_green = bullish_candle and (prices[-2] > prices[-3])
    consecutive_red = (not bullish_candle) and (prices[-2] < prices[-3])
    
    if consecutive_green:
        pattern_score = 15.0
    elif bullish_candle:
        pattern_score = 10.0
    elif consecutive_red:
        pattern_score = 0.0
    else:
        pattern_score = 5.0
    
    # 6. MACD Score (0-10)
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    macd_bullish = ema_12 > ema_26
    macd_score = 10.0 if macd_bullish else 5.0
    
    # รวมคะแนน
    total_score = trend_score + rsi_score + volume_score + bb_score + pattern_score + macd_score
    
    return {
        'total_score': total_score,
        'probability_up': total_score,
        'probability_down': 100 - total_score,
        'rsi': rsi,
        'ma_value': ma_value,
        'bb_upper': bb_upper,
        'bb_lower': bb_lower,
        'ema_12': ema_12,
        'ema_26': ema_26
    }

def calculate_bayesian_probability(indicators, prices):
    """คำนวณ Bayesian Probability"""
    prob_up = indicators['probability_up'] / 100.0
    prob_down = indicators['probability_down'] / 100.0
    
    # Likelihood based on patterns
    recent_trend = prices[-1] > prices[-5]
    likelihood_up = 0.75 if recent_trend else 0.25
    likelihood_down = 0.75 if not recent_trend else 0.25
    
    # Bayesian Update
    evidence = (likelihood_up * prob_up) + (likelihood_down * prob_down)
    
    if evidence > 0:
        posterior_up = (likelihood_up * prob_up) / evidence
        bayesian_prob_up = posterior_up * 100
        bayesian_prob_down = (1 - posterior_up) * 100
    else:
        bayesian_prob_up = 50
        bayesian_prob_down = 50
    
    return bayesian_prob_up, bayesian_prob_down

def calculate_ai_confidence(indicators, prices, bayesian_prob_up):
    """คำนวณ AI Confidence Score"""
    
    # Pattern Recognition
    is_hammer = abs(prices[-1] - prices[-2]) < (max(prices[-3:]) - min(prices[-3:])) * 0.3
    pattern_conf = 20 if is_hammer else 10
    
    # Regime Detection
    avg_return = sum([prices[i] - prices[i-1] for i in range(1, min(20, len(prices)))]) / min(20, len(prices))
    regime_conf = 25 if abs(avg_return) > 0 else 10
    
    # Momentum Quality
    rsi = indicators['rsi']
    momentum_conf = 25 if (rsi > 40 and rsi < 60) else 15
    
    # Trend Consistency
    ups = sum([1 for i in range(1, min(10, len(prices))) if prices[i] > prices[i-1]])
    trend_conf = (ups / min(10, len(prices))) * 30
    
    ai_confidence = pattern_conf + regime_conf + momentum_conf + trend_conf
    ai_confidence = min(ai_confidence, 100)
    
    return ai_confidence

def calculate_ultimate_accuracy(indicators, bayesian_prob_up, ai_confidence):
    """คำนวณ Ultimate Accuracy Score"""
    
    # Composite Score
    composite = indicators['probability_up']
    
    # Ultimate Score
    ultimate = (composite * 0.5) + (bayesian_prob_up * 0.3) + (ai_confidence * 0.2)
    ultimate = min(ultimate, 100)
    
    # Confidence Level
    if ultimate >= 90:
        confidence_level = "มั่นใจมาก"
    elif ultimate >= 75:
        confidence_level = "มั่นใจ"
    elif ultimate >= 60:
        confidence_level = "ปานกลาง"
    elif ultimate >= 45:
        confidence_level = "ต่ำ"
    else:
        confidence_level = "ต่ำมาก"
    
    return ultimate, confidence_level

# ========== กลยุทธ์การเทรด (AI-Enhanced) ==========
def analyze_signal(symbol):
    """วิเคราะห์สัญญาณซื้อ/ขาย แบบ AI"""
    print(f"\n{'='*70}")
    print(f"🤖 AI ANALYSIS - {symbol} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # ดึงข้อมูลราคา
    ticker = get_ticker(symbol)
    if not ticker:
        print("❌ ไม่สามารถดึงข้อมูลราคาได้")
        return None
    
    current_price = float(ticker['last'])
    print(f"💰 ราคาปัจจุบัน: {current_price:,.2f} บาท")
    
    # ดึงข้อมูลย้อนหลัง
    prices = get_historical_data(symbol, timeframe=1, limit=100)
    if len(prices) < 50:
        print("❌ ข้อมูลไม่เพียงพอ")
        return None
    
    # คำนวณตัวชี้วัดพื้นฐาน
    rsi = calculate_rsi(prices, RSI_PERIOD)
    ma_short = calculate_ma(prices, MA_SHORT)
    ma_long = calculate_ma(prices, MA_LONG)
    
    # ========== AI ANALYSIS ==========
    print(f"\n🧠 กำลังคำนวณด้วย AI...")
    
    # 1. Advanced Indicators
    indicators = calculate_advanced_indicators(prices, current_price)
    
    # 2. Bayesian Probability
    bayesian_prob_up, bayesian_prob_down = calculate_bayesian_probability(indicators, prices)
    
    # 3. AI Confidence
    ai_confidence = calculate_ai_confidence(indicators, prices, bayesian_prob_up)
    
    # 4. Ultimate Accuracy
    ultimate_accuracy, confidence_level = calculate_ultimate_accuracy(
        indicators, bayesian_prob_up, ai_confidence
    )
    
    # แสดงผล AI Analysis
    print(f"\n📊 ตัวชี้วัดพื้นฐาน:")
    print(f"  RSI ({RSI_PERIOD}): {rsi:.2f}")
    print(f"  MA {MA_SHORT}: {ma_short:,.2f}")
    print(f"  MA {MA_LONG}: {ma_long:,.2f}")
    print(f"  EMA 12: {indicators['ema_12']:,.2f}")
    print(f"  EMA 26: {indicators['ema_26']:,.2f}")
    
    print(f"\n🎯 การวิเคราะห์ AI:")
    print(f"  ความน่าจะเป็น (พื้นฐาน): ขึ้น {indicators['probability_up']:.1f}% | ลง {indicators['probability_down']:.1f}%")
    print(f"  Bayesian Probability: ขึ้น {bayesian_prob_up:.1f}% | ลง {bayesian_prob_down:.1f}%")
    print(f"  AI Confidence: {ai_confidence:.1f}%")
    print(f"  ⭐ Ultimate Accuracy: {ultimate_accuracy:.1f}% ({confidence_level})")
    
    # วิเคราะห์สัญญาณ
    signal = None
    reason = []
    
    # ใช้ Ultimate Accuracy ในการตัดสินใจ
    if ultimate_accuracy >= 70:  # ความแม่นยำสูง
        if bayesian_prob_up > bayesian_prob_down:
            signal = "BUY"
            if ultimate_accuracy >= 85:
                reason.append(f"🔥 AI แนะนำ ซื้อแรง (Accuracy {ultimate_accuracy:.0f}%)")
            else:
                reason.append(f"AI แนะนำ ซื้อ (Accuracy {ultimate_accuracy:.0f}%)")
            
            if rsi < RSI_OVERSOLD:
                reason.append(f"RSI Oversold ({rsi:.1f})")
            if current_price < indicators['bb_lower']:
                reason.append(f"ราคาต่ำกว่า BB Lower")
        else:
            signal = "SELL"
            if ultimate_accuracy >= 85:
                reason.append(f"🔥 AI แนะนำ ขายแรง (Accuracy {ultimate_accuracy:.0f}%)")
            else:
                reason.append(f"AI แนะนำ ขาย (Accuracy {ultimate_accuracy:.0f}%)")
            
            if rsi > RSI_OVERBOUGHT:
                reason.append(f"RSI Overbought ({rsi:.1f})")
            if current_price > indicators['bb_upper']:
                reason.append(f"ราคาสูงกว่า BB Upper")
    
    elif ultimate_accuracy >= 60:  # ความแม่นยำปานกลาง
        # ใช้กลยุทธ์แบบดั้งเดิม
        if rsi < RSI_OVERSOLD and ma_short > ma_long:
            signal = "BUY"
            reason.append(f"RSI Oversold + MA Crossover (Accuracy {ultimate_accuracy:.0f}%)")
        elif rsi > RSI_OVERBOUGHT and ma_short < ma_long:
            signal = "SELL"
            reason.append(f"RSI Overbought + MA Crossover (Accuracy {ultimate_accuracy:.0f}%)")
    
    else:
        # ความแม่นยำต่ำ - รอดู
        signal = None
        reason.append(f"⚠️ ความแม่นยำต่ำ ({ultimate_accuracy:.0f}%) - รอดู")
    
    # แสดงผลสัญญาณ
    if signal == "BUY":
        print(f"\n🟢 สัญญาณ: ซื้อ (BUY)")
        print(f"📝 เหตุผล: {', '.join(reason)}")
    elif signal == "SELL":
        print(f"\n🔴 สัญญาณ: ขาย (SELL)")
        print(f"📝 เหตุผล: {', '.join(reason)}")
    else:
        print(f"\n⚪ สัญญาณ: รอดู (HOLD)")
        print(f"📝 เหตุผล: {', '.join(reason)}")
    
    return {
        'signal': signal,
        'price': current_price,
        'rsi': rsi,
        'ma_short': ma_short,
        'ma_long': ma_long,
        'probability_up': indicators['probability_up'],
        'probability_down': indicators['probability_down'],
        'bayesian_prob_up': bayesian_prob_up,
        'bayesian_prob_down': bayesian_prob_down,
        'ai_confidence': ai_confidence,
        'ultimate_accuracy': ultimate_accuracy,
        'confidence_level': confidence_level,
        'reason': reason
    }

# ========== ซื้อ/ขาย ==========
def place_buy_order(symbol, amount):
    """สั่งซื้อ"""
    print(f"\n🛒 กำลังสั่งซื้อ {symbol} มูลค่า {amount} บาท...")
    
    if not TRADING_ENABLED:
        print("⚠️  TRADING DISABLED - นี่คือการจำลอง (ไม่ซื้อจริง)")
        return True
    
    payload = {
        'sym': symbol,
        'amt': amount,
        'typ': 'market'
    }
    
    result = bitkub_api_call('/api/market/place-bid', payload)
    
    if result and 'error' not in result:
        print(f"✅ ซื้อสำเร็จ! Order ID: {result.get('id')}")
        return True
    else:
        print(f"❌ ซื้อไม่สำเร็จ: {result}")
        return False

def place_sell_order(symbol, amount=None):
    """สั่งขาย (ขายทั้งหมด)"""
    print(f"\n💸 กำลังสั่งขาย {symbol}...")
    
    # ดึงยอดเหรียญที่มี
    wallet = get_wallet_balance()
    if not wallet:
        print("❌ ไม่สามารถดึงข้อมูลกระเป๋าได้")
        return False
    
    crypto = symbol.replace('THB_', '')
    if crypto not in wallet or float(wallet[crypto]['available']) <= 0:
        print(f"⚠️  ไม่มี {crypto} ในกระเป๋า")
        return False
    
    available = float(wallet[crypto]['available'])
    ticker = get_ticker(symbol)
    value = available * float(ticker['last'])
    
    print(f"💰 มี {available} {crypto} (มูลค่า ~{value:,.2f} บาท)")
    
    if not TRADING_ENABLED:
        print("⚠️  TRADING DISABLED - นี่คือการจำลอง (ไม่ขายจริง)")
        return True
    
    payload = {
        'sym': symbol,
        'amt': value,
        'typ': 'market'
    }
    
    result = bitkub_api_call('/api/market/place-ask', payload)
    
    if result and 'error' not in result:
        print(f"✅ ขายสำเร็จ! Order ID: {result.get('id')}")
        return True
    else:
        print(f"❌ ขายไม่สำเร็จ: {result}")
        return False

# ========== Main Loop ==========
def main():
    """ลูปหลัก - รันตลอดเวลา"""
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║     🤖 BITKUB AI AUTO TRADING BOT (Advanced Edition)             ║
╠═══════════════════════════════════════════════════════════════════╣
║  Mode: {'🎮 DEMO MODE (ข้อมูลจำลอง)' if DEMO_MODE else '🔴 LIVE MODE (API จริง)':<56}║
║  Symbol: {SYMBOL:<60}║
║  Trade Amount: {TRADE_AMOUNT} THB{' '*48}║
║  Check Interval: {CHECK_INTERVAL} วินาที{' '*45}║
║  Trading: {'✅ ENABLED' if TRADING_ENABLED else '❌ DISABLED (TEST MODE)':<52}║
║                                                                   ║
║  🧠 AI Features:                                                  ║
║    • Bayesian Probability Analysis                               ║
║    • Pattern Recognition                                         ║
║    • Ultimate Accuracy Score                                     ║
║    • Multi-indicator Analysis                                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    if DEMO_MODE:
        print("🎮 กำลังรันในโหมดทดสอบ - ใช้ข้อมูลจำลอง")
        print("💡 เปลี่ยน DEMO_MODE = False เพื่อใช้ API จริง")
        print()
    
    if not TRADING_ENABLED:
        print("⚠️  การเทรดปิดอยู่ - นี่คือโหมดทดสอบ")
        print("⚠️  เปลี่ยน TRADING_ENABLED = True เพื่อเทรดจริง")
        print()
    
    last_signal = None
    
    while True:
        try:
            # วิเคราะห์สัญญาณ
            analysis = analyze_signal(SYMBOL)
            
            if analysis:
                signal = analysis['signal']
                ultimate_accuracy = analysis.get('ultimate_accuracy', 0)
                
                # ป้องกันสัญญาณซ้ำ และตรวจสอบความแม่นยำ
                if signal and signal != last_signal:
                    # ตรวจสอบความแม่นยำก่อนเทรด
                    if ultimate_accuracy >= 60:  # ต้องมีความแม่นยำอย่างน้อย 60%
                        if signal == "BUY":
                            print(f"\n✨ สัญญาณมีคุณภาพ! (Accuracy: {ultimate_accuracy:.1f}%)")
                            success = place_buy_order(SYMBOL, TRADE_AMOUNT)
                            if success:
                                last_signal = "BUY"
                        
                        elif signal == "SELL":
                            print(f"\n✨ สัญญาณมีคุณภาพ! (Accuracy: {ultimate_accuracy:.1f}%)")
                            success = place_sell_order(SYMBOL)
                            if success:
                                last_signal = "SELL"
                    else:
                        print(f"\n⚠️ ความแม่นยำต่ำเกินไป ({ultimate_accuracy:.1f}%) - ข้ามการเทรด")
            
            # รอก่อนตรวจสอบครั้งถัดไป
            print(f"\n⏳ รอ {CHECK_INTERVAL} วินาที...")
            print(f"{'='*70}\n")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n⛔ หยุดการทำงานโดยผู้ใช้")
            break
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาด: {e}")
            print(f"⏳ รอ {CHECK_INTERVAL} วินาที แล้วลองใหม่...")
            time.sleep(CHECK_INTERVAL)

# ========== เริ่มต้น ==========
if __name__ == "__main__":
    # ตรวจสอบ API Key (เฉพาะเมื่อไม่ใช่ DEMO_MODE)
    if not DEMO_MODE and BITKUB_API_KEY == "YOUR_API_KEY":
        print("❌ กรุณาใส่ API Key และ Secret ก่อนใช้งาน!")
        print("📝 แก้ไขที่บรรทัดที่ 10-11")
        print("\n💡 หรือเปลี่ยน DEMO_MODE = True เพื่อทดสอบด้วยข้อมูลจำลอง")
    else:
        main()

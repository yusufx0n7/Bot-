import ccxt
import requests
import time
import threading

# === BU YERGA TOKEN VA ID NI KIRITING ===
TELEGRAM_TOKEN="7605062670:AAHLKWg-Zkow-j1y5mdWGli6MJafN3XRCxE"
CHAT_ID = "7971306481"

# === BOT SOZLAMALARI ===
MIN_PROFIT_PERCENT = 3.0
MIN_LIQUIDITY = 5000
CHESK_MODE_TIME = 300  # sekund (5 daqiqa)
PAIR_LIST = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "TON/USDT", "LINK/USDT", "DOT/USDT"]

# === CCXT Mavjud birjalar (API ochiq) ===
CCXT_SUPPORTED_EXCHANGES = [
    "binance", "mexc", "coinex", "kraken", "huobi", "bitget",
    "poloniex", "bitmart", "bingx", "lbank", "digifinex"
]

# === Yopiq API birjalar (CoinGecko orqali ishlaydi) ===
COINGECKO_ONLY_EXCHANGES = [
    "superex", "toobit", "ascendex", "blofin", "bdfi", "bitrue", "bydfi",
    "coinw", "ourbit", "btcc", "weex", "gmgn", "kcex", "coincola"
]

EXCHANGES = CCXT_SUPPORTED_EXCHANGES + COINGECKO_ONLY_EXCHANGES

# === CoinGecko ID mapping ===
COINGECKO_IDS = {
    "AA/USDT": "a3s-protocol",
    "ABEL/USDT": "abelian",
    "ACE/USDT": "acent",
    "ACH/USDT": "alchemy-pay",
    "ACRIA/USDT": "acria-ai",
    "ACT/USDT": "act-i-the-ai-prophecy",
    "ADA/USDT": "cardano",
    "ADX/USDT": "adex",
    "AGLD/USDT": "adventure-gold",
    "AE/USDT": "aeternity",
    "AERGO/USDT": "aergo",
    "AGRS/USDT": "agoras-currency-of-tau",
    "AGIXT/USDT": "agixt",
    "AIA/USDT": "aia-chain",
    "AIFUN/USDT": "ai-agent-layer",
    "AIN/USDT": "ai-network",
    "AI/USDT": "ai-pin", # "Multiverse" ham "AI" bo'lishi mumkin, aniqlash kerak
    "ARC/USDT": "ai-rig-complex",
    "AIMX/USDT": "aimedis-new",
    "AIXBT/USDT": "aixbt-by-virtuals",
    "AKI/USDT": "aki-network",
    "AGT/USDT": "alaya-governance-token",
    "ALCH/USDT": "alchemist-ai",
    "ALEO/USDT": "aleo",
    "ALEPH/USDT": "aleph-im",
    "ALPH/USDT": "alephium",
    "ALGO/USDT": "algorand",
    "ALLIN/USDT": "all-in",
    "ABR/USDT": "allbridge",
    "ATS/USDT": "alltoscan",
    "ALPINE/USDT": "alpine-f1-team",
    "ALT/USDT": "altlayer",
    "ALU/USDT": "altura",
    "AMB/USDT": "airdao",
    "AME/USDT": "ame-chain",
    "AMP/USDT": "amp",
    "ANLOG/USDT": "analog",
    "AEUR/USDT": "anchored-coins-aeur",
    "ANDR/USDT": "andromeda",
    "ANKR/USDT": "ankr",
    "ANYONE/USDT": "anyone-protocol",
    "AO/USDT": "ao",
    "APE/USDT": "apecoin",
    "API3/USDT": "api3",
    "APT/USDT": "aptos",
    "AQA/USDT": "aqa",
    "ARB/USDT": "arbitrum",
    "AIUS/USDT": "arbius",
    "ARDR/USDT": "arbor", # "Ardor" ham ARDR
}
chesk_mode = False

# === Telegram xabar yuborish ===
def send_message(text):
    """
    Telegram bot orqali xabar yuborish funksiyasi.
    Xabar yuborishda xato yuzaga kelsa, uni e'tiborsiz qoldiradi.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except requests.exceptions.RequestException as e:
        print(f"Telegramga xabar yuborishda xato: {e}") # Xatolarni konsolga chiqarish tavsiya etiladi
        pass

# === CCXT orqali birja ulash ===
def get_exchange(name):
    """
    CCXT kutubxonasi orqali birja obyektini yaratish.
    Agar birja topilmasa yoki ulanishda xato bo'lsa, None qaytaradi.
    """
    try:
        # ccxt.binance(), ccxt.mexc() kabi obyektlarni qaytaradi
        return getattr(ccxt, name)()
    except AttributeError:
        print(f"CCXT: '{name}' birjasi topilmadi yoki xato.")
        return None
    except Exception as e:
        print(f"CCXT: '{name}' birjasini ishga tushirishda kutilmagan xato: {e}")
        return None

# === CCXT narx olish ===
def fetch_price_ccxt(exchange, pair):
    """
    CCXT orqali berilgan birjadan valyuta juftligining narxini olish.
    Agar narx olishda xato yuzaga kelsa, None qaytaradi.
    """
    try:
        ticker = exchange.fetch_ticker(pair)
        return {
            "bid": ticker['bid'],
            "ask": ticker['ask'],
            "volume": ticker.get('baseVolume', 0) # 'baseVolume' mavjud bo'lmasa 0 qaytaradi
        }
    except ccxt.NetworkError as e:
        print(f"CCXT {exchange.id} {pair}: Tarmoq xatosi - {e}")
        return None
    except ccxt.ExchangeError as e:
        print(f"CCXT {exchange.id} {pair}: Birja xatosi - {e}")
        return None
    except Exception as e:
        print(f"CCXT {exchange.id} {pair}: Narxni olishda kutilmagan xato: {e}")
        return None

# === CoinGecko narx olish ===
def fetch_price_coingecko(coin_id):
    """
    CoinGecko API orqali koinning narxini olish.
    Agar API chaqiruvida xato yuzaga kelsa, None qaytaradi.
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        r = requests.get(url, timeout=10) # Timeout qo'shish tavsiya etiladi
        r.raise_for_status() # HTTP xatolarini tekshirish (4xx yoki 5xx)
        data = r.json()
        if coin_id in data and 'usd' in data[coin_id]:
            # CoinGecko volume ma'lumotini to'g'ridan-to'g'ri bermaydi, shuning uchun katta son berildi
            # Real loyihalar uchun volume uchun boshqa API ishlatish kerak
            return {
                "bid": data[coin_id]['usd'],
                "ask": data[coin_id]['usd'],
                "volume": 999999999 # Katta, mavjud bo'lmagan likvidlik qiymati
            }
        else:
            print(f"CoinGecko: '{coin_id}' uchun narx ma'lumoti topilmadi.")
            return None
    except requests.exceptions.Timeout:
        print(f"CoinGecko {coin_id}: So'rov vaqti tugadi.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"CoinGecko {coin_id}: So'rov xatosi - {e}")
        return None
    except Exception as e:
        print(f"CoinGecko {coin_id}: Narxni olishda kutilmagan xato: {e}")
        return None

# === Narxlarni olish ===
def fetch_price(exchange_name, symbol):
    """
    Berilgan birja nomidan va valyuta juftligidan narx ma'lumotlarini olish.
    CCXT yoki CoinGecko orqali harakat qiladi.
    """
    coin_id = COINGECKO_IDS.get(symbol)
    if exchange_name in CCXT_SUPPORTED_EXCHANGES:
        exch = get_exchange(exchange_name)
        if exch:
            return fetch_price_ccxt(exch, symbol)
    elif exchange_name in COINGECKO_ONLY_EXCHANGES:
        if coin_id: # coin_id mavjudligini tekshirish muhim
            return fetch_price_coingecko(coin_id)
        else:
            print(f"CoinGecko: '{symbol}' uchun CoinGecko ID topilmadi.")
    return None

# === Arbitraj tekshirish ===
def check_arbitrage(pair):
    """
    Berilgan valyuta juftligi bo'yicha turli birjalar orasida arbitraj imkoniyatini tekshiradi.
    Topilgan imkoniyatlarni Telegramga xabar qilib yuboradi.
    """
    prices = []
    for name in EXCHANGES:
        price_info = fetch_price(name, pair)
        if price_info and price_info['bid'] is not None and price_info['ask'] is not None:
            # Ba'zi birjalar 'bid' yoki 'ask' ni None qaytarishi mumkin, tekshirish muhim
            prices.append((name, price_info))

    if len(prices) < 2:
        # print(f"{pair}: Arbitraj tekshirish uchun yetarli narx ma'lumoti topilmadi ({len(prices)} ta birja).")
        return

    # Eng past sotib olish narxi (ask) va eng yuqori sotish narxi (bid) ni topish
    min_buy = min(prices, key=lambda x: x[1]['ask'])
    max_sell = max(prices, key=lambda x: x[1]['bid'])

    if min_buy[0] == max_sell[0]:
        # print(f"{pair}: Sotib olish va sotish bir xil birjada.")
        return

    spread = max_sell[1]['bid'] - min_buy[1]['ask']

    if min_buy[1]['ask'] == 0: # 0 ga bo'linishni oldini olish
        print(f"{pair}: Sotib olish narxi 0 bo'lgani uchun foyda hisoblash imkonsiz.")
        return

    profit_percent = (spread / min_buy[1]['ask']) * 100

    # Foyda va likvidlik shartlarini tekshirish
    if profit_percent >= MIN_PROFIT_PERCENT and min_buy[1]['volume'] >= MIN_LIQUIDITY:
        msg = (f"💰 Arbitraj Topildi!\n"
               f"Coin: {pair}\n"
               f"⬇️ Sotib olish: {min_buy[0]} @ {min_buy[1]['ask']:.6f}\n" # Formatlash
               f"⬆️ Sotish: {max_sell[0]} @ {max_sell[1]['bid']:.6f}\n" # Formatlash
               f"📈 Foyda: {profit_percent:.2f}%")
        send_message(msg)
        print(f"ARBITRAJ TOPILDI: {pair} - {profit_percent:.2f}%")
    elif chesk_mode and profit_percent >= 1.0: # chesk_mode holati faqat foyda 1% dan yuqori bo'lganda ishlaydi
        msg = (f"🧐 Chesk imkoniyat: {pair}\n"
               f"⬇️ {min_buy[0]}: {min_buy[1]['ask']:.6f}\n" # Formatlash
               f"⬆️ {max_sell[0]}: {max_sell[1]['bid']:.6f}\n" # Formatlash
               f"📉 Foyda: {profit_percent:.2f}%")
        send_message(msg)
        print(f"CHESK IMKONIYATI: {pair} - {profit_percent:.2f}%")


# === Bot komandalarini tinglash ===
def listen_bot():
    """
    Telegram botidan kelgan komandalarni tinglaydi va ularga javob beradi.
    '/start' va '/chesk' komandalarini qo'llab-quvvatlaydi.
    """
    global chesk_mode
    offset = None
    chesk_start_time = 0
    print("Telegram komandalarini tinglash boshlandi...")
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        if offset:
            url += f"?offset={offset}"
        try:
            r = requests.get(url, timeout=10).json() # Timeout qo'shish
            for result in r.get('result', []): # 'result' kaliti mavjudligini tekshirish
                offset = result['update_id'] + 1
                message = result.get('message', {})
                text = message.get('text', '')
                chat_id_from_msg = message.get('chat', {}).get('id')

                # Chat ID to'g'riligini tekshirish (faqat ruxsat berilgan CHAT_ID dan kelgan xabarlarga javob berish)
                if str(chat_id_from_msg) != CHAT_ID:
                    print(f"Begona CHAT_ID dan xabar keldi: {chat_id_from_msg}. E'tiborsiz qoldirildi.")
                    continue

                if text == "/start":
                    send_message("🟢 Assalomu alaykum! Maqsadingiz esingizdan chiqmasin. Tekshiruv boshlandi.")
                    print("/start komandasi qabul qilindi.")
                elif text == "/chesk":
                    send_message("🧪 5 daqiqalik chesk rejimi ishga tushdi...")
                    chesk_mode = True
                    chesk_start_time = time.time()
                    print("/chesk komandasi qabul qilindi. Chesk rejimi faol.")
                elif text: # Boshqa xabarlarga ham javob berish mumkin
                    print(f"Yangi xabar: {text}")

        except requests.exceptions.RequestException as e:
            print(f"Telegram getUpdates so'rovida xato: {e}")
        except Exception as e:
            print(f"Telegram komandalarini tinglashda kutilmagan xato: {e}")

        # Chesk rejimini vaqt bo'yicha o'chirish
        if chesk_mode and (time.time() - chesk_start_time > CHESK_MODE_TIME):
            chesk_mode = False
            send_message("✅ Chesk rejimi yakunlandi.")
            print("Chesk rejimi yakunlandi.")
        time.sleep(2)

# === Asosiy tekshiruv ishga tushurish ===
def run_bot():
    """
    Asosiy bot funksiyasi. Belgilangan valyuta juftliklari bo'yicha
    arbitraj imkoniyatlarini muntazam tekshirib boradi.
    """
    print("Asosiy arbitraj tekshiruvi boshlandi...")
    while True:
        for pair in PAIR_LIST:
            check_arbitrage(pair)
            time.sleep(1)  # har 1 sekunda 1 coin tekshiradi
        print(f"{len(PAIR_LIST)} ta coin tekshirildi. Navbatdagi tekshiruv 60 sekunddan so'ng.")
        time.sleep(60)  # 10 ta coin tugasa 60 sekunda dam

# === Boshlash ===
if __name__ == "__main__":
    # Telegram TOKEN va CHAT_ID ni tekshirish
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        print("XATO: Iltimos, TELEGRAM_TOKEN va CHAT_ID ni o'rnating. Kod ishga tushmaydi.")
    else:
        # Ikkita alohida threadda ishga tushirish
        telegram_listener_thread = threading.Thread(target=listen_bot)
        main_bot_thread = threading.Thread(target=run_bot)

        telegram_listener_thread.start()
        main_bot_thread.start()

        # Threadlar tugashini kutish (nazariy jihatdan bu bot doimiy ishlashi kerak)
        telegram_listener_thread.join()
        main_bot_thread.join()

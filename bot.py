# import nest_asyncio  # Olib tashlandi
# nest_asyncio.apply() # Olib tashlandi

# import asyncio  # Olib tashlandi, lekin asinxron funksiyalar ishlashi uchun kerak bo'ladi
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime

TELEGRAM_TOKEN = "8010258907:AAFOD8hyCy6eW0KjLdtHOVW14IMwGsphF7U"
TELEGRAM_USER_ID = "7971306481"

coins = [
    "gtc", "gitcoin", "ach", "alchemy-pay", "ada", "cardano", "adx", "adex",
    "aergo", "aeur", "agix", "singularitynet", "algo", "algorand", "alice",
    "myneighboralice", "amp", "ape", "apecoin", "matic", "polygon", "xvg",
    "verge", "zilliqa", "zil", "vidt-dao", "vidt", "bluzelle", "blz",
    "stellar", "xlm", "chainlink", "link", "bitcoin", "btc", "stratis",
    "strax", "band-protocol", "band", "phala-network", "pha", "the-graph",
    "grt", "polkadot", "dot", "polymesh", "polyx", "solar", "sxp",
    "lto-network", "lto", "vanar-chain", "vanry", "iq", "wax", "waxp",
    "first-digital-usd", "fdusd", "jasmycoin", "jasmy", "nervos-network",
    "ckb", "arbitrum", "arb", "drep", "space-id", "id", "the-sandbox",
    "sand", "near-protocol", "near", "internet-computer", "icp", "xrp",
    "ethereum", "eth", "celo", "kadena", "kda", "render", "rndr",
    "theta-network", "theta", "theta-fuel", "tfuel", "dusk", "loom-network",
    "loom", "avalanche", "avax", "cartesi", "ctsi", "ordi", "syscoin",
    "sys", "ravencoin", "rvn", "litecoin", "ltc", "loopring", "lrc",
    "iota", "livepeer", "lpt", "fetch-ai", "fet", "sei", "bonfida",
    "fida", "phoenix", "phb", "ethereum-classic", "etc", "gifto", "gft",
    "celer-network", "celr", "hive", "horizen", "zen", "iexec-rlc", "rlc",
    "powerledger", "powr", "quant", "qnt", "crypterium", "crpt",
    "digibyte", "dgb", "fio-protocol", "fio", "oasis-network", "rose",
    "dia", "ethereum-name-service", "ens", "rif-token", "rif", "optimism",
    "op", "tron", "trx", "stepn", "gmt", "moonriver", "movr",
    "measurable-data-token", "mdt", "nfprompt", "nfp", "klaytn", "klay",
    "mina", "filecoin", "fil", "dogecoin", "doge", "trust-wallet-token",
    "twt", "superrare", "rare", "moonbeam", "glmr", "vechain", "vet",
    "contentos", "cos", "qtum", "multiversx", "egld", "pyth-network",
    "pyth", "conflux", "cfx", "mantra", "om", "skale", "skl", "xai",
    "portal", "enjin-coin", "enj", "arpa", "playdapp", "pda", "cortex",
    "ctxc", "nano", "xno", "prom", "reserve-rights", "rsr", "sui",
    "iost", "selfkey", "key", "flow", "manta-network", "manta", "tezos",
    "xtz", "bitcoin-cash", "bch", "aptos", "apt", "bitcoin-gold", "btg",
    "dash", "dent", "dent", "lisk", "lsk", "firo", "pax-gold", "paxg",
    "ecash", "xec", "nem", "xem", "komodo", "kmd", "cosmos", "atom",
    "solana", "sol"
]

ALLOWED_EXCHANGES = {
    "superex", "coinex", "kraken", "htx", "toobit", "ascendex", "bitget", "blofin", "poloniex",
    "bitmart", "bitrue", "bydfi", "coinw", "bingx", "ourbit", "btcc", "weex", "binance", "mexc",
    "lbank", "gmgn", "kcex", "digifinex", "coincola"
}

async def fetch_prices_from_coingecko(session, coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/tickers"
    try:
        async with session.get(url, timeout=10) as resp:
            data = await resp.json()
            prices = {}
            for ticker in data.get("tickers", []):
                market = ticker.get("market", {}).get("name", "").lower()
                price = ticker.get("last")
                target = ticker.get("target", "").lower()
                volume = ticker.get("converted_volume", {}).get("usd", 0)
                if (market in [m.lower() for m in ALLOWED_EXCHANGES] and target == "usdt" and price and volume >= 10000):
                    prices[market] = price
            return coin_id, prices
    except Exception:
        return coin_id, {}

async def analyze_prices(context: ContextTypes.DEFAULT_TYPE):
    async with aiohttp.ClientSession() as session:
        for coin_id in coins:
            coin_id, prices = await fetch_prices_from_coingecko(session, coin_id)
            if len(prices) >= 2:
                low = min(prices.items(), key=lambda x: x[1])
                high = max(prices.items(), key=lambda x: x[1])
                diff = (high[1] - low[1]) / low[1] * 100
                if diff >= 2:
                    msg = (
                        f"\u2728 <b>{coin_id.upper()}</b> Arbitraj imkoniyati!\n"
                        f"\U0001F4C9 <b>Foyda:</b> <code>{diff:.2f}%</code>\n"
                        f"\U0001F4CD Sotib olish: <b>{low[0].capitalize()}</b> - <code>{low[1]:.8f} USDT</code>\n"
                        f"\U0001F4CD Sotish: <b>{high[0].capitalize()}</b> - <code>{high[1]:.8f} USDT</code>"
                    )
                    await context.bot.send_message(chat_id=TELEGRAM_USER_ID, text=msg, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Arbitraj bot ishga tushdi. 👋 inshaaloh yaqinda millioner bolaman inshaaloh niyat🙂🙃"
    )

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    async with app:
        app.job_queue.run_repeating(analyze_prices, interval=60)
        print("🤖 Bot ishga tushdi...")
        await app.start()
        await app.updater.start_polling()
        await app.updater.idle()

# if __name__ == "__main__": # Olib tashlandi
#     asyncio.run(main())     # Olib tashlandi

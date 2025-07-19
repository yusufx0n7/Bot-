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
    "XAR/USDT": "arcana-network",
    "ARX/USDT": "arcs",
    "AGC/USDT": "argocoin",
    "ARK/USDT": "ark",
    "ARKHAM/USDT": "arkham",
    "ARPA/USDT": "arpa",
    "ALI/USDT": "artificial-liquid-intelligence",
    "FET/USDT": "artificial-superintelligence-alliance",
    "ARV/USDT": "ariva",
    "AR/USDT": "arweave",
    "ASM/USDT": "assemble-ai",
    "ASSIST/USDT": "assist-ai",
    "ASRR/USDT": "assisterr",
    "ASTR/USDT": "astar",
    "ASTRA/USDT": "astra",
    "ASTO/USDT": "altered-state-token",
    "ATOMARC20/USDT": "atomicals",
    "ATOM/USDT": "cosmos",
    "AURORA/USDT": "aurora",
    "AOA/USDT": "aurora-old",
    "AU/USDT": "autocrypto",
    "ATA/USDT": "automata-network",
    "OLAS/USDT": "autonolas",
    "AVA/USDT": "ava-travala",
    "AVAIL/USDT": "avail",
    "AVAX/USDT": "avalanche-2",
    "AVTM/USDT": "avantis-metaverse",
    "AVIVE/USDT": "avive-world",
    "AVT/USDT": "aventus",
    "AXIS/USDT": "axis-token",
    "AXL/USDT": "axelar",
    "BAD/USDT": "bad-idea-ai",
    "EPT/USDT": "balance",
    "BAI/USDT": "balance-ai",
    "BANANA/USDT": "banana-gun",
    "BAND/USDT": "band-protocol",
    "BAT/USDT": "basic-attention-token",
    "BASEDAI/USDT": "basedai",
    "BATCH/USDT": "batching-ai",
    "BEAMX/USDT": "beam",
    "BDX/USDT": "beldex",
    "BEPRO/USDT": "bepro",
    "BGSC/USDT": "bugscoin",
    "BICO/USDT": "biconomy",
    "BIDP/USDT": "btd-protocol",
    "BIDZ/USDT": "bidz-coin",
    "BFC/USDT": "bifrost",
    "BDP/USDT": "big-data-protocol",
    "BIO/USDT": "bio-protocol",
    "BTC/USDT": "bitcoin",
    "BCH/USDT": "bitcoin-cash",
    "BTG/USDT": "bitcoin-gold",
    "BSAI/USDT": "bitcoin-silver-ai",
    "BTF/USDT": "bitfinity-network",
    "STORE/USDT": "bit-store",
    "TAO/USDT": "bittensor",
    "BITS/USDT": "bitswift",
    "BCUT/USDT": "bitscrunch",
    "BLOK/USDT": "bloktopia",
    "BLM/USDT": "blombard",
    "BLUR/USDT": "blur",
    "BLZ/USDT": "bluzelle",
    "BOBA/USDT": "boba-network",
    "BOLTAI/USDT": "boltai",
    "FIDA/USDT": "bonfida",
    "BDXN/USDT": "bondex",
    "BORA/USDT": "bora",
    "BOSON/USDT": "boson-protocol",
    "BOTIFY/USDT": "botify",
    "BTO/USDT": "bottos",
    "BRCT/USDT": "brc-app",
    "BRG/USDT": "bridge-oracle",
    "BKN/USDT": "brickken",
    "B2/USDT": "bsquared-network",
    "BMT/USDT": "bubblemaps",
    "BUILD/USDT": "build",
    "BUSY/USDT": "busy-dao",
    "BCN/USDT": "bytecoin",
    "KMA/USDT": "calamari-network",
    "CAM/USDT": "camino-network",
    "CAU/USDT": "canxium",
    "CARR/USDT": "carnomaly",
    "CARV/USDT": "carv",
    "CSPR/USDT": "casper",
    "CTSI/USDT": "cartesi",
    "CELO/USDT": "celo",
    "CELR/USDT": "celer-network",
    "TIA/USDT": "celestia",
    "CELL/USDT": "cellframe",
    "CENS/USDT": "censored-ai",
    "CENNZ/USDT": "cenzznet",
    "CERE/USDT": "cere-network",
    "CGAI/USDT": "cryptograd-ai",
    "CGPT/USDT": "chaingpt",
    "LINK/USDT": "chainlink",
    "CHAPZ/USDT": "chappyz",
    "CHATAI/USDT": "chatai-token",
    "CHEQ/USDT": "cheqd",
    "CHZ/USDT": "chiliz",
    "CHEX/USDT": "chintai",
    "CHRP/USDT": "chirpley",
    "CHR/USDT": "chromia",
    "CIRX/USDT": "circular-protocol",
    "CIRUS/USDT": "cirus-foundation",
    "CVC/USDT": "civic",
    "CLV/USDT": "clv",
    "CLBK/USDT": "cloudbric",
    "CDX/USDT": "codexchange",
    "CWEB/USDT": "coinweb",
    "CLS/USDT": "coldstack",
    "COLLAT/USDT": "collaterize",
    "COLX/USDT": "colossusxt",
    "COMBO/USDT": "combo",
    "COMAI/USDT": "commune-ai",
    "CCD/USDT": "concordium",
    "CFX/USDT": "conflux",
    "CNTM/USDT": "connectome",
    "COS/USDT": "contentos",
    "COOKIE/USDT": "cookie",
    "CORAL/USDT": "coral-protocol",
    "COREUM/USDT": "coreum",
    "CTXC/USDT": "cortex",
    "CXT/USDT": "covalent",
    "CRTS/USDT": "cratos",
    "CREO/USDT": "creo-engine",
    "CROS/USDT": "cros",
    "CRPT/USDT": "crypterium",
    "CRU/USDT": "crust-network",
    "TALK/USDT": "cryptalk", # "Talken" ham TALK
    "CRAI/USDT": "cryptify-ai",
    "CRP/USDT": "crypton",
    "AUTOS/USDT": "cryptoautos",
    "CRTAI/USDT": "crt-ai-network",
    "CTP/USDT": "ctomorrow-platform",
    "CUDIS/USDT": "cudis",
    "CUDOS/USDT": "cudos",
    "CYBER/USDT": "cyber",
    "CBAI/USDT": "cyberbots-ai",
    "BEE/USDT": "daobase",
    "RADAR/USDT": "dappradar",
    "D/USDT": "dar-open-network",
    "DASH/USDT": "dash",
    "DHX/USDT": "datahighway",
    "DOP/USDT": "data-ownership-protocol",
    "RING/USDT": "darwinia-network",
    "DDMT/USDT": "ddmtown",
    "MANA/USDT": "decentraland",
    "DCD/USDT": "decideai",
    "DBC/USDT": "deepbrain-chain",
    "DPR/USDT": "deeper-network",
    "DLC/USDT": "deeplink-protocol",
    "DEGEN/USDT": "degen",
    "BOX/USDT": "debox",
    "DCR/USDT": "decred",
    "DTVC/USDT": "delnorte",
    "AGI/USDT": "delysium", # "Artificial Liquid Intelligence" ham AGI
    "DENT/USDT": "dent",
    "DERO/USDT": "dero",
    "DSYNC/USDT": "destra",
    "DEXE/USDT": "dexe",
    "DIA/USDT": "dia",
    "DIAM/USDT": "diam",
    "DGB/USDT": "digibyte",
    "DIMO/USDT": "dimo",
    "DMTR/USDT": "dimitra",
    "DIS/USDT": "distribute-ai",
    "DOCK/USDT": "dock",
    "DOGE/USDT": "dogecoin",
    "DOAI/USDT": "dojo-protocol",
    "DOMIN/USDT": "domin-network",
    "DORA/USDT": "dora-factory",
    "DRGN/USDT": "dragonchain",
    "DREP/USDT": "drep-new",
    "DUCK/USDT": "duckchain",
    "DUSK/USDT": "dusk",
    "DX/USDT": "dxchain-token",
    "XEC/USDT": "ecash",
    "EDGE/USDT": "edge",
    "EMC/USDT": "edge-matrix-computing",
    "EDG/USDT": "edgeware",
    "EFX/USDT": "effect-ai",
    "EGLD/USDT": "multiversx",
    "EGO/USDT": "ego",
    "ECOIN/USDT": "ecoin-official",
    "ELA/USDT": "elastos",
    "XEP/USDT": "electra-protocol",
    "ETN/USDT": "electroneum",
    "ELF/USDT": "aelf",
    "EMT/USDT": "email-token",
    "EMRLD/USDT": "the-emerald-company",
    "NRG/USDT": "energi",
    "ENJ/USDT": "enjin-coin",
    "ENQAI/USDT": "enqai",
    "ENS/USDT": "ethereum-name-service",
    "EPIK/USDT": "epik-prime",
    "AIEPK/USDT": "epik-protocol",
    "EPAY/USDT": "epay",
    "ESX/USDT": "estatex",
    "EAI/USDT": "eternal-ai",
    "ELAND/USDT": "etherland",
    "ETH/USDT": "ethereum",
    "ETC/USDT": "ethereum-classic",
    "ETHW/USDT": "ethereum-pow",
    "ETHO/USDT": "etho-protocol",
    "EURC/USDT": "eurc",
    "EURI/USDT": "eurite",
    "EVER/USDT": "everscale",
    "FMC/USDT": "fame-ai",
    "FTN/USDT": "fasttoken",
    "FTR/USDT": "fautor",
    "FHE/USDT": "mind-network",
    "FIL/USDT": "filecoin",
    "STAR/USDT": "filestar",
    "FIO/USDT": "fio-protocol",
    "FIRO/USDT": "firo",
    "FDUSD/USDT": "first-digital-usd",
    "FLAI/USDT": "flare-ai",
    "FLOCK/USDT": "flock-io",
    "FLOW/USDT": "flow",
    "FLT/USDT": "fluence",
    "FLUX/USDT": "flux",
    "FLY/USDT": "fly-trade",
    "FOG/USDT": "fognet",
    "FORT/USDT": "forta",
    "FRA/USDT": "fractal-network",
    "FREE/USDT": "freedom-coin",
    "FRIC/USDT": "frictionless",
    "FROKAI/USDT": "frokai",
    "FUEL/USDT": "fuel-network",
    "FX/USDT": "function-x",
    "GMRX/USDT": "gaimin",
    "GALA/USDT": "gala",
    "GALAXIS/USDT": "galaxis",
    "GAL/USDT": "galxe",
    "GHX/USDT": "gamercoin",
    "GAS/USDT": "gas",
    "GTH/USDT": "gather",
    "GEOD/USDT": "geodnet",
    "GFT/USDT": "gifto",
    "GINI/USDT": "kalp-network",
    "GTC/USDT": "gitcoin",
    "GLMR/USDT": "moonbeam",
    "GMT/USDT": "gmt",
    "AIAI/USDT": "goatindex-ai",
    "GO/USDT": "gochain",
    "GOC/USDT": "gocrypto-token",
    "GLM/USDT": "golem",
    "GOMINING/USDT": "gomining",
    "GPS/USDT": "goplus-security",
    "ZZZ/USDT": "gosleep",
    "GRASS/USDT": "grass",
    "GRIFFAIN/USDT": "griffain",
    "GRS/USDT": "groestlcoin",
    "GROW/USDT": "grow-token",
    "GRT/USDT": "the-graph",
    "GTAI/USDT": "gt-protocol",
    "GURUNETWORK/USDT": "guru-network",
    "HAI/USDT": "hacken-token",
    "HAHA/USDT": "hasaki",
    "HNS/USDT": "handshake",
    "ONE/USDT": "harmony",
    "HASHAI/USDT": "hashai",
    "HTR/USDT": "hathor",
    "HBAR/USDT": "hedera",
    "HEI/USDT": "heima",
    "HELIO/USDT": "helio",
    "IOT/USDT": "helium-iot",
    "MOBILE/USDT": "helium-mobile",
    "HEU/USDT": "heurist-ai",
    "HIDE/USDT": "hide-coin",
    "HIENS3/USDT": "hiens3",
    "HIGH/USDT": "highstreet",
    "HPO/USDT": "hippocrat",
    "HIVE/USDT": "hive",
    "HINT/USDT": "hive-intelligence",
    "HONEY/USDT": "hivemapper",
    "HLG/USDT": "holograph",
    "HMND/USDT": "humanode",
    "HOT/USDT": "holo",
    "HOOK/USDT": "hooked-protocol",
    "HOPR/USDT": "hopr",
    "ZEN/USDT": "horizen",
    "LOCK/USDT": "houdini-swap",
    "HMT/USDT": "human",
    "HEART/USDT": "humans-ai",
    "HPB/USDT": "hyperblox",
    "HGPT/USDT": "hypergpt",
    "HYPER/USDT": "hyperlane",
    "HYVE/USDT": "hyve",
    "COOL/USDT": "hype3-cool",
    "IAI/USDT": "iai-center",
    "IAG/USDT": "iagon",
    "ICX/USDT": "icon",
    "IDNA/USDT": "idena",
    "RLC/USDT": "iexec-rlc",
    "LIME/USDT": "ime-lab",
    "IMX/USDT": "immutable",
    "ICNT/USDT": "impossible-cloud-network",
    "INF/USDT": "infinaeon",
    "TEER/USDT": "integritee-network",
    "ICP/USDT": "internet-computer",
    "IOST/USDT": "iost",
    "IOTX/USDT": "iotex",
    "IPV/USDT": "ipverse",
    "IQ/USDT": "iq",
    "IRIS/USDT": "irisnet",
    "IRON/USDT": "iron-fish",
    "ISSP/USDT": "issp",
    "ISP/USDT": "ispolink",
    "JASMY/USDT": "jasmycoin",
    "J/USDT": "jambo",
    "JKL/USDT": "jackal-protocol",
    "JU/USDT": "juchain",
    "JKC/USDT": "junkcoin",
    "JUP/USDT": "jupiter",
    "KDA/USDT": "kadena",
    "KAIA/USDT": "kaia",
    "KAITO/USDT": "kaito",
    "KALIS/USDT": "kalichain",
    "KAT/USDT": "kambria",
    "KARCON/USDT": "kaarigar-connect",
    "KLS/USDT": "karlsen",
    "KARRAT/USDT": "karrat",
    "KAS/USDT": "kaspa",
    "KEEP/USDT": "keep-network",
    "KTA/USDT": "keeta",
    "REALKENDO/USDT": "kendo-ai",
    "KEY/USDT": "selfkey",
    "KIN/USDT": "kin",
    "KIP/USDT": "kip-protocol",
    "KITEAI/USDT": "kiteai",
    "KLAY/USDT": "klaytn",
    "KLEAR/USDT": "krayon-klear-token",
    "KOIN/USDT": "koinos",
    "KOLZ/USDT": "kolz",
    "KMD/USDT": "komodo",
    "KRO/USDT": "kroma",
    "KSM/USDT": "kusama",
    "KYVE/USDT": "kyve-network",
    "LA/USDT": "lagrange",
    "LKI/USDT": "laika-ai",
    "LAIKA/USDT": "laika", # same token as Laika AI
    "LAMB/USDT": "lambda",
    "LTX/USDT": "lattice-token",
    "LAVITA/USDT": "lavita-ai",
    "L3/USDT": "layer3",
    "EDGEN/USDT": "layeredge",
    "ZRO/USDT": "layerzero",
    "LBC/USDT": "lbry-credits",
    "LENS/USDT": "lens",
    "LF/USDT": "lf",
    "LFT/USDT": "lifeform-token",
    "LL/USDT": "lightlink",
    "LMT/USDT": "limitus",
    "LSK/USDT": "lisk",
    "LITH/USDT": "lithium",
    "LTC/USDT": "litecoin",
    "LPT/USDT": "livepeer",
    "DAPP/USDT": "liquidapps",
    "LRC/USDT": "loopring",
    "LOOKS/USDT": "looksrare",
    "LSS/USDT": "lossless",
    "LTO/USDT": "lto-network",
    "LKY/USDT": "luckycoin",
    "LMR/USDT": "lumerin",
    "LUNA/USDT": "terra",
    "LYX/USDT": "lukso",
    "MAGIC/USDT": "treasure",
    "MAIAR/USDT": "maiar",
    "NetZ/USDT": "mainnetz",
    "MAND/USDT": "mande-network",
    "MGO/USDT": "mango-network",
    "MANTA/USDT": "manta-network",
    "OM/USDT": "mantra",
    "MAPO/USDT": "map-protocol",
    "POND/USDT": "marlin",
    "MARSH/USDT": "unmarshal",
    "MASK/USDT": "mask-network",
    "MAT/USDT": "matchain",
    "MATH/USDT": "math",
    "MATIC/USDT": "polygon",
    "MDT/USDT": "measurable-data-token",
    "MEALY/USDT": "mealy",
    "ME/USDT": "magic-eden",
    "HERO/USDT": "metahero",
    "MTS/USDT": "meta-plus-token",
    "MTL/USDT": "metal-dao",
    "MPLX/USDT": "metaplex",
    "METIS/USDT": "metis",
    "MICRO/USDT": "micro-gpt",
    "MLK/USDT": "mil-k",
    "MINA/USDT": "mina",
    "MINT/USDT": "mint-blockchain",
    "MOBI/USDT": "mobius",
    "MOB/USDT": "mobilecoin",
    "MOCA/USDT": "moca-coin",
    "MXC/USDT": "mxc", # "Moonchain" also MXC
    "MOVR/USDT": "moonriver",
    "MOR/USDT": "morpheus",
    "MIND/USDT": "morpheus-infrastructure-node",
    "MOVE/USDT": "movement",
    "MUA/USDT": "mua-dao",
    "MTV/USDT": "multivac",
    "MVL/USDT": "mvl",
    "ALICE/USDT": "myneighboralice",
    "MYRIA/USDT": "myria",
    "SYL/USDT": "mydid",
    "MYST/USDT": "mysterium",
    "MYTH/USDT": "mythos",
    "XNO/USDT": "nano",
    "NATIX/USDT": "natix-network",
    "NXN/USDT": "naxion",
    "NEAR/USDT": "near-protocol",
    "NEBL/USDT": "neblio",
    "XEM/USDT": "nem",
    "NEON/USDT": "neon-evm",
    "NERTA/USDT": "nerta",
    "CKB/USDT": "nervos-network",
    "NETVR/USDT": "netvrk",
    "NEI/USDT": "neurashi",
    "NEUR/USDT": "neur-sh",
    "NEURONI/USDT": "neuroni-ai",
    "NRN/USDT": "neuron",
    "NEUTON/USDT": "neuton",
    "NTRN/USDT": "neutron",
    "GEMAI/USDT": "next-gem-ai",
    "NXRA/USDT": "nexera",
    "NEXA/USDT": "nexa",
    "NXS/USDT": "nexus",
    "NEXUS/USDT": "nexuschain",
    "NAI/USDT": "neyroai", # "Nuklai" also NAI
    "NFM/USDT": "nfmart",
    "NFP/USDT": "nfprompt",
    "NFTAI/USDT": "nftai",
    "NIL/USDT": "nillion",
    "NKN/USDT": "nkn",
    "NRK/USDT": "nordek",
    "NOS/USDT": "nosana",
    "NULS/USDT": "nuls",
    "NCDT/USDT": "nuco-cloud",
    "NLK/USDT": "nulink",
    "NTX/USDT": "nunet",
    "NUM/USDT": "numbers-protocol",
    "NYM/USDT": "nym",
    "OAS/USDT": "oasys",
    "OBORTECH/USDT": "obortech",
    "OBOT/USDT": "obortech", # Same as OBORTECH
    "OCEAN/USDT": "ocean-protocol",
    "OCN/USDT": "odyssey",
    "OCTA/USDT": "octaspace",
    "OCTO/USDT": "octonetai",
    "OGN/USDT": "origin-protocol",
    "AIOT/USDT": "okzoo",
    "OL/USDT": "open-loot",
    "OMG/USDT": "omg-network",
    "OMNI/USDT": "omni-network",
    "ONG/USDT": "ontology-gas",
    "EDU/USDT": "open-campus",
    "OPEN/USDT": "open-custody-protocol",
    "OBX/USDT": "openblox",
    "SERV/USDT": "openserv",
    "OP/USDT": "optimism",
    "OPTI/USDT": "optimus-ai",
    "ORA/USDT": "ora",
    "ORAI/USDT": "oraichain",
    "ORBR/USDT": "orbler",
    "ORDI/USDT": "ordi",
    "ORE/USDT": "ore",
    "TRAC/USDT": "origintrail",
    "OXT/USDT": "orchid",
    "PATEX/USDT": "patex",
    "PRX/USDT": "parex",
    "PRQ/USDT": "parsiq",
    "PART/USDT": "particl",
    "PARTI/USDT": "particle-network",
    "MPC/USDT": "partisia-blockchain",
    "PAXG/USDT": "pax-gold",
    "USDP/USDT": "pax-dollar",
    "PEAQ/USDT": "peaq",
    "PPC/USDT": "peercoin",
    "PEP/USDT": "pepecoin",
    "PHA/USDT": "phala-network",
    "SOUL/USDT": "phantasma",
    "PHI/USDT": "phicoin",
    "PHB/USDT": "phoenix",
    "PIB/USDT": "pibble",
    "PIN/USDT": "pinlink",
    "ARRR/USDT": "pirate-chain",
    "PIVX/USDT": "pivx",
    "PDA/USDT": "playdapp",
    "LAT/USDT": "platon",
    "PLI/USDT": "plugin-decentralized-oracle",
    "PLUME/USDT": "plume",
    "POKT/USDT": "pocket-network",
    "POL/USDT": "pol-ex-matic",
    "POLYX/USDT": "polymesh",
    "ZKJ/USDT": "polyhedra-network",
    "NCT/USDT": "polyswarm",
    "PORT3/USDT": "port3-network",
    "PORTAL/USDT": "portal",
    "POWR/USDT": "powerledger",
    "PRAI/USDT": "privasea-ai",
    "RESCUE/USDT": "project-rescue",
    "PROM/USDT": "prom",
    "PROPS/USDT": "propbase",
    "PROPC/USDT": "propchain",
    "PRO/USDT": "propy",
    "PUMLX/USDT": "pumx",
    "PUNDIAI/USDT": "pundi-ai",
    "PUNDIX/USDT": "pundi-x-new",
    "UFI/USDT": "purefi-protocol",
    "PYTH/USDT": "pyth-network",
    "QGOV/USDT": "q-protocol",
    "QNT/USDT": "quant",
    "QRL/USDT": "quantum-resistant-ledger",
    "QUAI/USDT": "quai-network",
    "QKC/USDT": "quarkchain",
    "QTUM/USDT": "qtum",
    "RAD/USDT": "radworks",
    "RDN/USDT": "raiden-network-token",
    "RXD/USDT": "radiant",
    "RARI/USDT": "rari",
    "RAVEN/USDT": "raven-protocol",
    "RVN/USDT": "ravencoin",
    "RAZE/USDT": "raze-network",
    "REACH/USDT": "reach",
    "REEF/USDT": "reef",
    "REI/USDT": "rei-network",
    "REALIS/USDT": "realis-worlds",
    "BRIC/USDT": "redbrick",
    "RNT/USDT": "reental",
    "RNDR/USDT": "render",
    "RAI/USDT": "reploy",
    "REQ/USDT": "request",
    "RSC/USDT": "researchcoin",
    "RSR/USDT": "reserve-rights",
    "REV/USDT": "revain",
    "REX/USDT": "revox",
    "RIF/USDT": "rootstock-infrastructure-framework",
    "RLUSD/USDT": "ripple-usd",
    "RIZ/USDT": "rivalz-network",
    "XRT/USDT": "robonomics-network",
    "ROAM/USDT": "roam",
    "RON/USDT": "ronin",
    "ROSE/USDT": "oasis-network",
    "RWN/USDT": "rowan-coin",
    "ROY/USDT": "royalty",
    "RUNECOIN/USDT": "rsic-genesis-rune",
    "RWAI/USDT": "rwai",
    "RYO/USDT": "ryo-coin",
    "SABAI/USDT": "sabai-protocol",
    "SC/USDT": "safe-circle",
    "SFP/USDT": "safepal",
    "SRC/USDT": "safe-road-club-ai",
    "SAGA/USDT": "saga",
    "SAHARA/USDT": "sahara-ai",
    "SAITO/USDT": "saito",
    "SKR/USDT": "saakuru-protocol",
    "ALL/USDT": "sallar",
    "SAND/USDT": "the-sandbox",
    "SAVM/USDT": "satoshi-vm",
    "SCP/USDT": "scprime",
    "SCR/USDT": "scroll",
    "SDN/USDT": "shiden-network",
    "SCRT/USDT": "secret",
    "SEI/USDT": "sei",
    "SEKOIA/USDT": "sekoia-by-virtuals",
    "SLF/USDT": "self-chain",
    "SNSY/USDT": "sensay",
    "DVPN/USDT": "sentinel",
    "UPP/USDT": "sentinel-protocol",
    "SETAI/USDT": "sentient-ai",
    "SHDW/USDT": "shadow-token",
    "SHM/USDT": "shardeum",
    "SDM/USDT": "shieldeum",
    "SC/USDT": "siacoin",
    "SIGN/USDT": "sign",
    "SIMMI/USDT": "simmi-token",
    "AGIX/USDT": "singularitynet",
    "SINGULAR/USDT": "singular",
    "SIX/USDT": "six",
    "SKALE/USDT": "skale",
    "SKATE/USDT": "skate",
    "SKAI/USDT": "skillful-ai",
    "SKYAI/USDT": "skyai",
    "SVL/USDT": "slash-vision-labs",
    "SLN/USDT": "smart-layer-network",
    "MFG/USDT": "smart-mfg",
    "SMRT/USDT": "smartpractice",
    "SMH/USDT": "spacemesh",
    "SOL/USDT": "solana",
    "SXP/USDT": "solar",
    "LAYER/USDT": "solayer",
    "SOLVE/USDT": "solve",
    "SOLVEX/USDT": "solvex-network",
    "S/USDT": "sonic-prev-ftm",
    "SONIC/USDT": "sonic-svm",
    "SOON/USDT": "soon",
    "SOPH/USDT": "sophon",
    "SOSO/USDT": "sosovalue",
    "SOUL/USDT": "phantasma", # Same as Phantasma
    "SOAI/USDT": "sozoai",
    "ID/USDT": "space-id",
    "SXT/USDT": "space-and-time",
    "SPORE/USDT": "spore-fun",
    "SQD/USDT": "subsquid",
    "SSV/USDT": "ssv-network",
    "STX/USDT": "stacks",
    "ANS/USDT": "star-protocol",
    "SNT/USDT": "status",
    "STEEM/USDT": "steem",
    "XLM/USDT": "stellar",
    "FITFI/USDT": "step-app",
    "STORJ/USDT": "storj",
    "STORAGENT/USDT": "storagent",
    "WSTOR/USDT": "storagechain",
    "STMX/USDT": "stormx",
    "STOS/USDT": "stratos",
    "STRAX/USDT": "stratis",
    "DATA/USDT": "streamr",
    "SUI/USDT": "sui",
    "NS/USDT": "sui-name-service",
    "SUIRWA/USDT": "sui-rwa",
    "SUKU/USDT": "suku",
    "RARE/USDT": "superrare",
    "SERO/USDT": "super-zero-protocol",
    "SUPRA/USDT": "supra",
    "BZZ/USDT": "swarm",
    "SNAI/USDT": "swarmnode-ai",
    "SWASH/USDT": "swash",
    "SWAN/USDT": "swan-chain-formerly-filswan",
    "SWEAT/USDT": "sweat-economy",
    "SWFTC/USDT": "swftcoin",
    "XYM/USDT": "symbol",
    "SNS/USDT": "synesis-one",
    "SYNT/USDT": "synternet",
    "SYS/USDT": "syscoin",
    "TADA/USDT": "ta-da",
    "TAG/USDT": "tagger",
    "TAKI/USDT": "taki-games",
    "TSLT/USDT": "tamkin",
    "TARA/USDT": "taraxa",
    "TAI/USDT": "tars-ai",
    "TEER/USDT": "integritee-network",
    "TRB/USDT": "tellor",
    "TNSR/USDT": "tensor",
    "XAUt/USDT": "tether-gold",
    "XTZ/USDT": "tezos",
    "ARENA/USDT": "the-arena",
    "TON/USDT": "the-open-network",
    "TFUEL/USDT": "theta-fuel",
    "THETA/USDT": "theta-network",
    "WNK/USDT": "the-winkyverse",
    "THT/USDT": "thought",
    "THREE/USDT": "three-protocol-token",
    "TIA/USDT": "celestia", # Same as Celestia
    "TOKEN/USDT": "tokenfi",
    "TMAI/USDT": "token-metrics-ai",
    "TTM/USDT": "tradetomato",
    "TRACE/USDT": "trace-network-labs",
    "TRL/USDT": "triall",
    "TRISIG/USDT": "tri-sigma",
    "TRX/USDT": "tron",
    "TUSD/USDT": "trueusd",
    "TRUF/USDT": "truflation",
    "TWT/USDT": "trust-wallet-token",
    "TRVL/USDT": "trvl",
    "UBX/USDT": "ubix-network",
    "U2U/USDT": "u2u-network",
    "UMA/USDT": "uma",
    "FUND/USDT": "unification",
    "UNQ/USDT": "unique-network",
    "UQC/USDT": "uquid-coin",
    "USDC/USDT": "usd-coin",
    "VAL/USDT": "validity",
    "VANRY/USDT": "vanar-chain",
    "VANA/USDT": "vana",
    "B3TR/USDT": "vebetterdao",
    "VET/USDT": "vechain",
    "VXV/USDT": "vectorspace-ai",
    "VELO/USDT": "velo",
    "VEMP/USDT": "vemp",
    "VVV/USDT": "venice-token",
    "XVG/USDT": "verge",
    "VDA/USDT": "verida",
    "VEX/USDT": "vexanium",
    "VTHO/USDT": "vethor-token",
    "VIC/USDT": "viction",
    "VIDT/USDT": "vidt-dao",
    "DAOX/USDT": "virtualdaos",
    "VV/USDT": "virtual-versions",
    "VIS/USDT": "envision",
    "VITE/USDT": "vite",
    "VSYS/USDT": "v-systems",
    "WAXP/USDT": "wax",
    "WCT/USDT": "walletconnect",
    "WAL/USDT": "walrus",
    "WAVES/USDT": "waves",
    "WEST/USDT": "waves-enterprise",
    "PROMPT/USDT": "wayfinder",
    "WRX/USDT": "wazirx",
    "WELL/USDT": "well3",
    "WIFI/USDT": "wifi-map",
    "WIN/USDT": "winklink",
    "WXT/USDT": "wirex-token",
    "WSDM/USDT": "wisdomise-ai",
    "WIT/USDT": "witnet",
    "WOOP/USDT": "woonkly-power",
    "WORK/USDT": "work-x",
    "WMT/USDT": "world-mobile-token",
    "WLD/USDT": "worldcoin",
    "W/USDT": "wormhole",
    "WOW/USDT": "wownero",
    "XAI/USDT": "xai",
    "XBG/USDT": "xborg",
    "XDAO/USDT": "xdao",
    "XEL/USDT": "xelis",
    "XEM/USDT": "nem",
    "XIDR/USDT": "xidr",
    "XTAG/USDT": "xhashtag-ai",
    "UTK/USDT": "xmoney",
    "XNO/USDT": "nano", # Same as Nano
    "XR/USDT": "xraders",
    "XRP/USDT": "xrp",
    "XRPH/USDT": "xrp-healthcare",
    "XSGD/USDT": "xsgd",
    "XTZ/USDT": "tezos", # Same as Tezos
    "Y8U/USDT": "y8u",
    "YNE/USDT": "yesnoerror",
    "YOM/USDT": "yom",
    "ZANO/USDT": "zano",
    "ZAYA/USDT": "zayaai",
    "ZBU/USDT": "zeebu",
    "ZEC/USDT": "zcash",
    "ZNN/USDT": "zenon",
    "ZENQ/USDT": "zenqira",
    "ZIG/USDT": "zignaly",
    "ZIL/USDT": "zilliqa",
    "ZRC/USDT": "zircuit",
    "ZKJ/USDT": "polyhedra-network"
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

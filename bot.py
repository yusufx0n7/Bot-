import asyncio
import logging
from telegram import Bot
import json
import requests
import datetime
import pytz

# --- Logging sozlamalari ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Telegram bot sozlamalari ---
TELEGRAM_BOT_TOKEN = '8010258907:AAFOD8hyCy6eW0KjLdtHOVW14IMwGsphF7U' # Bu yerga Telegram bot tokeningizni kiriting
TELEGRAM_CHAT_ID = '7971306481'     # Bu yerga o'zingizning chat ID'ingizni kiriting

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# --- Koinlar ro'yxati (siz taqdim etgan va tozalangan ro'yxatlar) ---
PAIR_LIST = [
    "gtc", "ach", "ada", "adx", "aergo", "aeur", "agix", "algo", "alice",
    "amp", "ape", "matic", "xvg", "zilliqa", "vidt-dao", "bluzelle", "stellar",
    "chainlink", "bitcoin", "stratis", "band-protocol", "phala-network", "the-graph",
    "polkadot", "polymesh", "solar", "lto-network", "vanar-chain", "iq", "wax",
    "first-digital-usd", "jasmycoin", "nervos-network", "arbitrum", "drep-new",
    "space-id", "the-sandbox", "near-protocol", "internet-computer", "xrp", "ethereum",
    "celo", "kadena", "render", "theta-network", "theta-fuel", "dusk", "loom-network",
    "avalanche", "cartesi", "ordi", "syscoin", "ravencoin", "litecoin", "loopring",
    "iota", "livepeer", "artificial-superintelligence-alliance", "sei", "bonfida",
    "phoenix", "ethereum-classic", "gifto", "celer-network", "hive", "horizen",
    "iexec-rlc", "powerledger", "quant", "crypterium", "digibyte", "fio-protocol",
    "oasis-network", "dia", "ethereum-name-service", "rootstock-infrastructure-framework",
    "optimism", "tron", "gmt", "moonriver", "measurable-data-token", "nfprompt",
    "klaytn", "mina", "filecoin", "dogecoin", "trust-wallet-token", "superrare",
    "moonbeam", "vechain", "contentos", "qtum", "multiversx", "pyth-network",
    "conflux", "mantra", "skale", "xai", "portal", "enjin-coin", "arpa",
    "playdapp", "cortex", "nano", "prom", "reserve-rights", "sui", "iost",
    "selfkey", "flow", "manta-network", "tezos", "bitcoin-cash", "aptos",
    "bitcoin-gold", "dash", "dent", "lisk", "firo", "pax-gold", "ecash", "nem",
    "komodo", "cosmos", "solana", "ocean-protocol", "mask-network", "rei-network",
    "streamr", "viction", "waves", "automata-network", "cyber", "radworks",
    "api3", "blur", "gas", "axelar", "terra", "galxe", "decentraland", "ardor",
    "stacks", "icon", "golem", "wazirx", "decred", "steem", "metal-dao", "nuls",
    "flux", "secret", "biconomy", "combo", "hedera", "civic", "request", "dexe",
    "origin-protocol", "mobilecoin", "highstreet", "ava-travala", "usd-coin", "arweave",
    "chiliz", "harmony", "storj", "trueusd", "pivx", "irisnet", "basic-attention-token",
    "metis", "celestia", "nkn", "xmoney", "marlin", "wormhole", "quarkchain",
    "hooked-protocol", "saga", "astar", "ark", "tensor", "beamx", "kusama",
    "omni-network", "aelf", "holo", "winklink", "tellor", "bittensor", "stormx",
    "status", "safepal", "siacoin", "orchid", "ontology-gas", "iotex", "toncoin",
    "fame-ai", "alephium", "hasaki", "tether-gold", "origintrail", "casper", "zeebu",
    "fasttoken", "layerzero", "ipverse", "zignaly", "vethor-token", "orbler",
    "boba-network", "cyberbots-ai", "helium-mobile", "nosana", "hivemapper",
    "world-mobile-token", "shadow-token", "nym", "pocket-network", "cudos",
    "octaspace", "coinweb", "gaimin", "aleph.im", "iagon", "kyve-network",
    "xraders", "delysium", "ozone-chain", "oraichain", "artificial-liquid-intelligence",
    "forta", "platon", "agoras-currency-of-tau", "victoria-vr", "dimitra",
    "moca-coin", "dkargo", "commune-ai", "hacken-token", "numbers-protocol",
    "sentinel-protocol", "uxlink", "data-ownership-protocol", "avive-world",
    "aurora", "nunet", "ime-lab", "cere-network", "neyroai", "gt-protocol",
    "frokai", "hypergpt", "oort", "parsiq", "vectorspace-ai", "degen", "koinos",
    "synesis-one", "lumerin", "qna3.ai", "xelis", "ddmtown", "deepbrain-chain",
    "nuco.cloud", "waves-enterprise", "eclipse", "gamercoin", "optimus-ai",
    "ta-da", "trvl", "big-data-protocol", "bad-idea-ai", "phantasma", "bitscrunch",
    "pibble", "robonomics.network", "swash", "lambda", "math", "subquery-network",
    "lithium", "lossless", "bridge-oracle", "avail", "mande-network",
    "crypto-ai-robo.com", "metahero", "netvrk", "smart-layer-network", "effect-ai",
    "chirpley", "ispolink", "edge-matrix-computing", "dock", "purefi-protocol",
    "gny", "dxchain-token", "b-cube.ai", "dojo-protocol", "propy", "axis-token",
    "lbry-credits", "clintex-cti", "gocrypto-token", "three-protocol-token", "idena",
    "aimedis-new", "ubix.network", "cirus-foundation", "all-in", "neurashi", "aurora",
    "ojamu", "raze-network", "ubex", "censored-ai", "triall", "pawtocol", "covalent",
    "connectome", "altered-state-token", "autonolas", "dtec", "work-x", "grow-token",
    "lavita-ai", "arbius", "epik-protocol", "multiverse", "enqai", "humans.ai", "y8u",
    "ai-network", "jackal-protocol", "morpheus-infrastructure-node", "tradetomato",
    "basedai", "issp", "aventis-metaverse", "nfmart", "the-winkyverse", "next-gem-ai",
    "human", "alphascan-ai", "eternal-ai", "datahighway", "balance-ai", "a3s-protocol",
    "ore", "inheritance-art", "raven-protocol", "swan-chain-formerly-filswan", "vemp",
    "flourishing-ai", "cloudbric", "kin", "meta-plus-token", "lukso", "neuroni-ai",
    "ai-pin", "layer3", "trace-network-labs", "gosleep", "chappyz", "kambria", "aion",
    "acria.ai", "ctomorrow-platform", "the-emerald-company", "gomining", "epik-prime",
    "myria", "autocrypto", "cindicator", "bottos", "eurite", "bloktopia", "runesterminal",
    "rsic-genesis-rune", "well3", "alpine-f1-team", "verida", "galaxis", "energi",
    "build", "decideai", "5ire", "slash-vision-labs", "star-protocol", "fautor",
    "bidz-coin", "port3-network", "kiteai", "super-zero-protocol", "chatai-token",
    "alltoscan", "hathor", "spacemesh", "woonkly-power", "anyone-protocol", "chromia",
    "oasys", "zano", "concordium", "nulink", "wisdomise-ai", "synternet", "q-protocol",
    "self-chain", "xdao", "email-token", "hyve", "kaarigar-connect", "arcs", "gtc-ai",
    "taraxa", "radiant", "electra-protocol", "nexa", "agentlayer", "epic-cash", "saito",
    "zenon", "abelian", "humanode", "multivac", "integritee-network", "mainnetz",
    "hide-coin", "busy-dao", "wyzth", "clv", "karlsen", "canxium", "allbridge",
    "ice-open-network", "kalichain", "witnet", "hiens3", "unique-network",
    "calamari-network", "ecoin-official", "ethereumpow", "reach", "friend3", "ecomi",
    "bora", "mxc", "adventure-gold", "swarm", "looksrare", "polyswarm",
    "virtual-versions", "swftcoin", "wirex-token", "taki-games", "polyhedra-network",
    "dora-factory", "wifi-map", "sweat-economy", "gala", "dappradar", "eurc",
    "iron-fish", "scroll", "pol-ex-matic", "carv", "kylacoin", "thought", "naxion",
    "andromeda", "lightlink", "nordek", "satoshivm", "liquidapps", "holograph",
    "zenqira", "aia-chain", "beldex", "truflation", "aki-network", "aleo", "cellframe",
    "ariva", "freedom-coin", "metaplex", "uma", "pirate-chain", "dero", "hopr",
    "colossusxt", "crypton", "grass", "bytecoin", "vertcoin", "cros", "mua-dao",
    "fognet", "fractal-network", "wownero", "the-root-network", "xborg", "kaia",
    "natix-network", "ctrl-wallet", "assemble-ai", "telos", "kardiachain",
    "shiden-network", "xhashtag-ai", "lifeform-token", "ego", "tars-ai",
    "sui-name-service", "omg-network", "bit-store", "altura", "cookie", "aeternity",
    "bytomdao", "gochain", "batching.ai", "plugin-decentralized-oracle",
    "darwinia-network", "revain", "mydid", "v.systems", "vexanium", "edgeware",
    "ame-chain", "nexera", "coreum", "zircuit", "sensay", "brickken", "laika-ai",
    "supra", "pumx", "banana-gun", "acent", "gather", "brc-app", "rowan-coin",
    "tamkin", "xrp-healthcare", "open-loot", "tornado-cash", "peaq", "mvl",
    "open-campus", "simmi-token", "xion", "ora", "alkimi", "gravity", "bgsc",
    "fluence", "magic-eden", "movement", "dimo", "heurist-ai", "obortech", "klear",
    "neuton", "kip-protocol", "propchain", "agents-ai", "ripple-usd", "kaspa",
    "worldcoin", "chromia-chr", "shieldeum", "ai-agent-layer", "guru-network",
    "unmarshal", "vana", "nirvana", "skillful-ai", "bepro", "solvex-network",
    "rwa-inc.", "codexchain", "deeper-network", "rari", "u2u-network", "pax-dollar",
    "peercoin", "quantum-resistant-ledger", "elastos", "storx-network", "helium-iot",
    "sentinel", "stratos", "bitfinity-network", "kroma", "laika", "handshake",
    "crust-network", "paal-ai", "karrat", "kolz", "octonetai", "edge", "griffain",
    "parex", "circular-protocol", "researchcoin", "hippocrat", "cryptoautos",
    "pepecoin", "luckycoin", "setai", "junkcoin", "reploy", "flock.io",
    "network-dsync", "bio-protocol", "mobius", "mysterium", "raiden-network-token",
    "yom", "odyssey", "sozoai", "aixbt-by-virtuals", "sonic-prev.-ftm",
    "crt-ai-network", "storagent", "boltai", "fuel-network", "function-x", "cheqd",
    "neur.sh", "limitus", "zayaai", "sekoia-by-virtuals", "realis-worlds", "hterm",
    "hashai", "cgai", "suirwa", "nodecoin", "bidp", "vis", "spore.fun",
    "goatindex.ai", "dgh", "ultima", "act-i-the-ai-prophecy", "energy-web-token",
    "dragonchain", "phicoin", "ai16z", "plume", "hat", "sonic", "virtualdaos",
    "chintai", "dar-open-network", "venice-token", "creo", "mor", "goplus-security",
    "yesnoerror", "creatorbid", "alchemist-ai", "symbol", "etherland",
    "hive-intelligence", "network3", "lak3", "ntmpi", "onyxcoin",
    "partisia-blockchain", "sui-desci-agents", "aventus", "blocery", "boson-protocol",
    "cennznet", "unification", "solve", "bitswift", "hyperblox", "neblio", "smart-mfg",
    "blockv", "suku", "analog", "diam", "atomicals", "camino-network", "story",
    "nexus", "ancient8", "coldstack", "scprime", "etho-protocol", "sallar",
    "academic-labs", "electroneum", "kaito", "groestlcoin", "filestar", "particl",
    "micro-gpt", "psjglobal", "storagechain", "agoric", "myshell", "epay",
    "open-custody-protocol", "assist-ai", "aist", "collaterize", "jobseek-ai",
    "safecircle", "swarmnode.ai", "maiar", "artgee-ai", "immutable", "kendo-ai",
    "helio", "ai-rig-complex", "bifrost", "skey-network", "xterio", "blombard",
    "openblox", "bubblemaps", "roam", "hype3-cool", "singular", "uquid-coin",
    "nillion", "cryptalk", "gini", "kalp-network", "particle-network", "nireafty",
    "safe-road-club-ai", "straitsx-usd", "xsgd", "xidr", "paraverse", "walrus",
    "flare-ai", "sender", "milk", "wayfinder", "walletconnect", "mind-network",
    "talken", "hyperlane", "saakuru-protocol", "balance", "arkham", "ankr",
    "altlayer", "royalty", "mansory", "arcana-network", "sign", "pundi-x-new", "aqa",
    "agixt", "treasure", "nuklai", "amb", "neutron", "nexuschain", "ava-ai", "vite",
    "okzoo", "cratos", "propbase", "step-app", "obortech", "carnomaly", "cryptify-ai",
    "argocoin", "frictionless", "heima", "space-and-time", "gpus", "domin-network",
    "jupiter", "skyai", "six", "upcx", "bsquared-network", "rwai", "reental",
    "okratech-token", "muxyai", "neon-evm", "tri-sigma", "duckchain",
    "alaya-governance-token", "mint-blockchain", "privasea-ai", "keep-network",
    "houdini-swap", "openserv", "rivalz-network", "keeta", "reef", "soon",
    "quai-network", "ryo-coin", "epic-chain", "soso-value", "awe-network",
    "project-rescue", "jambo", "sophon", "patex", "moonchain", "orbiter-finance",
    "iai-center", "assisterr-asrr", "delnorte", "inferium", "shardeum", "layeredge",
    "debox", "block-vault", "subsquid", "everscale", "bondex", "neuron", "nerta",
    "nftai", "lagrange", "infinaeon", "lens", "ab", "tokenfi", "ssv.network",
    "solayer", "zcash", "fly.trade", "mythos", "ronin", "cudis", "pinlink",
    "deeplink-protocol", "skate", "ao", "astra", "token-metrics-ai", "reddio",
    "the-arena", "gag-token", "esx", "matchain", "nam", "daobase", "tagger",
    "bitcoin-silver-ai", "redbrick", "botify", "smartpractice", "coral-protocol",
    "cli.ai", "newton-protocol", "sahara-ai", "mango-network", "distribute.ai",
    "humanity-protocol", "delorean", "revox", "paragon-tweaks", "mealy",
    "impossible-cloud-network", "waterminder", "paynetic-ai", "velo", "lf",
    "vebetterdao", "map-protocol", "chaingpt", "cobak-token", "blockprompt",
    "sabai-protocol", "juchain", "pundi-ai", "infinity-ground", "validity", "b3-base"
]

COINGECKO_IDS = [
    "gitcoin", "alchemy-pay", "cardano", "adex", "aergo", "anchored-coins-aeur",
    "singularitynet", "algorand", "myneighboralice", "amp", "apecoin", "polygon",
    "verge", "zil", "vidt", "blz", "xlm", "link", "btc", "strax", "band",
    "pha", "grt", "dot", "polyx", "sxp", "lto", "vanry", "iq", "waxp",
    "fdusd", "jasmy", "ckb", "arb", "drep", "id", "sand", "near", "icp",
    "xrp", "eth", "celo", "kda", "rndr", "theta", "tfuel", "dusk", "loom",
    "avax", "ctsi", "ordi", "sys", "rvn", "ltc", "lrc", "iota", "lpt", "fet",
    "sei", "fida", "phb", "etc", "gft", "celr", "hive", "zen", "rlc", "powr",
    "qnt", "crpt", "dgb", "fio", "rose", "dia", "ens", "rif", "op", "trx",
    "gmt", "movr", "mdt", "nfp", "klay", "mina", "fil", "doge", "twt", "rare",
    "glmr", "vet", "cos", "qtum", "egld", "pyth", "cfx", "om", "skl", "xai",
    "portal", "enj", "arpa", "pda", "ctxc", "xno", "prom", "rsr", "sui", "iost",
    "key", "flow", "manta", "xtz", "bch", "apt", "btg", "dash", "dent", "lsk",
    "firo", "paxg", "xec", "xem", "kmd", "atom", "sol", "ocean", "mask", "rei",
    "data", "vic", "waves", "ata", "cyber", "rad", "api3", "blur", "gas", "axl",
    "luna", "gal", "mana", "ardr", "stx", "icx", "glm", "wrx", "dcr", "steem",
    "mtl", "nuls", "flux", "scrt", "bico", "combo", "hbar", "cvc", "req", "dexe",
    "ogn", "mob", "high", "ava", "usdc", "ar", "chz", "one", "storj", "tusd",
    "pivx", "iris", "bat", "metis", "tia", "nkn", "utk", "pond", "w", "qkc",
    "hook", "saga", "astr", "ark", "tnsr", "beam", "ksm", "omni", "elf", "hot",
    "win", "trb", "tao", "stmx", "snt", "sfp", "sc", "oxt", "ong", "iotx", "ton",
    "fmc", "alph", "haha", "xaut", "trac", "cspr", "zbu", "ftn", "zro", "ipv",
    "zig", "vtho", "orbr", "boba", "cbai", "mobile", "nos", "honey", "wmt",
    "shdw", "nym", "pokt", "cudos", "octa", "cweb", "gmrx", "aleph", "iag",
    "kyve", "xr", "agi", "ozo", "orai", "ali", "fort", "lat", "agrs", "vr", "dmtr",
    "moca", "dka", "comai", "hai", "num", "upp", "uxlink", "dop", "avive", "aurora",
    "ntx", "lime", "cere", "nai", "gtai", "frokai", "hgpt", "oort", "prq", "vxv",
    "degen", "koin", "sns", "lmr", "gpt", "xel", "ddmt", "dbc", "ncdt", "west",
    "eclipse", "ghx", "opti", "tada", "trvl", "bdp", "bad", "soul", "bcut", "pib",
    "xrt", "swash", "lamb", "math", "sqt", "lith", "lss", "brg", "avail", "mand",
    "cair", "hero", "netvr", "sln", "efx", "chrp", "isp", "emc", "dock", "ufi",
    "gny", "dx", "bcube", "doai", "pro", "axis", "lbc", "cti", "goc", "three",
    "idna", "aimx", "ubx", "cirus", "allin", "nei", "aoa", "oja", "raze", "ubex",
    "cens", "trl", "upi", "cxt", "cntm", "asto", "olas", "dtec", "work", "grow",
    "lavita", "aius", "aiepk", "ai", "enqai", "heart", "y8u", "ain", "jkl", "mind",
    "ttm", "basedai", "issp", "avtm", "nfm", "wnk", "gemai", "hmt", "ascn", "eai",
    "dhx", "bai", "aa", "ore", "iai", "raven", "swan", "vemp", "ai", "clbk", "kin",
    "mts", "lyx", "neuroni", "ai", "l3", "trace", "zzz", "chapz", "kat", "aion",
    "acria", "ctp", "emrld", "gomining", "epik", "myria", "au", "cnd", "bto",
    "euri", "blok", "runi", "runecoin", "well", "alpine", "vda", "galaxis", "nrg",
    "build", "dcd", "5ire", "svl", "ans", "ftr", "bidz", "port3", "kiteai", "sero",
    "chatai", "ats", "htr", "smh", "woop", "anyone", "chr", "oas", "zano", "ccd",
    "nlk", "wsdm", "synt", "qgov", "slf", "xdao", "emt", "hyve", "karcon", "arx",
    "gtc-ai", "tara", "rxd", "xep", "nexa", "agent", "epic", "saito", "znn", "abel",
    "hmnd", "mtv", "teer", "netz", "hide", "busy", "wyz", "clv", "kls", "cau",
    "abr", "ice", "kalis", "wit", "hiens3", "unq", "kma", "ecoin", "ethw", "reach",
    "f3", "omi", "bora", "mxc", "agld", "bzz", "looks", "nct", "vv", "swftc", "wxt",
    "taki", "zkj", "dora", "wifi", "sweat", "gala", "radar", "eurc", "iron", "scr",
    "pol", "carv", "kcn", "tht", "nxn", "andr", "ll", "nrk", "savm", "dapp", "hlg",
    "zenq", "aia", "bdx", "truf", "aki", "aleo", "cell", "arv", "free", "mplx",
    "uma", "arrr", "dero", "hopr", "colx", "crp", "grass", "bcn", "vtc", "cros",
    "mua", "fog", "fra", "wow", "root", "xbg", "kaia", "natix", "ctrl", "asm",
    "telos", "kai", "sdn", "xtag", "lft", "ego", "tai", "ns", "omg", "store", "alu",
    "cookie", "ae", "btm", "go", "batch", "pli", "ring", "rev", "syl", "vsys",
    "vex", "edg", "ame", "nxra", "coreum", "zrc", "oort", "sensay", "bkn", "lki",
    "supra", "pumx", "banana", "ace", "fmc", "gth", "brct", "rwn", "tslt", "xrph",
    "ol", "torn", "peaq", "mvl", "edu", "simmi", "xion", "ora", "ads", "g",
    "bugscoin", "flt", "me", "move", "dimo", "heu", "obortech", "krayon-klear-token",
    "neuton", "kip", "propc", "agent", "rlusd", "kas", "wld", "chromia-chr", "sdm",
    "aifun", "guru", "marsh", "vana", "vana", "skai", "bepro", "solvex", "rwa",
    "cdx", "dpr", "rari", "u2u", "usdp", "ppc", "qrl", "ela", "srx", "iot", "dvpn",
    "stos", "btf", "kro", "laika", "hns", "cru", "paal", "karrat", "kolz", "octo",
    "edge", "griffain", "prx", "cirx", "rsc", "hpo", "autos", "pep", "lky",
    "sentient-ai", "jkc", "rai", "flock", "destra", "bio", "mobi", "myst", "rdn",
    "yom", "ocn", "soai", "aixbt", "s", "crtai", "storagent", "boltai", "fuel", "fx",
    "cheq", "neur", "lmt", "zaya", "sekoia", "realis", "hiero-terminal", "hashai",
    "cryptograd-al", "sui-rwa", "nc", "btd-protocol", "envision", "spore", "aiai",
    "digihealth", "ultima", "act", "ewt", "drgn", "phi", "ai16z", "plume", "top-hat",
    "sonic-svm", "daox", "chex", "d", "vvv", "creo-engine", "morpheus", "gps", "yne",
    "bid", "alch", "xym", "eland", "hint", "n3", "lake", "timpi", "xcn", "mpc",
    "desci", "avt", "bly", "boson", "cennz", "fund", "solve", "bits", "hpb", "nebl",
    "mfg", "vee", "suku", "anlog", "diam", "atomarc20", "cam", "ip", "nxs", "a8",
    "cls", "scp", "etho", "all", "aax", "etn", "kaito", "grs", "star", "part",
    "micro", "cycon", "wstor", "bld", "shell", "epay", "open", "assist", "aisim",
    "collat", "jobseek", "sc", "snai", "maiar", "gb", "imx", "realkendo", "helio",
    "arc", "bfc", "skey", "xter", "blm", "obx", "bmt", "roam", "cool", "singular",
    "uqc", "nil", "talk", "gini", "kalp-network", "parti", "nfc", "src", "xusd",
    "xsgd", "xidr", "pvs", "wal", "flai", "sender", "mlk", "prompt", "wct", "fhe",
    "talk", "hyper", "skr", "ept", "ankr", "ankr", "alt", "roy", "mnsry",
    "xar", "sign", "pundix", "aqa", "agixt", "magic", "nai", "airdao", "ntrn",
    "nexus", "avaai", "vite", "aiot", "crts", "props", "fitfi", "obot", "carr",
    "crai", "agc", "fric", "hei", "sxt", "gpus", "domin", "jup", "skyai", "six",
    "upc", "b2", "rwai", "rnt", "ort", "mai", "neon", "trisig", "duck", "agt",
    "mint", "praai", "keep", "lock", "serv", "riz", "kta", "reef", "soon",
    "quai-network", "ryo", "epic", "soso", "awe", "rescue", "j", "soph", "patex",
    "mxc", "obt", "iai", "asrr", "delnorte", "ifr", "shm", "edgen", "box", "bvt",
    "sqd", "ever", "bdxn", "nrn", "nerta", "nft-ai", "la", "inf", "lens", "ab",
    "token", "ssv", "layer", "zec", "fly", "myth", "ron", "cudis", "pin",
    "dlc", "skate", "ao", "astra", "tmai", "rdo", "arena", "gag", "estatex",
    "mat", "nam", "bee", "tag", "bsai", "bric", "botify", "smrt", "coral",
    "cmd", "newt", "sahara", "mgo", "dis", "h", "dmc", "rex", "paragon",
    "mealy", "icnt", "wmdr", "pyn", "velo", "lf", "b3tr", "mapo", "cgpt", "cbk",
    "blpt", "sabai", "ju", "pundiai", "ain", "val", "b3"
]

# --- Coingecko API URL'i ---
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# --- Funksiyalar ---
def get_coin_prices(coin_ids):
    """
    CoinGecko API'dan koinlarning USD narxini oladi.
    """
    try:
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd'
        }
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()  # HTTP xatolarini tekshirish
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"CoinGecko API'dan narxlarni olishda xato: {e}")
        return None

def format_price_message(prices):
    """
    Narxlarni chiroyli formatda xabar qilib qaytaradi.
    """
    if not prices:
        return "Hozircha koinlar narxlari mavjud emas."

    message_parts = ["*Hozirgi koin narxlari:*\n\n"]
    for i, coin_id in enumerate(COINGECKO_IDS):
        price_data = prices.get(coin_id)
        if price_data and 'usd' in price_data:
            price = price_data['usd']
            # Narxni o'zbek so'miga o'tkazish (taxminiy kurs)
            uzs_price = price * 12600 # Hozirgi dollar kursi taxminan 12600 so'm deb olindi
            message_parts.append(
                f"*{PAIR_LIST[i].upper()}*: ${price:,.8f} (~{uzs_price:,.2f} UZS)\n"
            )
        else:
            message_parts.append(f"*{PAIR_LIST[i].upper()}*: Narx topilmadi\n")
            logging.warning(f"CoinGecko ID uchun narx topilmadi: {coin_id}")

    # Vaqtni qo'shish
    uz_timezone = pytz.timezone('Asia/Tashkent')
    current_time_uz = datetime.datetime.now(uz_timezone).strftime("%Y-%m-%d %H:%M:%S")
    message_parts.append(f"\n_Yangilangan vaqt (Toshkent): {current_time_uz}_")

    return "".join(message_parts)

async def send_price_update():
    """
    Telegramga narx yangilanishini yuboradi.
    """
    logging.info("Narxlarni yangilash jarayoni boshlandi...")
    prices = get_coin_prices(COINGECKO_IDS)
    if prices:
        message = format_price_message(prices)
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
            logging.info("Narx yangilanishi Telegramga muvaffaqiyatli yuborildi.")
        except Exception as e:
            logging.error(f"Telegramga xabar yuborishda xato: {e}")
    else:
        logging.warning("Narxlar olinmadi, Telegramga xabar yuborilmadi.")

async def main():
    """
    Botning asosiy ishga tushirish funksiyasi.
    Har 5 daqiqada narx yangilanishini yuboradi.
    """
    while True:
        await send_price_update()
        await asyncio.sleep(300) # 5 daqiqa = 300 soniya

if __name__ == '__main_main__':
    # Asosiy funksiyani ishga tushirish
    asyncio.run(main())

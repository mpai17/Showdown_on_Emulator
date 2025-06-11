-- Pokemon Battle Data Script for Gen 1 Games
-- This script reads memory from Pokemon Red/Blue to display battle information
-- and automate enemy responses during battles

-- Memory Address Constants
local MEMORY = {
    -- Player Pokemon data
    PLAYER_PARTY_BASE = 0xD16B,
    PLAYER_SPECIES_ARRAY = 0xD164,
    
    -- Enemy Pokemon data
    ENEMY_PARTY_BASE = 0xD8A4,
    ENEMY_SPECIES_ARRAY = 0xD89D,
    
    -- Party Pokemon Data Structure (44 bytes per Pokemon)
    -- Each Pokemon starts at PLAYER_PARTY_BASE + (index * 44)
    POKEMON_DATA_SIZE = 44,

    -- Needed for updating Pokemon currently battling
    BATTLE_MON_MOVES = 0xD01C,
    BATTLE_MON_PP = 0xD02D,
    ENEMY_MON_MOVES = 0xCFED,
    ENEMY_MON_PP = 0xCFFE,
    DAMAGE = 0xD0D7,
    PLAYER_SLEEP_COUNTER = 0xD018,
    ENEMY_SLEEP_COUNTER = 0xCFE9,
    PLAYER_CONFUSE_COUNTER = 0xD06B,
    ENEMY_CONFUSE_COUNTER = 0xD070,
    
    -- Party Pokemon Nicknames (11 bytes per Pokemon)
    PLAYER_NICKS_BASE = 0xD2B5,
    ENEMY_NICKS_BASE = 0xD9EE,
    POKEMON_NICK_SIZE = 11,
    
    -- Pokemon Data Offsets (relative to each Pokemon's base address)
    POKEMON_SPECIES_OFFSET = 0x00,         -- Pokemon species ID
    CURRENT_HP_OFFSET = 0x01,              -- Current HP (2 bytes, big-endian)
    PSEUDO_LEVEL_OFFSET = 0x03,            -- Pseudo-level (not actual level)
    STATUS_OFFSET = 0x04,                  -- Status conditions (sleep, paralysis, etc.)
    TYPE1_OFFSET = 0x05,                   -- Primary type
    TYPE2_OFFSET = 0x06,                   -- Secondary type
    CATCH_RATE_OFFSET = 0x07,              -- Catch rate/Held item
    MOVES_OFFSET = 0x08,                   -- Move 1 ID
    TRAINER_ID_OFFSET = 0x0C,              -- Trainer ID (2 bytes, big-endian)
    EXPERIENCE_OFFSET = 0x0E,              -- Experience (3 bytes, big-endian)
    HP_EV_OFFSET = 0x11,                   -- HP EV (2 bytes, big-endian)
    ATTACK_EV_OFFSET = 0x13,               -- Attack EV (2 bytes, big-endian)
    DEFENSE_EV_OFFSET = 0x15,              -- Defense EV (2 bytes, big-endian)
    SPEED_EV_OFFSET = 0x17,                -- Speed EV (2 bytes, big-endian)
    SPECIAL_EV_OFFSET = 0x19,              -- Special EV (2 bytes, big-endian)
    ATTACK_DEFENSE_IV_OFFSET = 0x1B,       -- Attack and Defense IVs (4 bits each)
    SPEED_SPECIAL_IV_OFFSET = 0x1C,        -- Speed and Special IVs (4 bits each)
    MOVES_PP_OFFSET = 0x1D,                -- Move 1 PP
    ACTUAL_LEVEL_OFFSET = 0x21,            -- Actual level
    MAX_HP_OFFSET = 0x22,                  -- Max HP (2 bytes, big-endian)
    ATTACK_STAT_OFFSET = 0x24,             -- Attack stat (2 bytes, big-endian)
    DEFENSE_STAT_OFFSET = 0x26,            -- Defense stat (2 bytes, big-endian)
    SPEED_STAT_OFFSET = 0x28,              -- Speed stat (2 bytes, big-endian)
    SPECIAL_STAT_OFFSET = 0x2A,            -- Special stat (2 bytes, big-endian)

    
    -- Party metadata
    PARTY_COUNT = 0xD163,                  -- Number of Pokemon in party
    
    -- Battle UI and state
    CURSOR_X_POS = 0xCC25,
    CURSOR_Y_POS = 0xCC24,
    SELECTED_INDEX = 0xCC26,
    BATTLE_MENU_STATE = 0xC470,
    WHOSE_TURN = 0xFFF3,
    CRIT_FLAG = 0xD05E,
    MOVE_MISS = 0xD05F,
    
    -- ROM
    MASTER_SPEED_COMPARE = 0x03C339,    -- Bank #15 0x4339
    SLAVE_SPEED_COMPARE = 0x03C330,     -- Bank #15 0x4330
    PLAYER_PARALYSIS_CHECK = 0x03D948,  -- Bank #15 0x5948
    ENEMY_PARALYSIS_CHECK = 0x03E9C9,   -- Bank #15 0x69C9
    PLAYER_CONFUSE_CHECK = 0x03D919,    -- Bank #15 0x5919
    ENEMY_CONFUSE_CHECK = 0x03E956,     -- Bank #15 0x6956
    DAMAGE_CHECK = 0x03E6A4,            -- Bank #15 0x66A4
    SLEEP_SET_COUNTER = 0x03F234,      -- Bank #15 0x7234
    CONFUSE_SET_COUNTER = 0x03F994,    -- Bank #15 0x7994
    STAT_DOWN_EFFECT = 0x03F580,        -- Bank #15 0x7580
    FLINCH_CHECK = 0x03F87C,            -- Bank #15 0x787C
    POISON_CHECK = 0x03F293,            -- Bank #15 0x7293
    PLAYER_STATUSED = 0x03F340,         -- Bank #15 0x7340
    ENEMY_STATUSED = 0x03F3A8,          -- Bank #15 0x73A8
    
    -- Flags
    PLAYER_TURN_FLAG = 0x40,
    ENEMY_TURN_FLAG = 0x50,
    PARALYZED_FLAG = 0x00,
    NOT_PARALYZED_FLAG = 0xFF,
    CONFUSE_HIT_FLAG = 0xFF,
    CONFUSE_NO_HIT_FLAG = 0x00,
    STAT_DOWN_FLAG = 0x00,
    STAT_NOT_DOWN_FLAG = 0xFF,
    FLINCH_FLAG = 0x00,
    FLINCH_NOT_FLAG = 0xFF,
    STATUSED_FLAG = 0x00,
    STATUSED_NOT_FLAG = 0xFF,
    
    -- Move data
    SELECTED_MOVE_ID = 0xCFD2,
    MOVE_PP_BASE = 0xD02D,
    
    -- Pokemon data in battle
    CURRENT_ENEMY_POKEMON_SPECIES = 0xCFE5,
    CURRENT_ENEMY_POKEMON_HP = 0xCFE6,
    ENEMY_MOVE_BASE = 0xCFED,
}

-- Character table for english versions
local CHARMAP = {
    ["A"] = 0x80, ["B"] = 0x81, ["C"] = 0x82, ["D"] = 0x83, ["E"] = 0x84, ["F"] = 0x85, ["G"] = 0x86, ["H"] = 0x87, ["I"] = 0x88, ["J"] = 0x89, ["K"] = 0x8A, ["L"] = 0x8B, ["M"] = 0x8C, ["N"] = 0x8D, ["O"] = 0x8E, ["P"] = 0x8F, ["Q"] = 0x90, ["R"] = 0x91, ["S"] = 0x92, ["T"] = 0x93, ["U"] = 0x94, ["V"] = 0x95, ["W"] = 0x96, ["X"] = 0x97, ["Y"] = 0x98, ["Z"] = 0x99,
    ["a"] = 0xA0, ["b"] = 0xA1, ["c"] = 0xA2, ["d"] = 0xA3, ["e"] = 0xA4, ["f"] = 0xA5, ["g"] = 0xA6, ["h"] = 0xA7, ["i"] = 0xA8, ["j"] = 0xA9, ["k"] = 0xAA, ["l"] = 0xAB, ["m"] = 0xAC, ["n"] = 0xAD, ["o"] = 0xAE, ["p"] = 0xAF, ["q"] = 0xB0, ["r"] = 0xB1, ["s"] = 0xB2, ["t"] = 0xB3, ["u"] = 0xB4, ["v"] = 0xB5, ["w"] = 0xB6, ["x"] = 0xB7, ["y"] = 0xB8, ["z"] = 0xB9,
    ["0"] = 0xF6, ["1"] = 0xF7, ["2"] = 0xF8, ["3"] = 0xF9, ["4"] = 0xFA, ["5"] = 0xFB, ["6"] = 0xFC, ["7"] = 0xFD, ["8"] = 0xFE, ["9"] = 0xFF,
    ["("] = 0x9A, [")"] = 0x9B, [":"] = 0x9C, [";"] = 0x9D, ["["] = 0x9E, ["]"] = 0x9F, ["'"] = 0xE0, ["-"] = 0xE3, ["?"] = 0xE6, ["!"] = 0xE7, ["."] = 0xE8, ["/"] = 0xF3, [","] = 0xF4, [" "] = 0x7F, ["@"] = 0x50,
    ["é"] = 0xBA, ["'d"] = 0xBB, ["'l"] = 0xBC, ["'s"] = 0xBD, ["'t"] = 0xBE, ["'v"] = 0xBF, ["'r"] = 0xE4, ["'m"] = 0xE5,
    ["‘"] = 0x70, ["’"] = 0x71, ["“"] = 0x72, ["”"] = 0x73, ["…"] = 0x75, ["×"] = 0xF1, ["¥"] = 0xF0, ["♂"] = 0xEF, ["♀"] = 0xF5
}

-- Type names table
local TYPEMAP = {
    ["Normal"] = 0x00, ["Fighting"] = 0x01, ["Flying"] = 0x02, ["Poison"] = 0x03,
    ["Ground"] = 0x04, ["Rock"] = 0x05, ["Bird"] = 0x06, ["Bug"] = 0x07,
    ["Ghost"] = 0x08, ["Fire"] = 0x14, ["Water"] = 0x15, ["Grass"] = 0x16,
    ["Electric"] = 0x17, ["Psychic"] = 0x18, ["Ice"] = 0x19, ["Dragon"] = 0x1A
}

-- Move names table (all 165 moves)
local MOVE_DATA = {
    ["Pound"] = {id = 0x01, pp = 35}, ["Karate Chop"] = {id = 0x02, pp = 25}, ["Double Slap"] = {id = 0x03, pp = 10}, ["Comet Punch"] = {id = 0x04, pp = 15}, ["Mega Punch"] = {id = 0x05, pp = 20},
    ["Pay Day"] = {id = 0x06, pp = 20}, ["Fire Punch"] = {id = 0x07, pp = 15}, ["Ice Punch"] = {id = 0x08, pp = 15}, ["ThunderPunch"] = {id = 0x09, pp = 15}, ["Scratch"] = {id = 0x0A, pp = 35},
    ["ViceGrip"] = {id = 0x0B, pp = 30}, ["Guillotine"] = {id = 0x0C, pp = 5}, ["Razor Wind"] = {id = 0x0D, pp = 10}, ["Swords Dance"] = {id = 0x0E, pp = 30}, ["Cut"] = {id = 0x0F, pp = 30},
    ["Gust"] = {id = 0x10, pp = 35}, ["Wing Attack"] = {id = 0x11, pp = 35}, ["Whirlwind"] = {id = 0x12, pp = 20}, ["Fly"] = {id = 0x13, pp = 15}, ["Bind"] = {id = 0x14, pp = 20},
    ["Slam"] = {id = 0x15, pp = 20}, ["Vine Whip"] = {id = 0x16, pp = 25}, ["Stomp"] = {id = 0x17, pp = 20}, ["Double Kick"] = {id = 0x18, pp = 30}, ["Mega Kick"] = {id = 0x19, pp = 5},
    ["Jump Kick"] = {id = 0x1A, pp = 10}, ["Rolling Kick"] = {id = 0x1B, pp = 15}, ["Sand-Attack"] = {id = 0x1C, pp = 15}, ["Headbutt"] = {id = 0x1D, pp = 15}, ["Horn Attack"] = {id = 0x1E, pp = 25},
    ["Fury Attack"] = {id = 0x1F, pp = 20}, ["Horn Drill"] = {id = 0x20, pp = 5}, ["Tackle"] = {id = 0x21, pp = 35}, ["Body Slam"] = {id = 0x22, pp = 15}, ["Wrap"] = {id = 0x23, pp = 20},
    ["Take Down"] = {id = 0x24, pp = 20}, ["Thrash"] = {id = 0x25, pp = 10}, ["Double-Edge"] = {id = 0x26, pp = 15}, ["Tail Whip"] = {id = 0x27, pp = 30}, ["Poison Sting"] = {id = 0x28, pp = 35},
    ["Twineedle"] = {id = 0x29, pp = 20}, ["Pin Missile"] = {id = 0x2A, pp = 20}, ["Leer"] = {id = 0x2B, pp = 30}, ["Bite"] = {id = 0x2C, pp = 25}, ["Growl"] = {id = 0x2D, pp = 40},
    ["Roar"] = {id = 0x2E, pp = 20}, ["Sing"] = {id = 0x2F, pp = 15}, ["Supersonic"] = {id = 0x30, pp = 20}, ["SonicBoom"] = {id = 0x31, pp = 20}, ["Disable"] = {id = 0x32, pp = 20},
    ["Acid"] = {id = 0x33, pp = 30}, ["Ember"] = {id = 0x34, pp = 25}, ["Flamethrower"] = {id = 0x35, pp = 15}, ["Mist"] = {id = 0x36, pp = 30}, ["Water Gun"] = {id = 0x37, pp = 25},
    ["Hydro Pump"] = {id = 0x38, pp = 5}, ["Surf"] = {id = 0x39, pp = 15}, ["Ice Beam"] = {id = 0x3A, pp = 10}, ["Blizzard"] = {id = 0x3B, pp = 5}, ["Psybeam"] = {id = 0x3C, pp = 20},
    ["BubbleBeam"] = {id = 0x3D, pp = 20}, ["Aurora Beam"] = {id = 0x3E, pp = 20}, ["Hyper Beam"] = {id = 0x3F, pp = 5}, ["Peck"] = {id = 0x40, pp = 35}, ["Drill Peck"] = {id = 0x41, pp = 20},
    ["Submission"] = {id = 0x42, pp = 25}, ["Low Kick"] = {id = 0x43, pp = 20}, ["Counter"] = {id = 0x44, pp = 20}, ["Seismic Toss"] = {id = 0x45, pp = 20}, ["Strength"] = {id = 0x46, pp = 15},
    ["Absorb"] = {id = 0x47, pp = 25}, ["Mega Drain"] = {id = 0x48, pp = 15}, ["Leech Seed"] = {id = 0x49, pp = 10}, ["Growth"] = {id = 0x4A, pp = 20}, ["Razor Leaf"] = {id = 0x4B, pp = 25},
    ["SolarBeam"] = {id = 0x4C, pp = 10}, ["PoisonPowder"] = {id = 0x4D, pp = 35}, ["Stun Spore"] = {id = 0x4E, pp = 30}, ["Sleep Powder"] = {id = 0x4F, pp = 15}, ["Petal Dance"] = {id = 0x50, pp = 10},
    ["String Shot"] = {id = 0x51, pp = 40}, ["Dragon Rage"] = {id = 0x52, pp = 10}, ["Fire Spin"] = {id = 0x53, pp = 15}, ["ThunderShock"] = {id = 0x54, pp = 30}, ["Thunderbolt"] = {id = 0x55, pp = 15},
    ["Thunder Wave"] = {id = 0x56, pp = 20}, ["Thunder"] = {id = 0x57, pp = 10}, ["Rock Throw"] = {id = 0x58, pp = 15}, ["Earthquake"] = {id = 0x59, pp = 10}, ["Fissure"] = {id = 0x5A, pp = 5},
    ["Dig"] = {id = 0x5B, pp = 10}, ["Toxic"] = {id = 0x5C, pp = 10}, ["Confusion"] = {id = 0x5D, pp = 25}, ["Psychic"] = {id = 0x5E, pp = 10}, ["Hypnosis"] = {id = 0x5F, pp = 20},
    ["Meditate"] = {id = 0x60, pp = 40}, ["Agility"] = {id = 0x61, pp = 30}, ["Quick Attack"] = {id = 0x62, pp = 30}, ["Rage"] = {id = 0x63, pp = 20}, ["Teleport"] = {id = 0x64, pp = 20},
    ["Night Shade"] = {id = 0x65, pp = 15}, ["Mimic"] = {id = 0x66, pp = 10}, ["Screech"] = {id = 0x67, pp = 40}, ["Double Team"] = {id = 0x68, pp = 15}, ["Recover"] = {id = 0x69, pp = 20},
    ["Harden"] = {id = 0x6A, pp = 30}, ["Minimize"] = {id = 0x6B, pp = 10}, ["SmokeScreen"] = {id = 0x6C, pp = 20}, ["Confuse Ray"] = {id = 0x6D, pp = 10}, ["Withdraw"] = {id = 0x6E, pp = 40},
    ["Defense Curl"] = {id = 0x6F, pp = 40}, ["Barrier"] = {id = 0x70, pp = 20}, ["Light Screen"] = {id = 0x71, pp = 30}, ["Haze"] = {id = 0x72, pp = 30}, ["Reflect"] = {id = 0x73, pp = 20},
    ["Focus Energy"] = {id = 0x74, pp = 30}, ["Bide"] = {id = 0x75, pp = 10}, ["Metronome"] = {id = 0x76, pp = 10}, ["Mirror Move"] = {id = 0x77, pp = 20}, ["Selfdestruct"] = {id = 0x78, pp = 5},
    ["Egg Bomb"] = {id = 0x79, pp = 10}, ["Lick"] = {id = 0x7A, pp = 30}, ["Smog"] = {id = 0x7B, pp = 20}, ["Sludge"] = {id = 0x7C, pp = 20}, ["Bone Club"] = {id = 0x7D, pp = 20},
    ["Fire Blast"] = {id = 0x7E, pp = 5}, ["Waterfall"] = {id = 0x7F, pp = 15}, ["Clamp"] = {id = 0x80, pp = 15}, ["Swift"] = {id = 0x81, pp = 20}, ["Skull Bash"] = {id = 0x82, pp = 10},
    ["Spike Cannon"] = {id = 0x83, pp = 15}, ["Constrict"] = {id = 0x84, pp = 35}, ["Amnesia"] = {id = 0x85, pp = 20}, ["Kinesis"] = {id = 0x86, pp = 15}, ["Softboiled"] = {id = 0x87, pp = 10},
    ["Hi Jump Kick"] = {id = 0x88, pp = 10}, ["Glare"] = {id = 0x89, pp = 30}, ["Dream Eater"] = {id = 0x8A, pp = 15}, ["Poison Gas"] = {id = 0x8B, pp = 40}, ["Barrage"] = {id = 0x8C, pp = 20},
    ["Leech Life"] = {id = 0x8D, pp = 10}, ["Lovely Kiss"] = {id = 0x8E, pp = 10}, ["Sky Attack"] = {id = 0x8F, pp = 5}, ["Transform"] = {id = 0x90, pp = 10}, ["Bubble"] = {id = 0x91, pp = 30},
    ["Dizzy Punch"] = {id = 0x92, pp = 10}, ["Spore"] = {id = 0x93, pp = 15}, ["Flash"] = {id = 0x94, pp = 20}, ["Psywave"] = {id = 0x95, pp = 15}, ["Splash"] = {id = 0x96, pp = 40},
    ["Acid Armor"] = {id = 0x97, pp = 20}, ["Crabhammer"] = {id = 0x98, pp = 10}, ["Explosion"] = {id = 0x99, pp = 5}, ["Fury Swipes"] = {id = 0x9A, pp = 15}, ["Bonemerang"] = {id = 0x9B, pp = 10},
    ["Rest"] = {id = 0x9C, pp = 10}, ["Rock Slide"] = {id = 0x9D, pp = 10}, ["Hyper Fang"] = {id = 0x9E, pp = 15}, ["Sharpen"] = {id = 0x9F, pp = 30}, ["Conversion"] = {id = 0xA0, pp = 30},
    ["Tri Attack"] = {id = 0xA1, pp = 10}, ["Super Fang"] = {id = 0xA2, pp = 10}, ["Slash"] = {id = 0xA3, pp = 20}, ["Substitute"] = {id = 0xA4, pp = 10}, ["Struggle"] = {id = 0xA5, pp = 1}
}

-- Create reverse lookup tables for backward compatibility
local MOVE_NAMES = {}  -- id -> name
local MOVE_PPS = {}    -- id -> pp

for name, data in pairs(MOVE_DATA) do
    MOVE_NAMES[data.id] = name
    MOVE_PPS[data.id] = data.pp
end

-- Species names table (all 151 Pokémon)
local SPECIES_NAMES = {
    [0x01] = "Rhydon", [0x02] = "Kangaskhan", [0x03] = "Nidoran♂", [0x04] = "Clefairy", [0x05] = "Spearow",
    [0x06] = "Voltorb", [0x07] = "Nidoking", [0x08] = "Slowbro", [0x09] = "Ivysaur", [0x0A] = "Exeggutor",
    [0x0B] = "Lickitung", [0x0C] = "Exeggcute", [0x0D] = "Grimer", [0x0E] = "Gengar", [0x0F] = "Nidoran♀",
    [0x10] = "Nidoqueen", [0x11] = "Cubone", [0x12] = "Rhyhorn", [0x13] = "Lapras", [0x14] = "Arcanine",
    [0x15] = "Mew", [0x16] = "Gyarados", [0x17] = "Shellder", [0x18] = "Tentacool", [0x19] = "Gastly",
    [0x1A] = "Scyther", [0x1B] = "Staryu", [0x1C] = "Blastoise", [0x1D] = "Pinsir", [0x1E] = "Tangela",
    [0x21] = "Growlithe", [0x22] = "Onix", [0x23] = "Fearow", [0x24] = "Pidgey", [0x25] = "Slowpoke",
    [0x26] = "Kadabra", [0x27] = "Graveler", [0x28] = "Chansey", [0x29] = "Machoke", [0x2A] = "Mr. Mime",
    [0x2B] = "Hitmonlee", [0x2C] = "Hitmonchan", [0x2D] = "Arbok", [0x2E] = "Parasect", [0x2F] = "Psyduck",
    [0x30] = "Drowzee", [0x31] = "Golem", [0x33] = "Magmar", [0x35] = "Electabuzz", [0x36] = "Magneton",
    [0x37] = "Koffing", [0x39] = "Mankey", [0x3A] = "Seel", [0x3B] = "Diglett", [0x3C] = "Tauros",
    [0x40] = "Farfetch'd", [0x41] = "Venonat", [0x42] = "Dragonite", [0x46] = "Doduo", [0x47] = "Poliwag",
    [0x48] = "Jynx", [0x49] = "Moltres", [0x4A] = "Articuno", [0x4B] = "Zapdos", [0x4C] = "Ditto",
    [0x4D] = "Meowth", [0x4E] = "Krabby", [0x52] = "Vulpix", [0x53] = "Ninetales", [0x54] = "Pikachu",
    [0x55] = "Raichu", [0x58] = "Dratini", [0x59] = "Dragonair", [0x5A] = "Kabuto", [0x5B] = "Kabutops",
    [0x5C] = "Horsea", [0x5D] = "Seadra", [0x60] = "Sandshrew", [0x61] = "Sandslash", [0x62] = "Omanyte",
    [0x63] = "Omastar", [0x64] = "Jigglypuff", [0x65] = "Wigglytuff", [0x66] = "Eevee", [0x67] = "Flareon",
    [0x68] = "Jolteon", [0x69] = "Vaporeon", [0x6A] = "Machop", [0x6B] = "Zubat", [0x6C] = "Ekans",
    [0x6D] = "Paras", [0x6E] = "Poliwhirl", [0x6F] = "Poliwrath", [0x70] = "Weedle", [0x71] = "Kakuna",
    [0x72] = "Beedrill", [0x74] = "Dodrio", [0x75] = "Primeape", [0x76] = "Dugtrio", [0x77] = "Venomoth",
    [0x78] = "Dewgong", [0x7B] = "Caterpie", [0x7C] = "Metapod", [0x7D] = "Butterfree", [0x7E] = "Machamp",
    [0x80] = "Golduck", [0x81] = "Hypno", [0x82] = "Golbat", [0x83] = "Mewtwo", [0x84] = "Snorlax",
    [0x85] = "Magikarp", [0x88] = "Muk", [0x8A] = "Kingler", [0x8B] = "Cloyster", [0x8D] = "Electrode",
    [0x8E] = "Clefable", [0x8F] = "Weezing", [0x90] = "Persian", [0x91] = "Marowak", [0x93] = "Haunter",
    [0x94] = "Abra", [0x95] = "Alakazam", [0x96] = "Pidgeotto", [0x97] = "Pidgeot", [0x98] = "Starmie",
    [0x99] = "Bulbasaur", [0x9A] = "Venusaur", [0x9B] = "Tentacruel", [0x9D] = "Goldeen", [0x9E] = "Seaking",
    [0xA3] = "Ponyta", [0xA4] = "Rapidash", [0xA5] = "Rattata", [0xA6] = "Raticate", [0xA7] = "Nidorino",
    [0xA8] = "Nidorina", [0xA9] = "Geodude", [0xAA] = "Porygon", [0xAB] = "Aerodactyl", [0xAD] = "Magnemite",
    [0xB0] = "Charmander", [0xB1] = "Squirtle", [0xB2] = "Charmeleon", [0xB3] = "Wartortle", [0xB4] = "Charizard",
    [0xB9] = "Oddish", [0xBA] = "Gloom", [0xBB] = "Vileplume", [0xBC] = "Bellsprout", [0xBD] = "Weepinbell",
    [0xBE] = "Victreebel"
}

local SPECIES_DATA = {}
for id, name in pairs(SPECIES_NAMES) do
    SPECIES_DATA[name] = id
end

-- Configuration constants
local CONFIG = {
    FRAME_UPDATE_INTERVAL = 60,     -- Update party every 60 frames
    BUTTON_HOLD_FRAMES = 10,        -- Default frames to hold a button
    SWITCH_HOLD_FRAMES = 30,        -- Frames to hold button during switch
    BATTLE_MENU_SELECT_VALUE = 122, -- Value when an option is selected in battle
    ANIMATION_WAIT_FRAMES = 900     -- Longer wait time for some animations
}

-- Global state variables
local state = {
    backToMainMenu = true,          -- Track if we're back at the main menu
    lastSelectedPokeIndex = 0,      -- Store the last selected Pokemon index
    currentEnemyMoveIndex = 0,      -- Current enemy move index
    waitingForMenuReturn = false    -- Whether we're waiting to return to menu
}

-- Global RNG Sync variables
local RNG = {
    playerFirst = true,             -- Determines who moves first for a speed tie
    flinched = false,
    playerDamage = 100,
    playerCrit = 0,
    playerMoveMiss = 0,
    playerStatDownEffect = false,
    playerFullyParalyzed = false,
    playerHitConfuse = false,
    playerStatused = false,
    playerWokeUp = false,
    playerSnappedOut = false,
    enemyDamage = 100,
    enemyCrit = 0,
    enemyMoveMiss = 0,
    enemyStatDownEffect = false,
    enemyFullyParalyzed = false,
    enemyHitConfuse = false,
    enemyStatused = false,
    enemyWokeUp = false,
    enemySnappedOut = false
}

-- Global Pokemon Data Sync variables
local pokemonData = {
    nickname = "STARMIE",
    species = SPECIES_DATA["Starmie"],
    currentHP = 323, maxHP = 323,
    level = 100,
    type1 = TYPEMAP["Water"], type2 = TYPEMAP["Psychic"],
    moves = {1, 0, 0, 0},
    movesPP = {35, 0, 0, 0},
    attack = 999,
    defense = 999,
    speed = 999,
    special = 999
}

-- Default Pokemon Data
local unknownData = {
    nickname = "UNKNOWN",
    species = 0x1,
    currentHP = 999, maxHP = 999,
    level = 100,
    type1 = 1, type2 = 1,
    moves = {0, 0, 0, 0},
    movesPP = {0, 0, 0, 0},
    attack = 999,
    defense = 999,
    speed = 999,
    special = 999
}

-- Unified Pokemon class that works for both player and enemy
local Pokemon = {}
Pokemon.__index = Pokemon

function Pokemon.new(index, isPlayer, pokemonData)
    local self = setmetatable({}, Pokemon)
    self.index = index
    self.isPlayer = isPlayer
    self.baseAddress = MEMORY.PLAYER_PARTY_BASE + (index * MEMORY.POKEMON_DATA_SIZE)
    self.enemyBaseAddress = MEMORY.ENEMY_PARTY_BASE + (index * MEMORY.POKEMON_DATA_SIZE)
    self.nickAddress = MEMORY.PLAYER_NICKS_BASE + (index * MEMORY.POKEMON_NICK_SIZE)
    self.enemyNickAddress = MEMORY.ENEMY_NICKS_BASE + (index * MEMORY.POKEMON_NICK_SIZE)
    self.nickname = pokemonData.nickname
    self.species = pokemonData.species
    self.currentHP, self.maxHP = pokemonData.currentHP, pokemonData.maxHP
    self.level = pokemonData.level
    self.type1, self.type2 = pokemonData.type1, pokemonData.type2
    self.moves = pokemonData.moves
    self.movesPP = pokemonData.movesPP
    self.attack = pokemonData.attack
    self.defense = pokemonData.defense
    self.speed = pokemonData.speed
    self.special = pokemonData.special
    print(string.format("Created %s Pokemon %d: %s (HP: %d)",
        isPlayer and "Player" or "Enemy",
        index,
        SPECIES_NAMES[self.species] or "Unknown",
        self.currentHP))
    
    self:set(index)
    return self
end

function Pokemon:set(index)
    local memLocation = self.isPlayer and "P1 System Bus" or "P2 System Bus"
    
    memory.writebyte(MEMORY.PLAYER_SPECIES_ARRAY + index, self.species, memLocation)
    memory.writebyte(self.baseAddress + MEMORY.POKEMON_SPECIES_OFFSET, self.species, memLocation)
    memory.write_u16_be(self.baseAddress + MEMORY.CURRENT_HP_OFFSET, self.currentHP, memLocation)
    memory.write_u16_be(self.baseAddress + MEMORY.MAX_HP_OFFSET, self.maxHP, memLocation)
    memory.writebyte(self.baseAddress + MEMORY.ACTUAL_LEVEL_OFFSET, self.level, memLocation)
    memory.writebyte(self.baseAddress + MEMORY.TYPE1_OFFSET, self.type1, memLocation)
    memory.writebyte(self.baseAddress + MEMORY.TYPE2_OFFSET, self.type2, memLocation)
    
    for i = 1, 4 do
        memory.writebyte(self.baseAddress + MEMORY.MOVES_OFFSET + i - 1, self.moves[i], memLocation)
        memory.writebyte(self.baseAddress + MEMORY.MOVES_PP_OFFSET + i - 1, self.movesPP[i] | 0xC0, memLocation)
    end
    
    memory.write_u16_be(self.baseAddress + MEMORY.ATTACK_STAT_OFFSET, self.attack, memLocation)
    memory.write_u16_be(self.baseAddress + MEMORY.DEFENSE_STAT_OFFSET, self.defense, memLocation)
    memory.write_u16_be(self.baseAddress + MEMORY.SPEED_STAT_OFFSET, self.speed, memLocation)
    memory.write_u16_be(self.baseAddress + MEMORY.SPECIAL_STAT_OFFSET, self.special, memLocation)
    
    for i = 1, MEMORY.POKEMON_NICK_SIZE do
        local char = string.sub(self.nickname, i, i)
        local charValue = CHARMAP[char] or 0x50
        memory.writebyte(self.nickAddress + i - 1, charValue, memLocation)
    end
end

function Pokemon:updateEnemyParty(index)
    local memLocation = self.isPlayer and "P2 System Bus" or "P1 System Bus"
    
    memory.writebyte(MEMORY.ENEMY_SPECIES_ARRAY + index, self.species, memLocation)
    memory.writebyte(self.enemyBaseAddress + MEMORY.POKEMON_SPECIES_OFFSET, self.species, memLocation)
    memory.write_u16_be(self.enemyBaseAddress + MEMORY.CURRENT_HP_OFFSET, self.currentHP, memLocation)
    memory.write_u16_be(self.enemyBaseAddress + MEMORY.MAX_HP_OFFSET, self.maxHP, memLocation)
    memory.writebyte(self.enemyBaseAddress + MEMORY.ACTUAL_LEVEL_OFFSET, self.level, memLocation)
    memory.writebyte(self.enemyBaseAddress + MEMORY.TYPE1_OFFSET, self.type1, memLocation)
    memory.writebyte(self.enemyBaseAddress + MEMORY.TYPE2_OFFSET, self.type2, memLocation)
    
    for i = 1, 4 do
        memory.writebyte(self.enemyBaseAddress + MEMORY.MOVES_OFFSET + i - 1, self.moves[i], memLocation)
        memory.writebyte(self.enemyBaseAddress + MEMORY.MOVES_PP_OFFSET + i - 1, self.movesPP[i] | 0xC0, memLocation)
    end
    
    memory.write_u16_be(self.enemyBaseAddress + MEMORY.ATTACK_STAT_OFFSET, self.attack, memLocation)
    memory.write_u16_be(self.enemyBaseAddress + MEMORY.DEFENSE_STAT_OFFSET, self.defense, memLocation)
    memory.write_u16_be(self.enemyBaseAddress + MEMORY.SPEED_STAT_OFFSET, self.speed, memLocation)
    memory.write_u16_be(self.enemyBaseAddress + MEMORY.SPECIAL_STAT_OFFSET, self.special, memLocation)
    
    for i = 1, MEMORY.POKEMON_NICK_SIZE do
        local char = string.sub(self.nickname, i, i)
        local charValue = CHARMAP[char] or 0x50
        memory.writebyte(self.enemyNickAddress + i - 1, charValue, memLocation)
    end
end

function Pokemon:updateMoveList(moves, movesPP)
    local memLocation = self.isPlayer and "P1 System Bus" or "P2 System Bus"
    local enemyMemLocation = self.isPlayer and "P2 System Bus" or "P1 System Bus"
    self.moves = moves
    self.movesPP = movesPP
    for i = 1, 4 do
        memory.writebyte(self.baseAddress + MEMORY.MOVES_OFFSET + i - 1, moves[i], memLocation)
        memory.writebyte(self.baseAddress + MEMORY.MOVES_PP_OFFSET + i - 1, movesPP[i] | 0xC0, memLocation)  -- Sets top 2 bits to 1 for Max PP UP
        memory.writebyte(MEMORY.BATTLE_MON_MOVES + i - 1, moves[i], memLocation)
        memory.writebyte(MEMORY.BATTLE_MON_PP + i - 1, movesPP[i] | 0xC0, memLocation)
        memory.writebyte(self.enemyBaseAddress + MEMORY.MOVES_OFFSET + i - 1, moves[i], enemyMemLocation)
        memory.writebyte(self.enemyBaseAddress + MEMORY.MOVES_PP_OFFSET + i - 1, movesPP[i] | 0xC0, enemyMemLocation)
        memory.writebyte(MEMORY.ENEMY_MON_MOVES + i - 1, moves[i], enemyMemLocation)
        memory.writebyte(MEMORY.ENEMY_MON_PP + i - 1, movesPP[i] | 0xC0, enemyMemLocation)
    end
end

function Pokemon:getName()
    return SPECIES_NAMES[self.species] or "Unknown"
end

function Pokemon:isAlive()
    return self.currentHP > 0
end

-- Input handling functions
local Input = {}

-- Presses a button for a specified number of frames
function Input.pressButton(button, holdFrames)
    local frames = holdFrames or CONFIG.BUTTON_HOLD_FRAMES
    joypad.set(button, 2)
    for _ = 1, frames do emu.frameadvance() end
    joypad.set({}, 2)
    emu.frameadvance()
end

function Input.moveSequence(offset)
    -- Navigate to the move menu and select a move
    Input.pressButton({Up = true})
    Input.pressButton({Left = true})
    Input.pressButton({A = true})
    local direction = offset < 0 and {Up = true} or {Down = true}
    for _ = 1, math.abs(offset) do Input.pressButton(direction) end
    Input.pressButton({A = true})
end

function Input.switchSequence(offset)
    -- Navigate to the Pokemon menu and select a Pokemon
    Input.pressButton({Up = true}, CONFIG.SWITCH_HOLD_FRAMES)
    Input.pressButton({Right = true}, CONFIG.SWITCH_HOLD_FRAMES)
    Input.pressButton({A = true}, CONFIG.SWITCH_HOLD_FRAMES)
    local direction = offset < 0 and {Up = true} or {Down = true}
    for _ = 1, math.abs(offset) do Input.pressButton(direction, CONFIG.SWITCH_HOLD_FRAMES) end
    Input.pressButton({A = true}, CONFIG.SWITCH_HOLD_FRAMES)
    Input.pressButton({A = true}, CONFIG.SWITCH_HOLD_FRAMES)
end

function Input.faintedSequence(offset)
    -- Wait for animation and then select a replacement Pokemon
    Input.pressButton({Left = true}, CONFIG.ANIMATION_WAIT_FRAMES)
    local direction = offset < 0 and {Up = true} or {Down = true}
    for _ = 1, math.abs(offset) do Input.pressButton(direction, CONFIG.SWITCH_HOLD_FRAMES) end
    Input.pressButton({A = true}, CONFIG.SWITCH_HOLD_FRAMES)
    Input.pressButton({A = true}, CONFIG.SWITCH_HOLD_FRAMES)
end

-- UI Display functions
local Display = {}

-- Display information about the currently selected move
function Display.selectedMove()
    local selectedMoveIndex = memory.readbyte(MEMORY.SELECTED_INDEX)
    if selectedMoveIndex <= 4 then
        local moveID = memory.readbyte(MEMORY.SELECTED_MOVE_ID)
        local pp = memory.readbyte(MEMORY.MOVE_PP_BASE + selectedMoveIndex - 1) & 0x3F
        gui.text(10, 10, "Selected Move: " .. (MOVE_NAMES[moveID] or "Unknown") .. " (PP: " .. pp .. ")")
        if memory.readbyte(MEMORY.BATTLE_MENU_STATE) == CONFIG.BATTLE_MENU_SELECT_VALUE and state.backToMainMenu then
            state.backToMainMenu = false
            return true
        end
    end
    return false
end

-- Display information about the currently selected Pokemon
function Display.selectedPokemon()
    local xpos, ypos = memory.readbyte(MEMORY.CURSOR_X_POS), memory.readbyte(MEMORY.CURSOR_Y_POS)
    local selectedPokeIndex = ypos == 12 and state.lastSelectedPokeIndex or memory.readbyte(MEMORY.SELECTED_INDEX)
    if ypos ~= 12 then state.lastSelectedPokeIndex = selectedPokeIndex end
    if selectedPokeIndex < 6 then
        local species = memory.readbyte(MEMORY.PLAYER_PARTY_BASE + selectedPokeIndex)
        gui.text(10, 30, "Selected Pokémon: " .. (SPECIES_NAMES[species] or "Unknown"))
    end
    if ypos == 12 and memory.readbyte(MEMORY.BATTLE_MENU_STATE) == CONFIG.BATTLE_MENU_SELECT_VALUE and state.backToMainMenu then
        state.backToMainMenu = false
        return true
    end
    return false
end

-- Display battle menu options and handle selections
function Display.options()
    local xpos, ypos = memory.readbyte(MEMORY.CURSOR_X_POS), memory.readbyte(MEMORY.CURSOR_Y_POS)
    if ypos == 14 then state.backToMainMenu = true end
    if xpos == 5 and ypos == 12 then return Display.selectedMove()
    elseif ypos == 1 or ypos == 12 then return Display.selectedPokemon() end
    return false
end

-- AI Battle Logic
local BattleAI = {}

-- Select a random move or switch Pokemon
function BattleAI.selectRandomAction(party)
    math.randomseed(os.time() + emu.framecount())
    local rand = math.random(100)
    local move_select, party_select = rand % 4, rand % 6
    local curr_pokemon = memory.readbyte(MEMORY.CURRENT_ENEMY_POKEMON_SPECIES)
    local index = 0
    if rand % 2 == 0 then
        for i = 0, 5 do
            party[i]:update()
            if party[i].species == curr_pokemon then index = i end
        end
        for _ = 0, 5 do
            if party[party_select]:isAlive() and party[party_select].species ~= curr_pokemon then
                state.currentEnemyMoveIndex = 0
                Input.switchSequence(party_select - index)
                break
            end
            party_select = (party_select + 1) % 6
        end
    else
        Input.moveSequence(move_select - state.currentEnemyMoveIndex)
        state.currentEnemyMoveIndex = move_select
    end
end

-- Handle selecting a replacement when a Pokemon faints
function BattleAI.selectReplacement(party)
    math.randomseed(os.time() + emu.framecount())
    local rand = math.random(100)
    local curr_pokemon = memory.readbyte(MEMORY.CURRENT_ENEMY_POKEMON_SPECIES)
    local party_select, index = rand % 6, 0
    state.currentEnemyMoveIndex = 0
    for i = 0, 5 do
        party[i]:update()
        if party[i].species == curr_pokemon then index = i end
    end
    for _ = 0, 5 do
        if party[party_select]:isAlive() and party[party_select].species ~= curr_pokemon then
            Input.faintedSequence(party_select - index)
            break
        end
        party_select = (party_select + 1) % 6
    end
end



function main()
    -- PLAYER MOVES FIRST
    -- Random selection if speed is equal (invert) : MASTER
    event.on_bus_exec(function()
        emu.setregister("P1 F", RNG.playerFirst and MEMORY.PLAYER_TURN_FLAG or MEMORY.ENEMY_TURN_FLAG)
    end, MEMORY.MASTER_SPEED_COMPARE, 0, "P1 ROM")

    -- Random selection if speed is equal : SLAVE
    event.on_bus_exec(function()
        emu.setregister("P2 F", RNG.playerFirst and MEMORY.PLAYER_TURN_FLAG or MEMORY.ENEMY_TURN_FLAG)
    end, MEMORY.SLAVE_SPEED_COMPARE, 0, "P2 ROM")

    -- Player Damage Randomization
    -- event.on_bus_exec(function()
    --     emu.setregister("P1 A", memory.readbyte(MEMORY.WHOSE_TURN, "P1 System Bus") == 0 and RNG.playerDamage or RNG.enemyDamage)
    -- end, MEMORY.DAMAGE_CHECK, 0, "P1 ROM")

    -- Enemy Damage Randomization
    -- event.on_bus_exec(function()
    --     emu.setregister("P2 A", memory.readbyte(MEMORY.WHOSE_TURN, "P2 System Bus") == 0 and RNG.enemyDamage or RNG.playerDamage)
    -- end, MEMORY.DAMAGE_CHECK, 0, "P2 ROM")

    -- Player Damage Calculation
    event.on_bus_read(function()
        memory.write_u16_be(MEMORY.DAMAGE, memory.readbyte(MEMORY.WHOSE_TURN, "P1 System Bus") == 0 and RNG.playerDamage or RNG.enemyDamage, "P1 System Bus")
    end, MEMORY.DAMAGE, 0, "P1 System Bus")

    -- Enemy Damage Calculation
    event.on_bus_read(function()
        memory.write_u16_be(MEMORY.DAMAGE, memory.readbyte(MEMORY.WHOSE_TURN, "P2 System Bus") == 0 and RNG.enemyDamage or RNG.playerDamage, "P2 System Bus")
    end, MEMORY.DAMAGE, 0, "P2 System Bus")

    -- Player Sleep Turn Counter Set
    event.on_bus_exec(function() emu.setregister("P1 A", 7) end, MEMORY.SLEEP_SET_COUNTER, 0, "P1 ROM")     -- Always set to max turns of sleep
    -- Enemy Sleep Turn Counter Set
    event.on_bus_exec(function() emu.setregister("P2 A", 7) end, MEMORY.SLEEP_SET_COUNTER, 0, "P2 ROM")

    -- Player Wakes Up
    event.on_bus_read(function()
        if RNG.playerWokeUp and memory.readbyte(MEMORY.PLAYER_SLEEP_COUNTER, "P1 System Bus") > 1 then
            memory.writebyte(MEMORY.PLAYER_SLEEP_COUNTER, 1, "P1 System Bus") 
        end
    end, MEMORY.PLAYER_SLEEP_COUNTER, 0, "P1 System Bus")
    
    event.on_bus_read(function()
        if RNG.playerWokeUp and memory.readbyte(MEMORY.ENEMY_SLEEP_COUNTER, "P2 System Bus") > 1 then 
            RNG.playerWokeUp = false        -- Only set on P2 trigger after P1 to avoid desync
            memory.writebyte(MEMORY.ENEMY_SLEEP_COUNTER, 1, "P2 System Bus")
        end
    end, MEMORY.ENEMY_SLEEP_COUNTER, 0, "P2 System Bus")

    -- Enemy Wakes Up
    event.on_bus_read(function()
        if RNG.enemyWokeUp and memory.readbyte(MEMORY.ENEMY_SLEEP_COUNTER, "P1 System Bus") > 1 then
            memory.writebyte(MEMORY.ENEMY_SLEEP_COUNTER, 1, "P1 System Bus")
        end
    end, MEMORY.ENEMY_SLEEP_COUNTER, 0, "P1 System Bus")

    event.on_bus_read(function()
        if RNG.enemyWokeUp and memory.readbyte(MEMORY.PLAYER_SLEEP_COUNTER, "P2 System Bus") > 1 then 
            RNG.enemyWokeUp = false
            memory.writebyte(MEMORY.PLAYER_SLEEP_COUNTER, 1, "P2 System Bus")
        end
    end, MEMORY.PLAYER_SLEEP_COUNTER, 0, "P2 System Bus")

    -- Player Confuse Turn Counter Set
    event.on_bus_exec(function() emu.setregister("P1 A", 5) end, MEMORY.CONFUSE_SET_COUNTER, 0, "P1 ROM")    -- Always set to max turns of confusion
    -- Enemy Confuse Turn Counter Set
    event.on_bus_exec(function() emu.setregister("P2 A", 5) end, MEMORY.CONFUSE_SET_COUNTER, 0, "P2 ROM")

    -- Player snaps out of Confusion
    event.on_bus_read(function()
        if RNG.playerSnappedOut and memory.readbyte(MEMORY.PLAYER_CONFUSE_COUNTER, "P1 System Bus") > 1 then
            memory.writebyte(MEMORY.PLAYER_CONFUSE_COUNTER, 1, "P1 System Bus")
        end
    end, MEMORY.PLAYER_CONFUSE_COUNTER, 0, "P1 System Bus")
    
    event.on_bus_read(function()
        if RNG.playerSnappedOut and memory.readbyte(MEMORY.ENEMY_CONFUSE_COUNTER, "P2 System Bus") > 1 then 
            memory.writebyte(MEMORY.ENEMY_CONFUSE_COUNTER, 1, "P2 System Bus")
        end
    end, MEMORY.ENEMY_CONFUSE_COUNTER, 0, "P2 System Bus")

    -- Enemy snaps out of Confusion
    event.on_bus_read(function()
        if RNG.enemySnappedOut and memory.readbyte(MEMORY.ENEMY_CONFUSE_COUNTER, "P1 System Bus") > 1 then
            memory.writebyte(MEMORY.ENEMY_CONFUSE_COUNTER, 1, "P1 System Bus")
        end
    end, MEMORY.ENEMY_CONFUSE_COUNTER, 0, "P1 System Bus")

    event.on_bus_read(function()
        if RNG.enemySnappedOut and memory.readbyte(MEMORY.PLAYER_CONFUSE_COUNTER, "P2 System Bus") > 1 then 
            memory.writebyte(MEMORY.PLAYER_CONFUSE_COUNTER, 1, "P2 System Bus")
        end
    end, MEMORY.PLAYER_CONFUSE_COUNTER, 0, "P2 System Bus")

    -- Player Critical Check
    event.on_bus_write(function()
        memory.writebyte(MEMORY.CRIT_FLAG, memory.readbyte(MEMORY.WHOSE_TURN, "P1 System Bus") == 0 and RNG.playerCrit or RNG.enemyCrit, "P1 System Bus")
    end, MEMORY.CRIT_FLAG, 0, "P1 System Bus")

    -- Enemy Critical Check
    event.on_bus_write(function()
        memory.writebyte(MEMORY.CRIT_FLAG, memory.readbyte(MEMORY.WHOSE_TURN, "P2 System Bus") == 0 and RNG.enemyCrit or RNG.playerCrit, "P2 System Bus")
    end, MEMORY.CRIT_FLAG, 0, "P2 System Bus")

    -- Player Move Miss
    event.on_bus_write(function()
        memory.writebyte(MEMORY.MOVE_MISS, memory.readbyte(MEMORY.WHOSE_TURN, "P1 System Bus") == 0 and RNG.playerMoveMiss or RNG.enemyMoveMiss, "P1 System Bus")
    end, MEMORY.MOVE_MISS, 0, "P1 System Bus")

    -- Enemy Move Miss
    event.on_bus_write(function()
        memory.writebyte(MEMORY.MOVE_MISS, memory.readbyte(MEMORY.WHOSE_TURN, "P2 System Bus") == 0 and RNG.enemyMoveMiss or RNG.playerMoveMiss, "P2 System Bus")
    end, MEMORY.MOVE_MISS, 0, "P2 System Bus")

    -- Player Move Stat Down Effect
    event.on_bus_exec(function()
        emu.setregister("P1 A", memory.readbyte(MEMORY.WHOSE_TURN, "P1 System Bus") == 0 and
            (RNG.playerStatDownEffect and MEMORY.STAT_DOWN_FLAG or MEMORY.STAT_NOT_DOWN_FLAG) or
            (RNG.enemyStatDownEffect and MEMORY.STAT_DOWN_FLAG or MEMORY.STAT_NOT_DOWN_FLAG))
    end, MEMORY.STAT_DOWN_EFFECT, 0, "P1 ROM")

    -- Enemy Move Stat Down Effect
    event.on_bus_exec(function()
        emu.setregister("P2 A", memory.readbyte(MEMORY.WHOSE_TURN, "P2 System Bus") == 0 and
            (RNG.enemyStatDownEffect and MEMORY.STAT_DOWN_FLAG or MEMORY.STAT_NOT_DOWN_FLAG) or
            (RNG.playerStatDownEffect and MEMORY.STAT_DOWN_FLAG or MEMORY.STAT_NOT_DOWN_FLAG))
    end, MEMORY.STAT_DOWN_EFFECT, 0, "P2 ROM")

    -- Player Flinch Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.flinched and MEMORY.FLINCH_FLAG or MEMORY.FLINCH_NOT_FLAG)
    end, MEMORY.FLINCH_CHECK, 0, "P1 ROM")

    -- Enemy Flinch Check
    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.flinched and MEMORY.FLINCH_FLAG or MEMORY.FLINCH_NOT_FLAG)
    end, MEMORY.FLINCH_CHECK, 0, "P2 ROM")

    -- Player Poison Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", memory.readbyte(MEMORY.WHOSE_TURN, "P1 System Bus") == 0 and
            (RNG.playerStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG) or
            (RNG.enemyStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG))
    end, MEMORY.POISON_CHECK, 0, "P1 ROM")

    -- Enemy Poison Check
    event.on_bus_exec(function()
        emu.setregister("P2 A", memory.readbyte(MEMORY.WHOSE_TURN, "P2 System Bus") == 0 and
            (RNG.enemyStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG) or
            (RNG.playerStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG))
    end, MEMORY.POISON_CHECK, 0, "P2 ROM")

    -- Player Statused Check (other than poison)
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.playerStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG)
    end, MEMORY.PLAYER_STATUSED, 0, "P1 ROM")

    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.playerStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG)
    end, MEMORY.ENEMY_STATUSED, 0, "P2 ROM")

    -- Enemy Statused Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.enemyStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG)
    end, MEMORY.ENEMY_STATUSED, 0, "P1 ROM")

    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.enemyStatused and MEMORY.STATUSED_FLAG or MEMORY.STATUSED_NOT_FLAG)
    end, MEMORY.PLAYER_STATUSED, 0, "P2 ROM")

    -- Player Full Paralysis Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.playerFullyParalyzed and MEMORY.PARALYZED_FLAG or MEMORY.NOT_PARALYZED_FLAG)
    end, MEMORY.PLAYER_PARALYSIS_CHECK, 0, "P1 ROM")

    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.playerFullyParalyzed and MEMORY.PARALYZED_FLAG or MEMORY.NOT_PARALYZED_FLAG)
    end, MEMORY.ENEMY_PARALYSIS_CHECK, 0, "P2 ROM")

    -- Enemy Full Paralysis Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.enemyFullyParalyzed and MEMORY.PARALYZED_FLAG or MEMORY.NOT_PARALYZED_FLAG)
    end, MEMORY.ENEMY_PARALYSIS_CHECK, 0, "P1 ROM")

    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.enemyFullyParalyzed and MEMORY.PARALYZED_FLAG or MEMORY.NOT_PARALYZED_FLAG)
    end, MEMORY.PLAYER_PARALYSIS_CHECK, 0, "P2 ROM")

    -- Player Confuse Hit Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.playerHitConfuse and MEMORY.CONFUSE_HIT_FLAG or MEMORY.CONFUSE_NO_HIT_FLAG)
    end, MEMORY.PLAYER_CONFUSE_CHECK, 0, "P1 ROM")

    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.playerHitConfuse and MEMORY.CONFUSE_HIT_FLAG or MEMORY.CONFUSE_NO_HIT_FLAG)
    end, MEMORY.ENEMY_CONFUSE_CHECK, 0, "P2 ROM")

    -- Enemy Confuse Hit Check
    event.on_bus_exec(function()
        emu.setregister("P1 A", RNG.enemyHitConfuse and MEMORY.CONFUSE_HIT_FLAG or MEMORY.CONFUSE_NO_HIT_FLAG)
    end, MEMORY.ENEMY_CONFUSE_CHECK, 0, "P1 ROM")

    event.on_bus_exec(function()
        emu.setregister("P2 A", RNG.enemyHitConfuse and MEMORY.CONFUSE_HIT_FLAG or MEMORY.CONFUSE_NO_HIT_FLAG)
    end, MEMORY.PLAYER_CONFUSE_CHECK, 0, "P2 ROM")

    -- Initialize player and enemy parties
    local player_party, enemy_party = {}, {}
    enemy_party[0] = Pokemon.new(0, false, pokemonData)
    for i = 1, 5 do
    --     player_party[i] = Pokemon.new(i, true, pokemonData)
        enemy_party[i] = Pokemon.new(i, false, unknownData)
    end

    local frameCount = 0
    -- Main game loop
    while true do
        if joypad.get(1)["Start"] then
            RNG = {
                playerFirst = true,
                flinched = false,
                playerDamage = 100,
                playerCrit = 0,
                playerMoveMiss = 0,
                playerStatDownEffect = false,
                playerFullyParalyzed = false,
                playerHitConfuse = false,
                playerStatused = false,
                playerWokeUp = false,
                playerSnappedOut = false,
                enemyDamage = 100,
                enemyCrit = 0,
                enemyMoveMiss = 0,
                enemyStatDownEffect = false,
                enemyFullyParalyzed = false,
                enemyHitConfuse = false,
                enemyStatused = false,
                enemyWokeUp = false,
                enemySnappedOut = false
            }

            pokemonData = {
                nickname = "STARMIE",
                species = SPECIES_DATA["Starmie"],
                currentHP = 323, maxHP = 323,
                level = 100,
                type1 = TYPEMAP["Water"], type2 = TYPEMAP["Psychic"],
                moves = {MOVE_DATA["Psychic"].id, 0, 0, 0},
                movesPP = {MOVE_DATA["Psychic"].pp, 0, 0, 0},
                attack = 999,
                defense = 999,
                speed = 999,
                special = 999
            }
            
            for i = 0, 5 do
                if enemy_party[i].species == pokemonData.species then
                    if enemy_party[i].moves ~= pokemonData.moves then
                        enemy_party[i]:updateMoveList(pokemonData.moves, pokemonData.movesPP)
                    end
                    break
                elseif enemy_party[i].nickname == "UNKNOWN" then
                    enemy_party[i] = Pokemon.new(i, false, pokemonData)
                    enemy_party[i]:updateEnemyParty(i)
                    break
                end
            end
            
            client.pause()
        end
        
        frameCount = frameCount + 1
        if frameCount >= CONFIG.FRAME_UPDATE_INTERVAL then
            frameCount = 0

        end
        -- If player selects an option, have the enemy randomly select an option
        if Display.options() then
            -- BattleAI.selectRandomAction(enemy_party)
        end
        -- Check if active Pokemon fainted (HP = 0) and select replacement if needed
        -- if memory.read_u16_be(MEMORY.CURRENT_ENEMY_POKEMON_HP) == 0 and not state.waitingForMenuReturn then
        --     state.waitingForMenuReturn = true
        --     BattleAI.selectReplacement(enemy_party)
        -- end
        -- Reset waiting state when back at main menu
        if state.backToMainMenu and state.waitingForMenuReturn then
            state.waitingForMenuReturn = false
        end
        emu.frameadvance()
    end
end

-- Start the script
main()
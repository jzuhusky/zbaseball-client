PLAYOFF_GAME_ROUNDS = {
    "WS",
    "ALCS",
    "NLCS",
    "ALD1",
    "ALD2",
    "NLD1",
    "NLD2",
    "ALWC",
    "NLWC",
}

REGULAR_GAME = "REG"
ASG = "ASG"

GAME_TYPES = PLAYOFF_GAME_ROUNDS | {REGULAR_GAME} | {ASG}

BATTING_STATS = (
    "G",
    "PA",
    "AB",
    "H",
    "2B",
    "3B",
    "HR",
    "RBI",
    "R",
    "BB",
    "IBB",
    "SO",
    "ROE",
    "GIDP",
    "SH",
    "SF",
    "SB",
    "CS",
    "GB",
    "LD",
    "PF",
    "FB",
)

PITCHING_STATS = (
    "IP",
    "G",
    "BF",
    "AB",
    "H",
    "2B",
    "3B",
    "HR",
    "BB",
    "IBB",
    "SO",
    "ROE",
    "GIDP",
    "SH",
    "SF",
    "HBP",
    "ER",
    "R",
    "WP",
)

AGGREGATE_OPTIONS = (
    "C",  # by career
    "D",  # by day
    "W",  # by week, returned as date for monday which begins that "week"
    "M",  # by month,
    "MY",  # by month/year
    "Y",  # by year
    "G",  # by game-id
    "DOW",  # by day of the week
    "INN",  # by inning
    "COP",  # by count on play
    "PARK_NAME",
    "PARK_ID",
)

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

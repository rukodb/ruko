from enum import IntEnum


class Command(IntEnum):
    GET = 1
    SET = 2
    DELETE = 3
    DECLARE = 4
    LPUT = 5
    CREATE_MAPPING = 6
    DELETE_MAPPING = 7
    GET_MAPPINGS = 8

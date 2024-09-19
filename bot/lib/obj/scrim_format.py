from enum import Enum

class ScrimFormat(Enum):
    SOLO = 1
    DUO = 2
    TRIO = 3
    CUSTOM = 4

    @staticmethod
    def to_str(format: 'ScrimFormat') -> str:
        return {
            ScrimFormat.SOLO: "Solo",
            ScrimFormat.DUO: "Duo",
            ScrimFormat.TRIO: "Trio",
            ScrimFormat.CUSTOM: "Custom"
        }[format]
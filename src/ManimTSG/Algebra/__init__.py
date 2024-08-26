from __future__ import annotations

from ManimTSG import *

class Set:
    def __init__(self, letter) -> None:
        self.letter = letter

    @tex_string_group
    def tsg_letter(self):
        return self.letter

class Map:
    def __init__(self, letter, from_: Set, to: Set) -> None:
        self.letter = letter
        self.from_  = from_
        self.to     = to

    @tex_string_group
    def tsg_letter(self):
        return self.letter

    @tex_string_group
    def tsg_from_to(self):
        return (
            self.tsg_letter(),
            ":", self.from_.tsg_letter(),
            r"\to", self.to.tsg_letter()
        )

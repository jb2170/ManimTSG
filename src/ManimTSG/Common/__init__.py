from ManimTSG import *

def interspersed(iterand, sep):
    it = iter(iterand)
    try:
        n = next(it)
    except StopIteration:
        return

    yield n

    for n in it:
        yield sep
        yield n

def subscript(*elts: str | TexStringGroup) -> TexStringGroup:
    return TexStringGroup("_{", *elts, "}", labels = ["subscript"])

def superscript(*elts: str | TexStringGroup) -> TexStringGroup:
    return TexStringGroup("^{", *elts, "}", labels = ["superscript"])

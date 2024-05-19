def fqln(instance: type, label_name: str) -> str:
    """Generate a Fully Qualified Label Name"""
    return f"{instance.__class__.__name__}.{label_name}"

def iter_interspersed(iterand, sep):
    """Yield values by iterating through `iterand`, interspersing yields of values with yields of `sep`"""

    it = iter(iterand)
    try:
        n = next(it)
    except StopIteration:
        return

    yield n

    for n in it:
        yield sep
        yield n

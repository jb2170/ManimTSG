from __future__ import annotations

from ManimTSG import *
from ManimTSG.Common import interspersed

class Probability:
    def __init__(self, of: Event) -> None:
        self.of = of

    @tex_string_group
    def tsg_p(self):
        return r"\mathbb{P}"

    @tex_string_group
    def tsg_full(self):
        return (self.tsg_p(), "(", self.of.tsg_full(), ")")

class Event:
    def __init__(self, letter: str | TexStringGroup) -> None:
        self.letter = letter

    @tex_string_group
    def tsg_full(self):
        return self.letter

    def __and__(self, rhs: Event) -> Event:
        return Event(TexStringGroup(self.letter, r"\cap", rhs.letter))

    def __or__(self, rhs: Event) -> Event:
        return Event(TexStringGroup(self.letter, r"\cup", rhs.letter))

    def given(self, rhs: Event) -> Event:
        return Event(TexStringGroup(self.letter, "|", rhs.letter))

class RandomVariable:
    def __init__(
        self,
        letter:               str = r"X",
        space:                str = r"\Omega", # from
        to:                   str = r"\mathbb{R}",
        default_event_letter: str = r"x",
    ) -> None:
        self.letter = letter
        self.space = space
        self.to = to
        self.default_event_letter = default_event_letter

    @tex_string_group
    def tsg_letter(self):
        return self.letter

    @tex_string_group
    def tsg_from_to(self):
        return (self.letter, ":", self.space, r"\to", self.to)

class RandomVariableEvent:
    def __init__(self, rv: RandomVariable, value: str | None = None) -> None:
        self.rv = rv
        if value is None:
            value = rv.default_event_letter
        self.value = value

    def probability(self) -> RandomVariableProbability:
        return RandomVariableProbability([self])

    @tex_string_group
    def tsg_value(self):
        return self.value

    @tex_string_group
    def tsg_full(self):
        return (self.rv.tsg_letter(), "=", self.tsg_value())

class RandomVariableProbability:
    def __init__(
        self,
        events:       list[RandomVariableEvent],
        given_events: list[RandomVariableEvent] | None = None,
    ) -> None:
        self.events = events
        self.given_events = given_events

    @tex_string_group
    def tsg_p(self):
        return r"\mathbb{P}"

    @tex_string_group
    def tsg_short(self):
        # p_i
        assert len(self.events) == 1
        assert self.given_events is None

        event = self.events[0]

        return ("p", "_{", event.tsg_value(), "}")

    @tex_string_group
    def tsg_full(self):
        ret = tuple()

        ret += (self.tsg_p(), "(")

        ret += tuple(interspersed(
            (event.tsg_full() for event in self.events),
            ","
        ))

        if self.given_events is not None:
            ret += tuple("|")
            ret += tuple(interspersed(
                (given_event.tsg_full() for given_event in self.given_events),
                ","
            ))

        ret += tuple(")")

        return ret

class RandomVariableEntropy:
    def __init__(self, rv: RandomVariable) -> None:
        self.rv = rv

    @tex_string_group
    def tsg_lhs(self):
        return ("H", "(", self.rv.tsg_letter(), ")")

    @tex_string_group
    def tsg_rhs(self):
        event = RandomVariableEvent(self.rv)
        event_probability = event.probability()

        return (
            "-", r"\sum", "_{", self.rv.default_event_letter, "}",
            event_probability.tsg_full(),
            r"\log", "_2",
            "(",
            event_probability.tsg_full(),
            ")"
        )

    @tex_string_group
    def tsg_rhs_short(self):
        event = RandomVariableEvent(self.rv)
        event_probability = event.probability()

        return (
            "-", r"\sum", "_{", self.rv.default_event_letter, "}",
            event_probability.tsg_short(),
            r"\log", "_2",
            event_probability.tsg_short(),
        )

    @tex_string_group
    def tsg_full(self):
        return (self.tsg_lhs(), "=", self.tsg_rhs_short())

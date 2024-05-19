from __future__ import annotations
from typing import Callable
import copy

from manim import MathTex

def tex_string_group(func) -> Callable[..., TexStringGroup]: # is this typing correct?
    """Decorator"""

    class_name, func_name = func.__qualname__.split(".")

    func_prefix_must_be = "tsg_"

    if not func_name.startswith(func_prefix_must_be):
        raise AttributeError("Names of functions decorated with tex_string_group should begin with tsg_")

    # For finding the relevant subgroup when calling TexStringGroup.find_by_label
    group_label = f"{class_name}.{func_name.removeprefix(func_prefix_must_be)}"

    def helper(instance, *args, **kwargs):
        elts = func(instance, *args, **kwargs)

        if isinstance(elts, (str, TexStringGroup)):
            elts = (elts,)
        elif isinstance(elts, (tuple, list)):
            pass
        else:
            raise ValueError

        grp = TexStringGroup(*elts, labels = [group_label])

        return grp

    return helper

class TexStringGroup:
    def __init__(
        self,
        *elts: TexStringGroup | str,
        labels: list[str] | None = None
    ) -> None:
        if labels is None:
            labels = []

        self.elts = elts
        self.labels = labels

        self._slice_self: slice                                    = None
        self._str_to_indices:     dict[str, list[int]]             = None
        self._subgroups_by_label: dict[str, list[TexStringGroup]] = None

        # XXX unnecessary unless top level group, TODO improve performance?
        self._generate_label_slices()

    def __str__(self) -> str:
        ret = f"{self.__class__.__name__}({self.labels})"

        return ret

    def dump(self) -> None:
        self._dump_elt(self, [])

    def _dump_elt(self, elt: str | TexStringGroup, finals: list[bool]) -> None:
        print(
            "".join(
                ["    " if final else "│   " for final in finals[:-1]] +
                ["└───" if final else "├───" for final in finals[-1:]]
            ),
            elt,
            sep = ""
        )

        if not isinstance(elt, TexStringGroup):
            return

        for sub_elts, next_finals in (
            (elt.elts[:-1], finals + [False]),
            (elt.elts[-1:], finals + [True])
        ):
            for sub_elt in sub_elts:
                self._dump_elt(sub_elt, next_finals)

    @property
    def indices_slice(self) -> slice:
        return self._slice_self

    def flatten(self) -> list[str]:
        ret = []

        for elt in self.elts:
            if isinstance(elt, str):
                ret.append(elt)
            else:
                ret.extend(elt.flatten())

        return ret

    def copy(self) -> TexStringGroup:
        return copy.deepcopy(self)

    def mathtex(self) -> MathTex:
        return MathTex(*self.flatten())

    def _generate_label_slices(self, idx_so_far: int = 0) -> None:
        self._slice_self = None
        self._str_to_indices = {}
        self._subgroups_by_label = {}

        idx_start = idx_so_far

        for elt in self.elts:
            if isinstance(elt, str):
                self._str_to_indices.setdefault(elt, [])
                self._str_to_indices[elt].append(idx_so_far)
                idx_so_far += 1
            else:
                for label in elt.labels:
                    self._subgroups_by_label.setdefault(label, [])
                    self._subgroups_by_label[label].append(elt)

                elt._generate_label_slices(idx_so_far)

                idx_so_far = elt._slice_self.stop

        self._slice_self = slice(idx_start, idx_so_far)

    def find_by_label(
        self,
        *labels: str,
        return_slices: bool = True,
        depth_range: range = range(0, 100),
    ) -> list[TexStringGroup] | list[slice]:
        """Return a list of subgroups that have any label from `labels`.
        Optionally just return a list of `slice`s indexing where these subgroups occupy (True by default)"""
        comps = []
        for label in labels:
            if "." in label:
                comp = self.comp_eq
            else:
                comp = self.comp_in # not the best...
            comps.append(comp)

        ret = self._find_by_label(
            *labels,
            depth_range = depth_range,
            current_depth = 0,
            comps = comps
        )

        if return_slices:
            ret = [group._slice_self for group in ret]

        return ret

    def comp_eq(self, s1: str, s2: str) -> bool:
        return s1 == s2

    def comp_in(self, s1: str, s2: str) -> bool:
        return s1 in s2

    def _find_by_label(
        self,
        *labels: str,
        depth_range: range,
        current_depth: int,
        comps,
    ) -> list[TexStringGroup]:
        ret = []

        if depth_range.stop is not None and not current_depth < depth_range.stop:
            pass

        elif not current_depth < depth_range.start and any(
            comp(label, label_)
            for label_ in self.labels
            for label, comp in zip(labels, comps)
        ):
            ret.append(self)

        else:
            for elt in self.elts:
                if isinstance(elt, str):
                    continue

                ret.extend(elt._find_by_label(
                    *labels,
                    depth_range = depth_range,
                    current_depth = current_depth + 1,
                    comps = comps,
                ))

        return ret

    def find_by_str(
        self,
        *ss: str,
        depth_range: range = range(0, 100),
    ) -> list[int]:
        """Return a list of the indices of where strings in `ss` occur in the group"""
        return self._find_by_str(
            *ss,
            depth_range = depth_range,
            current_depth = 0
        )

    def _find_by_str(
        self,
        *ss: str,
        depth_range: range,
        current_depth: int
    ):
        ret = []

        if depth_range.stop is not None and not current_depth < depth_range.stop:
            return ret

        if not current_depth < depth_range.start:
            for elt, elt_indices in self._str_to_indices.items():
                # kinda defeats the purpose of cacheing this if we're just going to loop anyway
                for s in ss:
                    if self.comp_eq(elt.lower(), s.lower()):
                        ret.extend(elt_indices)

        for subgroup in (elt for elt in self.elts if isinstance(elt, TexStringGroup)):
            ret.extend(subgroup._find_by_str(
                *ss,
                depth_range = depth_range,
                current_depth = current_depth + 1
            ))

        return ret

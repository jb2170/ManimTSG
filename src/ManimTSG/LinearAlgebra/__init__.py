from __future__ import annotations

from ManimTSG import *

def subscript(*elts: str | TexStringGroup) -> TexStringGroup:
    return TexStringGroup("_{", *elts, "}", labels = ["subscript"])

def superscript(*elts: str | TexStringGroup) -> TexStringGroup:
    return TexStringGroup("^{", *elts, "}", labels = ["superscript"])

class VectorSpace:
    def __init__(
        self,
        letter: str = "V",
        dimension: int | str = "n",
        basis: Basis | None = None
    ) -> None:
        self.letter = letter
        self.dimension = dimension
        self._basis = basis

        if not self.is_variadic and self.dimension < 1:
            raise ValueError("dimension 0 not yet handled")

    @property
    def is_variadic(self) -> bool:
        """
        Dimension is a letter n instead of a fixed number like 3
        """
        return not isinstance(self.dimension, int)

    @property
    def basis(self) -> Basis:
        if self._basis is None:
            raise AttributeError("Basis not set")
        return self._basis

    @basis.setter
    def basis(self, value) -> None:
        self._basis = value

    @tex_string_group
    def tsg_letter(self):
        return self.letter

class Vector:
    def __init__(
        self,
        *letters: str,
        vspace: VectorSpace,
        with_arrow: bool = True
    ) -> None:
        self.letters = letters
        self.vspace = vspace
        self.with_arrow = with_arrow

    @tex_string_group
    def tsg_letters(self):
        ret = self.letters

        if self.with_arrow:
            ret = (
                TexStringGroup(r"\vec{", labels = [fqln(self, "arrow")]),
                *ret,
                "}",
            )

        return ret

    @tex_string_group
    def tsg_repr(self):
        return ("[", self.tsg_letters(), "]", subscript(self.vspace.basis.tsg_letter()))

class EquationLetter:
    def __init__(
        self,
        letter: str,
        n_subscript_indices: int | str,
        *,
        subscript_letter_start: str = "i",
        textify_letter: bool = True
    ) -> None:
        if textify_letter:
            letter = fr"\text{{{letter}}}"

        self.letter = letter
        self.n_subscript_indices = n_subscript_indices
        self.subscript_letter_start = subscript_letter_start

    @property
    def is_variadic(self) -> bool:
        """
        Number of indices is a letter n instead of a fixed number like 3
        """
        return not isinstance(self.n_subscript_indices, int)

    @tex_string_group
    def tsg_letter(self):
        return self.letter

    @tex_string_group
    def tsg_full(self):
        if self.is_variadic: # TODO more logic for short vs long
            return self.tsg_variadic_full()
        else:
            return self.tsg_indexed_full()

    @tex_string_group
    def tsg_variadic_full(self):
        return self.tsg_variadic_concise()

    @tex_string_group
    def tsg_variadic_concise(self):
        index_letter = self.subscript_letter_start # TODO allow this to be j etc

        indices_elts = [
            TexStringGroup(index_letter, subscript(t), labels = ["index"])
            for t in ["1", "2", "n"]
        ]

        indices = TexStringGroup([
            indices_elts[0],
            indices_elts[1],
            r"\cdots",
            indices_elts[2],
        ], labels = ["indices"])

        return (self.letter, subscript(indices))

    @tex_string_group
    def tsg_indexed_full(self):
        index_letters = [chr(ord(self.subscript_letter_start) + t) for t in range(self.n_subscript_indices)]

        indices_elts = [
            TexStringGroup(index_letter, labels = ["index"])
            for index_letter in index_letters
        ]

        indices = TexStringGroup(*indices_elts, labels = ["indices"])

        return (self.letter, subscript(indices))

class EquationLetterVector(EquationLetter):
    def __init__(
        self,
        letter: str,
        *,
        subscript_letter_start: str = "i",
        textify_letter: bool = True,
        # underline_letter: bool = True
    ) -> None:
        # if underline_letter:
        #     letter = fr"\underline{{{letter}}}"

        super().__init__(
            letter,
            1,
            subscript_letter_start = subscript_letter_start,
            textify_letter = textify_letter
        )

class EquationLetterMatrix(EquationLetter):
    def __init__(
        self,
        letter: str,
        *,
        subscript_letter_start: str = "i",
        textify_letter: bool = True
    ) -> None:
        super().__init__(
            letter,
            2,
            subscript_letter_start = subscript_letter_start,
            textify_letter = textify_letter
        )

class Basis:
    def __init__(
        self,
        vspace: VectorSpace,
        name: str = "B",
        elt_letter: str = "e",
        set_vector_space_basis: bool = False
    ) -> None:
        self.vspace = vspace
        self.name = name
        self.elt_letter = elt_letter

        if self.vspace.is_variadic:
            self.vectors = [
                Vector(self.elt_letter, subscript(f"{i}"), vspace = self.vspace)
                for i, _ in enumerate(range(2), 1)
            ] + [
                Vector(self.elt_letter, subscript(f"{self.size}"), vspace = self.vspace)
            ]
        else:
            self.vectors = [
                Vector(self.elt_letter, subscript(f"{i}"), vspace = self.vspace)
                for i, _ in enumerate(range(self.size), 1)
            ]

        if set_vector_space_basis:
            vspace.basis = self

    @property
    def size(self) -> int | str:
        return self.vspace.dimension

    @tex_string_group
    def tsg_letter(self):
        return fr"\mathcal{{{self.name}}}"

    @tex_string_group
    def tsg_full(self):
        if not self.vspace.is_variadic and self.size <= 3:
            tex_strings_main = [self.vectors[0].tsg_letters()]
            for vector in self.vectors[1:]:
                tex_strings_main.append(",")
                tex_strings_main.append(vector.tsg_letters())

        else:
            tex_strings_main = [
                self.vectors[0].tsg_letters(), ",",
                self.vectors[1].tsg_letters(), ",",
                r"\cdots", ",",
                self.vectors[-1].tsg_letters(),
            ]

        return (self.tsg_letter(), "=", r"\lbrace", *tex_strings_main, r"\rbrace")

class LinearMap:
    def __init__(
        self,
        letter: str = r"\alpha",
        vspace_from: VectorSpace | None = None,
        vspace_to: VectorSpace | None = None,
    ) -> None:
        self.letter = letter
        self.vspace_from = vspace_from
        self.vspace_to = vspace_to

        if self.vspace_from is None:
            self.vspace_from = VectorSpace("V", "n")
            self.vspace_from.basis = Basis(self.vspace_from, "B", "e")
        if self.vspace_to is None:
            self.vspace_to = VectorSpace("W", "m")
            self.vspace_to.basis = Basis(self.vspace_to, "C", "f")

    def applied_to(self, vec: Vector) -> Vector:
        return Vector(
                self.tsg_letter(), "(",
                TexStringGroup(vec.tsg_letters(), labels = [fqln(self, "argument")]),
                ")",
            vspace = self.vspace_to,
            with_arrow = False
        )

    @tex_string_group
    def tsg_letter(self):
        return self.letter

    @tex_string_group
    def tsg_from_to(self):
        return (
            self.tsg_letter(),
            ":", self.vspace_from.tsg_letter(),
            r"\to", self.vspace_to.tsg_letter()
        )

    @tex_string_group
    def tsg_repr(self):
        return (
            "[", self.tsg_letter(), "]", subscript(
                TexStringGroup(self.vspace_from.basis.tsg_letter(), labels = [fqln(self, "basis_from")]),
                ",",
                TexStringGroup(self.vspace_to.basis.tsg_letter(), labels = [fqln(self, "basis_to")]),
            )
        )

    @tex_string_group
    def tsg_repr_contents(self):
        if not self.vspace_from.is_variadic and self.vspace_from.dimension <= 3:
            tex_strings_main = []
            tex_strings_main.append(self.applied_to(self.vspace_from.basis.vectors[0]).tsg_repr())
            for vector in self.vspace_from.basis.vectors[1:]:
                tex_strings_main.append("|")
                tex_strings_main.append(self.applied_to(vector).tsg_repr())
        else:
            tex_strings_main = [
                self.applied_to(self.vspace_from.basis.vectors[0]).tsg_repr(), "|",
                self.applied_to(self.vspace_from.basis.vectors[1]).tsg_repr(), "|",
                r"\cdots", "|",
                self.applied_to(self.vspace_from.basis.vectors[-1]).tsg_repr(),
            ]

        return tuple(iter_interspersed(
            ("[", *tex_strings_main, "]"),
            r"\medspace"
        ))

    @tex_string_group
    def tsg_repr_linear_map_matrix_mult(self, v: Vector):
        return TexStringGroup(
            self.applied_to(v).tsg_repr(), "=", self.tsg_repr(), r"\cdot", v.tsg_repr(),
        )

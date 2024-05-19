from manim import *

from ManimTSG import *
from ManimTSG import LinearAlgebra

class ChapterTest(Scene):
    def construct(self):
        super().construct()

        V = LinearAlgebra.VectorSpace("V", "n")
        W = LinearAlgebra.VectorSpace("W", "m")

        B = LinearAlgebra.Basis(V, "B", "e", set_vector_space_basis = True)
        C = LinearAlgebra.Basis(W, "C", "e'", set_vector_space_basis = True)

        v = LinearAlgebra.Vector("v", vspace = V)

        alpha = LinearAlgebra.LinearMap(r"\alpha", vspace_from = V, vspace_to = W)

        tex_example = (
            tsg_example := alpha.tsg_repr_linear_map_matrix_mult(v)
        ).mathtex()

        print(*tsg_example.flatten(), sep = "")
        tsg_example.dump()

        self.add(tex_example)

        self.play(*(
            Indicate(tex_example[s])
            for s in tsg_example.find_by_label("Basis.letter")
        ))

        self.play(*(
            Indicate(tex_example[s])
            for s in tsg_example.find_by_label("LinearMap.argument")
        ))

        self.play(*(
            Indicate(tex_example[idx])
            for idx in tsg_example.find_by_str("[", "]")
        ))

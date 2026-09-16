from __future__ import annotations

from manim import DOWN, MathTex, Text, VGroup

class EquationRenderer:
    """Creates equations with compact semantic annotations instead of plain text."""
    def make(self, spec, color):
        expression = spec.get("expression", "") if isinstance(spec, dict) else spec.expression
        definitions = spec.get("symbol_definitions", {}) if isinstance(spec, dict) else spec.symbol_definitions
        equation = MathTex(expression, color=color)
        labels = VGroup(*[Text(f"{symbol}: {meaning}", font_size=20, color=color) for symbol, meaning in definitions.items()])
        if labels:
            labels.arrange(DOWN, aligned_edge=0).next_to(equation, DOWN)
            return VGroup(equation, labels)
        return equation

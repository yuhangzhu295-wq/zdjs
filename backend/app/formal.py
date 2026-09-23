"""Deterministic verification for a deliberately narrow arithmetic subset."""
from __future__ import annotations

import ast
import re
from fractions import Fraction

from .models import Claim, Evidence, EvidencePool


class FormalMathVerifier:
    """Verifies basic arithmetic without model inference or external retrieval.

    Only an expression made of numeric literals, parentheses, and the four basic
operators is accepted. Any other input stays on the evidence-research path.
    """

    _QUESTION = re.compile(
        r"^\s*(?P<expression>[0-9.\s+\-*/×÷()加减乘除以]+?)(?:等于多少|是多少)?[？?！!]?\s*$"
    )
    _NUMBER = re.compile(r"^[-+]?\d+(?:\.\d+)?$")

    def evaluate_question(self, question: str) -> Fraction | None:
        match = self._QUESTION.fullmatch(question)
        if not match:
            return None
        expression = match.group("expression")
        normalized = (
            expression.replace("乘以", "*").replace("除以", "/")
            .replace("加", "+").replace("减", "-")
            .replace("乘", "*").replace("除", "/")
            .replace("×", "*").replace("÷", "/")
        )
        if not any(operator in normalized for operator in "+-*/"):
            return None
        try:
            return self._evaluate(ast.parse(normalized, mode="eval").body)
        except (SyntaxError, ValueError, ZeroDivisionError):
            return None

    def evidence_pool(self, question: str, claims: list[Claim]) -> EvidencePool | None:
        result = self.evaluate_question(question)
        if result is None:
            return None
        answer = self.format(result)
        evidence = []
        for claim in claims:
            candidate = self._number(claim.text)
            stance = "support" if candidate == result else "counter"
            evidence.append(Evidence(
                evidence_id=f"formal_{claim.claim_id}", claim_id=claim.claim_id, stance=stance,
                source_type="formal_verification", title="Deterministic arithmetic verification",
                url="formal://arithmetic", source_name="Local arithmetic verifier",
                quote_or_fact=f"{question.strip()} = {answer}", direct_match=True,
                reliability_tier=1, fields={"expression": question.strip(), "result": answer},
            ))
        return EvidencePool(evidence=evidence)

    @classmethod
    def _number(cls, value: str) -> Fraction | None:
        value = value.strip()
        if not cls._NUMBER.fullmatch(value):
            return None
        return Fraction(value)

    @classmethod
    def _evaluate(cls, node: ast.AST) -> Fraction:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return Fraction(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = cls._evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            left, right = cls._evaluate(node.left), cls._evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            return left / right
        raise ValueError("unsupported arithmetic syntax")

    @staticmethod
    def format(value: Fraction) -> str:
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"

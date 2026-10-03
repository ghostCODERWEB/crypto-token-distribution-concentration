"""Measure token ownership inequality, concentration and minimal coalition sizes for declared voting thresholds."""

from .common import (
    number,
    integer,
    identity,
    records,
    chronology,
    allocate,
    result,
    validate_document,
)
from decimal import Decimal


def _analyze(d):
    accounts = records(d["accounts"], "id")
    values = sorted(integer(a["balance"]) for a in accounts)
    total = sum(values)
    n = len(values)
    if total == 0 or n == 0:
        raise ValueError("positive total supply required")
    gini = number(sum((2 * i - n - 1) * v for i, v in enumerate(values, 1))) / (
        n * total
    )
    hhi = sum((number(v) / total) ** 2 for v in values)
    ranked = sorted(accounts, key=lambda a: (-a["balance"], a["id"]))
    coalitions = []
    for threshold in d["thresholds"]:
        ratio = number(threshold, maximum=1)
        cumulative = 0
        members = []
        for a in ranked:
            if number(cumulative) >= total * ratio:
                break
            cumulative += a["balance"]
            members.append(a["id"])
        coalitions.append(
            {
                "threshold": ratio,
                "members": members,
                "count": len(members),
                "balance": cumulative,
            }
        )
    return result(
        {
            "supply": total,
            "holders": n,
            "gini": gini,
            "hhi": hhi,
            "top_holder_share": number(max(values)) / total,
            "coalitions": coalitions,
        }
    )


def analyze(document):
    validate_document(document)
    try:
        return result(_analyze(document))
    except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
        raise ValueError("invalid domain input: " + str(error)) from error

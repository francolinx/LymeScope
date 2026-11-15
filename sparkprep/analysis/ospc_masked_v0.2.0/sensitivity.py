"""Fixed-alignment row deletion and reuse of already-scored sequence positions."""
import math
from core import AA, column_stats, require


def average_ranks(values):
    """Ascending ranks; exact numeric ties receive their average rank."""
    indices = sorted(range(len(values)), key=values.__getitem__)
    ranks = [None] * len(values)
    begin = 0
    while begin < len(indices):
        end = begin + 1
        while end < len(indices) and values[indices[end]] == values[indices[begin]]:
            end += 1
        rank = (begin + 1 + end) / 2
        for i in indices[begin:end]:
            ranks[i] = rank
        begin = end
    return ranks


def rank_comparison(left, right, eligible):
    columns = sorted(eligible)
    require(all(math.isfinite(left[c]) and math.isfinite(right[c]) for c in columns), "Nonfinite rank value")
    a = average_ranks([left[c] for c in columns])
    b = average_ranks([right[c] for c in columns])
    rho = None
    if len(a) >= 2:
        am, bm = sum(a) / len(a), sum(b) / len(b)
        da, db = [x - am for x in a], [x - bm for x in b]
        denominator = math.sqrt(sum(x*x for x in da) * sum(x*x for x in db))
        if denominator:
            rho = sum(x*y for x, y in zip(da, db)) / denominator
    return {"common_eligible_columns": columns, "n": len(columns), "spearman_rho": rho,
            "analysis_set": "exact common eligible alignment columns enumerated in this result",
            "ties": "ascending average ranks for exact numeric equality; no rounding/tolerance tie merging",
            "null_reason": "fewer than two columns or a constant vector" if rho is None else None,
            "inference": "descriptive only; dependent columns; no p-value or significance claim"}


def aggregate(alignment, scores=None, retained=None):
    retained = list(alignment) if retained is None else list(retained)
    require(retained and len(retained) == len(set(retained)) and set(retained) <= set(alignment), "Invalid retained set")
    require(len({len(alignment[a]) for a in retained}) == 1, "Unequal alignment lengths")
    indexed = {(r["accession"], r["alignment_column"]): r for r in scores or []}
    require(len(indexed) == len(scores or []), "Duplicate score key")
    out = []
    for index in range(len(alignment[retained[0]])):
        stats = column_stats(alignment[a][index] for a in retained)
        observed = [a for a in retained if alignment[a][index] in AA]
        values = [-indexed[a, index + 1]["log_probability"] for a in observed if (a, index + 1) in indexed]
        out.append({"alignment_column": index + 1, **stats, "remaining_sequences": len(retained),
                    "full_coverage": len(observed) == len(retained), "model_score_count": len(values),
                    "mean_negative_log_probability": math.fsum(values) / len(values) if values else None,
                    "full_coverage_model_eligible": len(observed) == len(retained) == len(values)})
    return out


def leave_out(alignment, scores, removed, provenance):
    removed = list(removed)
    require(removed and len(set(removed)) == len(removed) and set(removed) < set(alignment), "Invalid leave-out group")
    retained = [a for a in alignment if a not in removed]
    before, after = aggregate(alignment, scores), aggregate(alignment, scores, retained)
    changes = []
    for a, b in zip(before, after):
        # Standard residues in every original row stay standard after row deletion.
        require(not a["full_coverage"] or b["full_coverage"], "Full coverage lost by row deletion")
        variable = a["modal_fraction"] is not None and a["modal_fraction"] < 1
        changes.append({"alignment_column": a["alignment_column"],
                        "conservation_change_at_originally_variable_column":
                            b["modal_fraction"] - a["modal_fraction"] if variable and b["modal_fraction"] is not None else None,
                        "coverage_change_at_originally_incomplete_column": b["coverage"] - a["coverage"] if not a["full_coverage"] else None,
                        "newly_apparent_observed_conservation": variable and b["modal_fraction"] == 1,
                        "newly_apparent_full_coverage_conservation": variable and b["modal_fraction"] == 1 and b["full_coverage"],
                        "remaining_contributors": b["contributing_sequences"]})
    # Same column set for both rankings. Newly complete columns are reported above
    # but do not silently expand the rank-comparison population.
    common = [a["alignment_column"] for a, b in zip(before, after) if a["full_coverage"] and b["full_coverage"]]
    ranks = {"conservation": rank_comparison({r["alignment_column"]: r["modal_fraction"] for r in before},
                                             {r["alignment_column"]: r["modal_fraction"] for r in after}, common)}
    common_model = [a["alignment_column"] for a, b in zip(before, after)
                    if a["full_coverage_model_eligible"] and b["full_coverage_model_eligible"]]
    ranks["masked_score"] = rank_comparison({r["alignment_column"]: r["mean_negative_log_probability"] for r in before},
                                            {r["alignment_column"]: r["mean_negative_log_probability"] for r in after}, common_model)
    return {"removed_accessions": removed, "retained_accessions": retained, "grouping_provenance": provenance,
            "column_aggregation_set": "all original alignment columns over the explicitly retained sequences; coverage and score counts per column",
            "alignment_policy": "fixed original columns; no realignment or column renumbering",
            "additional_model_forward_calls": 0, "columns": after, "changes": changes, "rank_comparisons": ranks}

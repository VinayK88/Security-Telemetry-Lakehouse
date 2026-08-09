from __future__ import annotations

from typing import Iterable, List

from .models import FeatureWindow, Finding


def score_features(features: Iterable[FeatureWindow]) -> List[Finding]:
    findings: List[Finding] = []

    for f in features:
        # Transparent baseline scoring. Production systems should learn baselines
        # per tenant/entity and calibrate thresholds with labeled outcomes.
        failure_component = min(1.0, f.failed_logins / 10.0)
        ip_component = min(1.0, max(0, f.distinct_ips - 1) / 5.0)
        sensitive_component = min(1.0, f.sensitive_actions / 2.0)
        risk_component = f.average_risk

        score = (
            0.35 * failure_component
            + 0.25 * ip_component
            + 0.25 * sensitive_component
            + 0.15 * risk_component
        )

        if score >= 0.35:
            reasons = []
            if f.failed_logins >= 5:
                reasons.append(f"{f.failed_logins} failed events")
            if f.distinct_ips >= 3:
                reasons.append(f"{f.distinct_ips} distinct source IPs")
            if f.sensitive_actions:
                reasons.append(f"{f.sensitive_actions} sensitive actions")
            if f.average_risk >= 0.5:
                reasons.append(f"average event risk {f.average_risk:.2f}")

            findings.append(
                Finding(
                    principal=f.principal,
                    finding_type="unusual_identity_behavior",
                    score=round(score, 4),
                    reason="; ".join(reasons) or "combined behavioral deviation",
                    window_start=f.window_start,
                )
            )

    return sorted(findings, key=lambda x: x.score, reverse=True)

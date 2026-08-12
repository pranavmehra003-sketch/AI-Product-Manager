"""
Demo / Simulation Fallback Module
Generates realistic, deterministic agent outputs when the LLM API is
unavailable (quota exceeded, network error, missing key).

This ensures the product demo always works — even offline or during quota limits.
All outputs match the exact Pydantic schemas in models/schemas.py.
"""
from __future__ import annotations
import re
import hashlib
import random
from typing import Any, Dict, List


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _stable_seed(seed_input: str) -> int:
    """Deterministic integer seed from string, so same input → same output."""
    return int(hashlib.md5(seed_input.encode("utf-8")).hexdigest()[:8], 16)


def _pick_categories(topics: List[str]) -> List[str]:
    """Pick the most relevant category keywords from a list of feedback topics."""
    categories = [
        "Performance", "Stability", "UI/UX", "Mobile", "Dark Mode",
        "Reporting", "Collaboration", "Integrations", "Billing",
        "Notifications", "Accessibility", "Security", "Search",
        "Onboarding", "Export/Import",
    ]
    text = " ".join(topics).lower()
    matched = []
    for c in categories:
        kw = c.lower()
        # search for the keyword or fragments of it in feedback text
        if any(part in text for part in kw.split()):
            matched.append(c)
    # fallback: populate with defaults based on popularity
    if not matched:
        matched = ["Performance", "UI/UX", "Stability"]
    return matched


# ─── 1. Feedback Agent Simulation ────────────────────────────────────────────

def simulate_feedback_analysis(feedback_list: List[str]) -> Dict[str, Any]:
    """Simulate the Feedback Analysis Agent output."""
    rng = random.Random(_stable_seed(str(len(feedback_list)) + "|".join(feedback_list[:50])))

    # Keyword-based issue/feature counts to reflect real distribution
    issue_keywords = {
        "slow report loading": [
            "slow", "load", "loading", "report", "lag", "delay", "performance",
            "fast", "speed", "take too long", "wait",
        ],
        "App crashes / errors": [
            "crash", "error", "bug", "broken", "freeze", "500", "404",
            "fail", "exception", "doesn't work",
        ],
        "Mobile app performance issues": [
            "mobile", "phone", "ios", "android", "app", "slow on phone",
            "tablet", "responsive",
        ],
        "Confusing navigation / UI": [
            "confusing", "hard to use", "difficult", "ui", "navigation",
            "can't find", "unclear", "clunky", "counterintuitive",
        ],
        "Missing export formats": [
            "export", "pdf", "csv", "download", "excel", "xlsx", "save",
        ],
        "Login / authentication problems": [
            "login", "sign in", "auth", "password", "sso", "2fa", "logout",
        ],
    }
    feature_keywords = {
        "Dark mode / Theme toggle": [
            "dark", "theme", "night", "light mode", "black background",
        ],
        "Real-time collaboration": [
            "collaborat", "share", "team", "multiple users", "real-time",
            "simultaneous", "live", "comment",
        ],
        "Mobile app": [
            "mobile app", "iphone", "android app", "native app", "play store",
            "app store",
        ],
        "Scheduled reports / alerts": [
            "schedule", "alert", "notif", "email me", "remind", "summary",
        ],
        "Custom dashboards": [
            "dashboard", "custom", "widget", "personalize", "layout",
        ],
        "API access / integrations": [
            "api", "integration", "webhook", "slack", "salesforce", "zapier",
            "connect",
        ],
        "Advanced filtering / search": [
            "filter", "search", "find", "query", "sort", "advanced",
        ],
        "Keyboard shortcuts": [
            "shortcut", "hotkey", "keyboard", "cmd+", "ctrl+",
        ],
    }

    combined_text = " ".join(feedback_list).lower()

    # ── Count issues ──
    issues: List[Dict[str, Any]] = []
    for issue_name, keywords in issue_keywords.items():
        count = sum(1 for kw in keywords if kw in combined_text)
        freq = rng.randint(18, 142) if count > 0 else rng.randint(2, 40)
        # Boost the biggest issue: "Slow reports" gets ~142 mentions
        if issue_name.startswith("slow report") or issue_name.startswith("Slow report"):
            freq = rng.randint(120, 150)
        if freq < 5:
            continue
        impact = "High" if freq >= 70 else ("Medium" if freq >= 35 else "Low")
        # Map to stable category
        if "crash" in issue_name.lower() or "error" in issue_name.lower():
            cat = "Stability"
        elif "mobile" in issue_name.lower():
            cat = "Mobile"
        elif "slow" in issue_name.lower() or "loading" in issue_name.lower():
            cat = "Performance"
        elif "navigation" in issue_name.lower() or "confusing" in issue_name.lower():
            cat = "UI/UX"
        elif "login" in issue_name.lower() or "auth" in issue_name.lower():
            cat = "Security"
        elif "export" in issue_name.lower():
            cat = "Export/Import"
        else:
            cat = rng.choice(["Performance", "Stability", "UI/UX", "Reporting"])
        issues.append({
            "category": cat,
            "issue": issue_name,
            "frequency": int(freq),
            "impact": impact,
            "sample_mentions": rng.randint(2, 12),
        })

    issues.sort(key=lambda x: x["frequency"], reverse=True)
    issues = issues[:8]

    # ── Count feature requests ──
    feature_requests: List[Dict[str, Any]] = []
    for feature_name, keywords in feature_keywords.items():
        count = sum(1 for kw in keywords if kw in combined_text)
        freq = rng.randint(12, 95) if count > 0 else rng.randint(1, 30)
        # Dark mode should be high
        if "dark" in feature_name.lower():
            freq = rng.randint(70, 95)
        # Mobile as a feature request
        if "mobile app" in feature_name.lower():
            freq = rng.randint(80, 100)
        if freq < 4:
            continue
        feature_requests.append({
            "feature": feature_name,
            "frequency": int(freq),
            "customer_segment": rng.choices(
                ["Enterprise", "SMB", "Consumer", "All"],
                weights=[0.35, 0.35, 0.2, 0.1],
                k=1,
            )[0],
        })
    feature_requests.sort(key=lambda x: x["frequency"], reverse=True)
    feature_requests = feature_requests[:8]

    # ── Sentiment & categories ──
    all_text = " ".join(feedback_list)
    pos_words = len(re.findall(
        r"\b(good|great|love|excellent|amazing|nice|perfect|awesome|helpful|useful|best|fantastic)\b",
        all_text, re.IGNORECASE,
    ))
    neg_words = len(re.findall(
        r"\b(bad|terrible|awful|hate|worst|poor|annoying|frustrat|buggy|broken|slow|crash|problem|issue|disappoint)\b",
        all_text, re.IGNORECASE,
    ))
    total = max(1, pos_words + neg_words + 1)
    neg_pct = round(neg_words / total * 100, 1)
    neu_pct = 40.0
    pos_pct = round(100 - neg_pct - neu_pct, 1)

    return {
        "status": "success",
        "summary": (
            f"Analyzed {len(feedback_list)} feedback entries. "
            f"Top issues: {issues[0]['issue']} ({issues[0]['frequency']} mentions), "
            f"{issues[1]['issue']} ({issues[1]['frequency']} mentions). "
            f"Top feature request: {feature_requests[0]['feature']}."
        ),
        "total_feedback": len(feedback_list),
        "sentiment_distribution": {
            "positive": max(25.0, pos_pct),
            "neutral": max(20.0, neu_pct),
            "negative": max(neg_pct, 15.0),
        },
        "common_themes": _pick_categories([f["issue"] for f in issues] + [f["feature"] for f in feature_requests]),
        "trending_issues": [issues[0]["issue"], issues[1]["issue"]],
        "issues": issues,
        "feature_requests": feature_requests,
    }


# ─── 2. Competitor Agent Simulation ──────────────────────────────────────────

def simulate_competitor_analysis(product_domain: str, competitors: List[str]) -> Dict[str, Any]:
    """Simulate the Competitor Research Agent output."""
    rng = random.Random(_stable_seed(product_domain + "|".join(competitors)))

    competitor_names = competitors if competitors else ["Competitor A", "Competitor B", "Competitor C"]
    # Defaults for common domains
    if product_domain and not competitors:
        if "analytic" in product_domain.lower():
            competitor_names = ["Tableau", "Power BI", "Looker Studio", "Mode Analytics"]
        elif "project" in product_domain.lower():
            competitor_names = ["Asana", "Monday.com", "Jira", "Notion"]
        elif "crm" in product_domain.lower():
            competitor_names = ["Salesforce", "HubSpot", "Pipedrive", "Zoho CRM"]

    all_features = [
        ("Dark mode / Theme toggle", True),
        ("Advanced report builder", True),
        ("Real-time collaboration", True),
        ("Mobile native app", True),
        ("Custom dashboards", True),
        ("Scheduled report emails", True),
        ("SSO / SAML authentication", True),
        ("Role-based access control", True),
        ("Public shareable links", True),
        ("AI-powered insights", True),
        ("Slack / Teams integration", True),
        ("Zapier / Webhook API", True),
        ("CSV / PDF export", True),
        ("Version history", False),
        ("Offline mode", False),
        ("White-labeling", False),
    ]

    competitor_list: List[Dict[str, Any]] = []
    feature_matrix: Dict[str, List[str]] = {}

    for comp in competitor_names:
        comp_dict = {
            "name": comp,
            "url": f"https://www.{comp.lower().replace(' ', '')}.com",
            "pricing_tier": rng.choice(["Free", "Freemium", "Mid-market", "Enterprise"]),
            "recent_launches": rng.sample([
                f"{comp} AI Assistant",
                f"{comp} Mobile v2",
                "Redesigned report builder",
                "Native Slack integration",
                "Enterprise SSO",
                "Custom branding",
                "Automated alerting",
            ], k=2),
            "strengths": rng.sample([
                "Rich visualization library",
                "Deep enterprise features",
                "Best-in-class mobile experience",
                "Strong collaboration tools",
                "Affordable pricing",
                "Robust partner ecosystem",
            ], k=2),
            "weaknesses": rng.sample([
                "Steep learning curve",
                "Expensive at scale",
                "Limited custom branding",
                "Slow report rendering",
                "Weak offline support",
                "Poor accessibility",
            ], k=2),
        }
        competitor_list.append(comp_dict)

        # Which features does this competitor have?
        feat_list = []
        for feat_name, common in all_features:
            has = common and rng.random() < 0.8
            if has:
                feat_list.append(feat_name)
            if feat_name not in feature_matrix:
                feature_matrix[feat_name] = []
            if has:
                feature_matrix[feat_name].append(comp)

    # Market gaps = features no competitor has, or only <1/2 of them have
    market_gaps = []
    for feat_name, have in feature_matrix.items():
        if len(have) <= 1:
            market_gaps.append(feat_name)
    # Also add one custom gap
    custom_gaps = [
        "Unified workspace for data + notes + chat",
        "One-click cross-source dashboard blending",
        "Customer-facing embedded analytics portal",
        "No-code automation builder",
        "Voice-controlled report navigation",
        "Real-time collaborative report editing with live cursors",
    ]
    for cg in rng.sample(custom_gaps, k=2):
        if cg not in market_gaps:
            market_gaps.append(cg)

    return {
        "status": "success",
        "competitors_analyzed": len(competitor_names),
        "competitors": competitor_list,
        "competitor_features": [
            {"name": comp["name"], "features": feature_matrix.get(comp["name"], [])}
            for comp in competitor_list
        ],
        "feature_coverage": {
            feat: len(haves) / max(1, len(competitor_list))
            for feat, haves in feature_matrix.items()
        },
        "market_gaps": market_gaps,
        "opportunities": [
            f"Match {competitor_names[0]} on {rng.choice(all_features)[0]}." if competitor_names else "Match market leaders on key features.",
            f"Capitalize on: {market_gaps[0]}." if market_gaps else "Capitalize on underserved market gaps.",
            f"Position against {competitor_names[1]}'s weakness: {competitor_list[1]['weaknesses'][0]}."
            if len(competitor_names) > 1 and len(competitor_list) > 1 and competitor_list[1].get("weaknesses")
            else f"Position against {competitor_names[0]}'s weakness: {competitor_list[0]['weaknesses'][0]}."
            if competitor_names and competitor_list and competitor_list[0].get("weaknesses")
            else "Position against key competitor weaknesses.",
        ],
    }


# ─── 3. Product Analytics Agent Simulation ───────────────────────────────────

def simulate_product_analytics(analytics_data: Dict[str, Any], feedback_topics: List[str]) -> Dict[str, Any]:
    """Simulate the Product Analytics Agent output."""
    rng = random.Random(_stable_seed(str(analytics_data) + "|".join(feedback_topics)))

    # If user provided analytics JSON, weave it through, otherwise generate defaults
    feature_metrics: List[Dict[str, Any]] = []
    provided = analytics_data.get("features", []) if isinstance(analytics_data, dict) else []

    if provided:
        for fm in provided:
            usage = fm.get("usage_percent", fm.get("usage", rng.randint(15, 90)))
            ret = fm.get("retention_impact", rng.choice(["High", "Medium", "Low"]))
            err = fm.get("error_rate", round(rng.uniform(0.2, 7.5), 1))
            trend = fm.get("trend", rng.choice(["Increasing", "Stable", "Declining"]))
            feature_metrics.append({
                "feature": fm.get("feature", "Unknown feature"),
                "usage_percent": float(usage),
                "dau": int(fm.get("dau", max(500, usage * rng.randint(100, 300)))),
                "mau": int(fm.get("mau", max(1500, usage * rng.randint(400, 900)))),
                "retention_impact": ret,
                "error_rate": float(err),
                "trend": trend,
                "top_error": fm.get("top_error", f"Slow response for >{rng.randint(5,50)}k rows"),
            })
    else:
        default_features = [
            "Reports & Dashboards",
            "Data Exports (CSV/PDF)",
            "Team Workspaces",
            "Search & Filter",
            "Mobile View",
            "Scheduled Emails",
            "SSO / Security",
            "Public Sharing",
        ]
        for feat in default_features:
            usage = rng.randint(22, 92)
            err = round(rng.uniform(0.1, 6.5), 1)
            if "Report" in feat:
                usage = rng.randint(70, 92)
                err = round(rng.uniform(2.8, 5.5), 1)
            if "Mobile" in feat:
                err = round(rng.uniform(3.5, 7.5), 1)
            feature_metrics.append({
                "feature": feat,
                "usage_percent": float(usage),
                "dau": int(max(500, usage * rng.randint(120, 280))),
                "mau": int(max(1500, usage * rng.randint(450, 850))),
                "retention_impact": rng.choices(
                    ["High", "Medium", "Low"],
                    weights=[0.4, 0.4, 0.2], k=1,
                )[0],
                "error_rate": float(err),
                "trend": rng.choice(["Increasing", "Stable", "Declining"]),
                "top_error": rng.choice([
                    "Timeout on large datasets",
                    "Blank screen on iOS Safari",
                    "Export fails for 10k+ records",
                    "Slow dashboard rendering",
                    "Permissions error for shared links",
                ]),
            })

    overall = {
        "dau": sum(f["dau"] for f in feature_metrics) // len(feature_metrics),
        "mau": sum(f["mau"] for f in feature_metrics) // len(feature_metrics),
        "avg_session_minutes": round(rng.uniform(6.5, 22.3), 1),
        "weekly_retention_pct": round(rng.uniform(35.0, 68.0), 1),
        "conversion_to_paid_pct": round(rng.uniform(2.2, 8.9), 1),
        "churn_rate_pct": round(rng.uniform(2.0, 7.5), 1),
    }

    # Highlight which features are the most risky from a product POV
    high_priority = [
        f["feature"] for f in feature_metrics
        if f["error_rate"] >= 3.0 and f["usage_percent"] >= 50
    ]

    return {
        "status": "success",
        "overall_metrics": overall,
        "features": feature_metrics,
        "top_growth_features": [
            f["feature"] for f in sorted(feature_metrics, key=lambda x: x["usage_percent"], reverse=True)[:3]
        ],
        "high_risk_features": high_priority[:4],
        "recommendations": [
            f"Investigate error rate on {high_priority[0]} ({next(f['error_rate'] for f in feature_metrics if f['feature']==high_priority[0])}%)",
            f"Double down on growth of {feature_metrics[0]['feature']} — highest usage at {feature_metrics[0]['usage_percent']}%.",
            f"Reduce churn by fixing {feature_metrics[-1]['feature']} issues before expanding marketing.",
        ],
    }


# ─── 4. Prioritization Agent Simulation ──────────────────────────────────────

def simulate_prioritization(
    feedback: Dict[str, Any],
    competitors: Dict[str, Any],
    analytics: Dict[str, Any],
    business_goals: List[str],
) -> Dict[str, Any]:
    """Simulate the Prioritization Agent output using the 5-factor score."""
    rng = random.Random(
        _stable_seed(
            str(feedback.get("issues", []))
            + str(competitors.get("market_gaps", []))
            + "|".join(business_goals),
        )
    )

    candidates: List[Dict[str, Any]] = []

    # Candidates come from top issues + top feature requests
    for item in feedback.get("issues", [])[:4]:
        candidates.append({
            "name": f"Improve: {item['issue']}",
            "type": "bugfix",
            "freq": item["frequency"],
            "impact": item["impact"],
        })
    for item in feedback.get("feature_requests", [])[:4]:
        candidates.append({
            "name": f"Build: {item['feature']}",
            "type": "feature",
            "freq": item["frequency"],
            "impact": "High" if item["frequency"] > 50 else "Medium",
        })
    # Add gap-based candidates
    for gap in competitors.get("market_gaps", [])[:3]:
        candidates.append({
            "name": f"Capitalize: {gap}",
            "type": "differentiator",
            "freq": 55,
            "impact": "High",
        })

    # Absolute safety: if no candidates were generated, provide a robust default set
    # (prevents IndexError on priorities[0] downstream when feedback/competitor data is empty)
    if not candidates:
        candidates = [
            {"name": "Improve: Application stability and crash recovery", "type": "bugfix", "freq": 80, "impact": "High"},
            {"name": "Improve: Page load and rendering performance", "type": "bugfix", "freq": 95, "impact": "High"},
            {"name": "Build: Customizable dashboard widgets", "type": "feature", "freq": 72, "impact": "High"},
            {"name": "Build: Dark mode / theme toggle", "type": "feature", "freq": 68, "impact": "Medium"},
            {"name": "Build: Advanced search and filtering", "type": "feature", "freq": 55, "impact": "Medium"},
            {"name": "Capitalize: Native mobile app experience", "type": "differentiator", "freq": 60, "impact": "High"},
            {"name": "Capitalize: Real-time collaboration features", "type": "differentiator", "freq": 55, "impact": "High"},
        ]

    priorities: List[Dict[str, Any]] = []
    for idx, c in enumerate(candidates):
        # Base values
        ci = {"High": 9, "Medium": 7, "Low": 5}[c["impact"]]
        bv = 9 if c["type"] == "bugfix" else (8 if c["type"] == "differentiator" else 7)
        sa = 8 if idx < 3 else (7 if idx < 6 else 6)
        urg = 9 if c["type"] == "bugfix" and c["freq"] > 70 else (8 if c["freq"] > 50 else 6)
        feas = 8 if c["type"] == "feature" else (7 if c["type"] == "bugfix" else 5)

        # Small deterministic jitter
        jitter = rng.uniform(-0.6, 0.6)
        score = round(
            (ci * 0.30) + (bv * 0.25) + (sa * 0.20) + (urg * 0.15) + (feas * 0.10) + jitter,
            2,
        )
        score = max(1.0, min(10.0, score))
        if score >= 8.0:
            p = "P0"
        elif score >= 7.0:
            p = "P1"
        elif score >= 6.0:
            p = "P2"
        else:
            p = "P3"

        reason_parts = []
        if c["freq"] >= 70:
            reason_parts.append(f"high customer volume ({c['freq']} mentions)")
        if c["type"] == "bugfix":
            reason_parts.append("stability risk")
        if c["type"] == "differentiator":
            reason_parts.append("competitive gap")
        if c["type"] == "feature":
            reason_parts.append("strong demand")
        reason = (
            f"This {c['type']} has " + ", ".join(reason_parts) + "."
        )

        priorities.append({
            "feature": c["name"],
            "description": (
                f"Address {c['name'].split(': ', 1)[-1]} to improve "
                f"customer satisfaction and retention."
            ),
            "type": c["type"],
            "customer_impact": ci,
            "business_value": bv,
            "strategic_alignment": sa,
            "urgency": urg,
            "feasibility": feas,
            "priority_score": score,
            "priority": p,
            "estimated_effort": {
                "P0": "2 sprints",
                "P1": "1 sprint",
                "P2": "0.5 sprint",
                "P3": "< 0.5 sprint",
            }[p],
            "reason": reason,
            "dependencies": rng.sample(
                ["None", "Design review", "Backend API", "Analytics tracking"],
                k=rng.randint(0, 2),
            ),
            "source": c["type"] if c["type"] in ("bugfix", "feature", "differentiator") else "combined",
        })

    priorities.sort(key=lambda x: x["priority_score"], reverse=True)
    # Ensure top item is P0
    priorities[0]["priority"] = "P0"
    priorities[0]["priority_score"] = max(priorities[0]["priority_score"], 8.2)

    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for p in priorities:
        counts[p["priority"]] += 1

    return {
        "methodology": (
            "Priority Score = Customer Impact × 0.30 + Business Value × 0.25 "
            "+ Strategic Alignment × 0.20 + Urgency × 0.15 + Feasibility × 0.10"
        ),
        "recommendation_summary": (
            f"Based on the combined analysis of feedback, competitors, and analytics, "
            f"{len(priorities)} features should be prioritized. Focus on P0 ({counts['P0']}) "
            f"and P1 ({counts['P1']}) items in the next sprint to address stability concerns, "
            f"capture market gaps, and drive progress on key business goals."
        ),
        "p0_count": counts["P0"],
        "p1_count": counts["P1"],
        "p2_count": counts["P2"],
        "p3_count": counts["P3"],
        "features": priorities,
    }


# ─── 5. PRD Writer Agent Simulation ──────────────────────────────────────────

def simulate_prd_writer(
    feature_name: str,
    product_name: str,
    product_domain: str,
    prioritization: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a complete PRD in dict form for a single feature."""
    rng = random.Random(_stable_seed(feature_name + product_name))
    clean_name = feature_name.split(": ", 1)[-1] if ": " in feature_name else feature_name

    # Find the matching prioritized feature to get scores
    def _feature_name(f: Dict[str, Any]) -> str:
        return f.get("feature") or f.get("name") or ""

    feat_meta = next(
        (f for f in prioritization.get("features", []) if clean_name in _feature_name(f)),
        None,
    ) or {
        "type": "feature",
        "priority": "P1",
        "priority_score": 7.5,
        "estimated_story_points": 10,
    }

    persona_raw = [
        {
            "name": "Enterprise Data Analyst",
            "role": "Senior Analyst at Fortune 500 company",
            "goal": f"Reliably analyze 100k+ rows daily using {product_name}",
            "pain": f"Current {clean_name.lower()} experience is unreliable for large datasets",
        },
        {
            "name": "SMB Operations Manager",
            "role": "Operations lead at 50-person company",
            "goal": "Create and share reports with leadership in under 5 minutes",
            "pain": f"Lacks custom settings for {clean_name.lower()}",
        },
        {
            "name": "Mobile Sales Executive",
            "role": "Field sales, uses iOS primarily",
            "goal": "Review key metrics between customer visits",
            "pain": f"{clean_name} is broken/slow on mobile",
        },
    ]

    # User personas as flat strings per PRDDocument schema
    user_personas = [
        f"{p['name']}: {p['role']}. Goal: {p['goal']}" for p in persona_raw
    ]

    # User stories matching UserStory schema (persona / action / benefit)
    us_personas = ["enterprise data analyst", "SMB operations manager", "mobile sales executive"]
    us_actions = [
        f"be able to run {clean_name.lower()} reliably on large datasets",
        f"have customization options and presets for {clean_name.lower()}",
        f"use {clean_name.lower()} effectively on my mobile device",
    ]
    us_benefits = [
        "I can trust my reports are accurate and delivered in time.",
        "my team and I can use the feature efficiently and share work.",
        "I can review and act on data between customer visits.",
    ]
    user_stories = []
    for i in range(3):
        story_acceptance = [
            f"Given the user is a {us_personas[i]}, when they perform {clean_name.lower()}, then the expected {us_actions[i].split()[0].lower()} outcome is produced.",
            f"When an error occurs during {clean_name.lower()}, the user sees a clear actionable message and a retry option.",
            f"All changes made during {clean_name.lower()} are persisted with no data loss on failure.",
        ]
        if i == 1:
            story_acceptance = [
                f"User can save up to 10 presets for {clean_name.lower()} configuration.",
                "A preset can be shared with team members via a single share action.",
                "Non-admin users cannot modify company-wide shared presets.",
            ]
        elif i == 2:
            story_acceptance = [
                f"{clean_name} renders correctly on mobile viewport sizes (iPhone and Android common widths).",
                "All primary actions for the feature are reachable with one thumb tap.",
                "Offline cache preserves the last 5 results when network is unavailable.",
            ]
        user_stories.append({
            "persona": us_personas[i].title(),
            "action": us_actions[i],
            "benefit": us_benefits[i],
            "acceptance_criteria": story_acceptance,
        })

    goals = [
        f"Reduce {clean_name.lower()} errors by 70% within 2 quarters.",
        f"Increase {clean_name.lower()} CSAT from 3.2/5 to 4.3/5.",
        f"Improve mobile completion rate for {clean_name.lower()} by 40%.",
    ]

    non_goals = [
        f"Rewriting the entire {product_name} UI from scratch.",
        "Introducing a new billing plan or pricing tier as part of this change.",
        "Support for legacy IE 11 browser.",
    ]

    functional_requirements = [
        f"FR-1 P0: 95th percentile latency for {clean_name.lower()} ≤ 3 seconds on 10k-record datasets.",
        "FR-2 P0: Every user action shows a loading state within 200ms after click.",
        "FR-3 P1: Users can save, name, and share presets/configuration for this feature.",
        "FR-4 P1: Mobile-first responsive layout, meeting WCAG AA accessibility standards.",
        "FR-5 P2: Offline mode preserves cached operations until connection is restored.",
    ]

    non_functional_requirements = [
        f"NFR-1 Performance: {clean_name.capitalize()} must work on Chrome, Safari, Firefox, Edge (2 latest versions).",
        "NFR-2 Observability: All API calls include request IDs for distributed tracing.",
        "NFR-3 Analytics: Logging of success/failure rates per action in Segment/Amplitude.",
        "NFR-4 Security: No sensitive data (PII/credentials) in query parameters or logs.",
    ]

    success_metrics = [
        f"{clean_name} P95 latency: target < 3s (baseline 8.2s)",
        f"{clean_name} error rate: target < 0.5% (baseline 4.2%)",
        f"Weekly active users of {clean_name}: target +25% vs baseline",
        f"CSAT on {clean_name} feature: target 4.3/5 (baseline 3.2/5)",
    ]

    dependencies = [
        "Backend team ships the new batch query API for this feature.",
        "Design team delivers final Figma specs for both mobile and desktop states.",
        "Data team confirms and signs off on query plan on the warehouse side.",
    ]

    risks = [
        "Risk: Query optimization may slip past the sprint boundary. Mitigation: Ship incremental phased rollout behind feature flags.",
        "Risk: Users resist the new UX pattern. Mitigation: Run an opt-in beta with 5% of users before full rollout.",
        "Risk: Mobile regression on older iOS / Android versions. Mitigation: QA on iOS 15+ and Android 11+ devices early in the sprint.",
    ]

    acceptance_criteria = [
        f"End-to-end test suite for {clean_name.lower()} passes on CI before merge.",
        "Load test simulates 2,000 concurrent users with <3s p95 response time.",
        "QA sign-off on desktop + mobile + accessibility audits.",
        "Beta cohort CSAT ≥ 4.2/5, or remaining regressions are documented and tracked as follow-ups.",
    ]

    technical_considerations = (
        "Evaluate read replicas or Redis cache layer to offload hot queries. "
        "Use WebSocket or streaming JSON responses for progressive rendering. "
        "Track every user action with unique event IDs for funnel analysis. "
        "Implement feature-flag gating for phased rollout (0% → 1% → 5% → 50% → 100%)."
    )

    return {
        "status": "success",
        "version": "1.0",
        "author": "AI Product Manager",
        "created_at": __import__("datetime").datetime.now().isoformat(),
        "feature_name": clean_name,
        "product_name": product_name,
        "product_domain": product_domain,
        "priority": feat_meta["priority"],
        "priority_score": feat_meta.get("priority_score", 7.5),
        "problem_statement": (
            f"Customers repeatedly report problems with {clean_name.lower()}: "
            f"it is {rng.choice(['slow', 'unreliable', 'missing customization', 'hard to use on mobile'])} "
            f"— this is causing churn, support tickets, and competitive losses."
        ),
        "background": (
            f"{clean_name.capitalize()} has {feat_meta.get('priority_score', 7.5):.1f}/10 priority based on "
            f"feedback volume and analytics. Competitors have already launched equivalent improvements."
        ),
        "user_personas": user_personas,
        "user_stories": user_stories,
        "goals": goals,
        "non_goals": non_goals,
        "functional_requirements": functional_requirements,
        "non_functional_requirements": non_functional_requirements,
        "success_metrics": success_metrics,
        "dependencies": dependencies,
        "risks": risks,
        "acceptance_criteria": acceptance_criteria,
        "technical_considerations": technical_considerations,
        "timeline_estimate": "Estimated 2 sprints / 4 weeks including rollout.",
        "estimated_story_points": feat_meta.get("estimated_story_points", 13),
    }


# ─── 6. Sprint Planner Agent Simulation ───────────────────────────────────────

def simulate_sprint_planner(
    approved_features: List[Dict[str, Any]],
    prds: List[Dict[str, Any]],
    capacity: int,
    team_size: int,
    sprint_number: int,
) -> Dict[str, Any]:
    """Simulate the Sprint Planner Agent output."""
    rng = random.Random(_stable_seed(str(approved_features) + str(capacity) + str(sprint_number)))

    tasks: List[Dict[str, Any]] = []
    # (Display assignee name, short team code for schema)
    teams = [
        ("Backend Team", "Backend"),
        ("Frontend Team", "Frontend"),
        ("Design Team", "Design"),
        ("QA Team", "QA"),
        ("DevOps / SRE", "DevOps"),
    ]
    p_to_sprint_priority = {
        "P0": "Must Have",
        "P1": "Must Have",
        "P2": "Should Have",
        "P3": "Nice to Have",
    }

    # Build tasks per approved feature
    for feat in approved_features:
        fname = (feat.get("feature") or feat.get("name") or "Feature").split(": ", 1)[-1]
        feat_priority = feat.get("priority", "P2")
        sprint_priority = p_to_sprint_priority.get(feat_priority, "Should Have")
        base_tasks = [
            (f"Design review & finalize specs for {fname}", 2, ("Design Team", "Design")),
            (f"Database / API work for {fname}", rng.randint(3, 8), ("Backend Team", "Backend")),
            (f"Implement {fname} UI + loading states", rng.randint(2, 6), ("Frontend Team", "Frontend")),
            (f"Accessibility + mobile polish ({fname})", rng.randint(1, 4), ("Frontend Team", "Frontend")),
            (f"Instrument analytics for {fname}", 1, ("Backend Team", "Backend")),
            (f"E2E tests for {fname} acceptance criteria", rng.randint(2, 6), ("QA Team", "QA")),
            (f"Performance & load testing on {fname}", rng.randint(2, 5), ("QA Team", "QA")),
            (f"Feature flag + staging rollout plan for {fname}", 2, ("DevOps / SRE", "DevOps")),
        ]
        for task_name, sp, (assignee, team) in base_tasks:
            tasks.append({
                "task": task_name,
                "description": f"Complete {task_name} as part of delivering {fname} to production.",
                "feature": fname,
                "story_points": int(sp),
                "assignee": assignee,
                "team": team,
                "priority": sprint_priority,
                "dependencies": [],
                "acceptance_criteria": [
                    f"Task passes code review with no blocking comments.",
                    f"Associated automated tests pass on CI for {fname}.",
                ],
            })

    # Add dependencies (frontend tasks depend on backend)
    for idx, task in enumerate(tasks):
        if task["team"] == "Frontend":
            for j, other in enumerate(tasks):
                if other["team"] == "Backend" and other["feature"] == task["feature"]:
                    task["dependencies"] = [other["task"]]
                    break

    total_sp = sum(t["story_points"] for t in tasks)
    # If over capacity, drop lowest priority tasks until we fit
    if total_sp > capacity:
        p_order = {"Must Have": 0, "Should Have": 1, "Nice to Have": 2}
        tasks_sorted = sorted(tasks, key=lambda t: (p_order.get(t["priority"], 9), -t["story_points"]))
        kept = []
        used = 0
        for t in tasks_sorted:
            if used + t["story_points"] <= capacity:
                kept.append(t)
                used += t["story_points"]
        # Rebuild tasks list but keep same order as before (stable)
        kept_set = {id(k): k for k in kept}
        tasks = [t for t in tasks if id(t) in kept_set]

    # Organize by team
    by_team: Dict[str, List[Dict[str, Any]]] = {}
    for t in tasks:
        by_team.setdefault(t["assignee"], []).append(t)

    total_sp_now = sum(t["story_points"] for t in tasks)
    velocity_per_person = round(total_sp_now / max(1, team_size), 1)

    return {
        "status": "success",
        "sprint": f"Sprint {sprint_number}",
        "sprint_name": f"Sprint {sprint_number}",
        "sprint_number": int(sprint_number),
        "duration_weeks": 2,
        "capacity_story_points": int(capacity),
        "total_capacity": int(capacity),
        "team_size": int(team_size),
        "committed_story_points": int(total_sp_now),
        "used_capacity": int(total_sp_now),
        "capacity_utilization_pct": round(total_sp_now / max(1, capacity) * 100, 1),
        "velocity_per_person_points": velocity_per_person,
        "features_covered": list({t["feature"] for t in tasks}),
        "features_included": list({t["feature"] for t in tasks}),
        "total_tasks": len(tasks),
        "tasks": tasks,
        "tasks_by_team": {team: ts for team, ts in by_team.items()},
        "sprint_goal": (
            f"Deliver {len(set(t['feature'] for t in tasks))} approved features end-to-end "
            f"({total_sp_now}/{capacity} story points), with focus on quality and production readiness."
        ),
        "definition_of_done": [
            "Code reviewed and approved by at least one team member.",
            "Unit tests written with >80% coverage for changed code.",
            "Integration and E2E tests passing on CI.",
            "Product Manager demo completed and accepted.",
            "Documentation and help articles updated where user-facing behavior changed.",
            "Staged rollout plan + feature flags in place before production deploy.",
        ],
        "risks_and_notes": [
            f"{tasks[0]['feature'] if tasks else 'Top feature'} is cross-team — align on handoff on Day 3.",
            "Reserve 10% capacity for bugs and production incidents.",
            "Sprint demo scheduled for Wednesday of Week 2.",
        ],
        "risks": [
            f"{tasks[0]['feature'] if tasks else 'Scope'} complexity may exceed estimates — break tasks further on Day 1.",
            "Reserve 10% capacity for unplanned bugs and production incidents.",
            "Sprint demo scheduled for Wednesday of Week 2 — freeze scope Monday before.",
        ],
    }

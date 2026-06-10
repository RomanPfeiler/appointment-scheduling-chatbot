"""Build the 150 with-label entity-gold rows authored in chat by Claude.

The rows are stratified into 5 kinds × 30 utterances:
- canonical_topic_only:   30 — explicit topic term from ``nlp.synonyms``, no medium term
- paraphrase_topic_only:  30 — topic intent expressed WITHOUT any synonym substring
- canonical_medium_only:  30 — explicit medium term from ``nlp.synonyms``, no topic term
- paraphrase_medium_only: 30 — medium intent expressed WITHOUT any synonym substring
- canonical_both:         30 — explicit topic AND medium terms from ``nlp.synonyms``

Authorship: Claude Code (Anthropic) generated these in the implementation
session, guided by the canonical synonym list. The human verifies each row
before parsers depend on the gold. Disclosed in the report's Data section.

Run::

    python -m nlp.eval_data._build_entity_with_label

Re-running overwrites ``entity_with_label.jsonl`` byte-for-byte (deterministic).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nlp.synonyms import all_medium_synonyms, all_topic_synonyms

OUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "nlp"
    / "eval_data"
    / "entity_with_label.jsonl"
)


# (utterance, proposed_topic, proposed_medium, row_kind)
ROWS: list[tuple[str, str, str, str]] = [
    # ────────────────────────────────────────────────────────────────────
    # canonical_topic_only (30) — explicit topic term, no medium term
    # ────────────────────────────────────────────────────────────────────
    # investing (10)
    ("I'd like to talk about investing.", "investing", "none", "canonical_topic_only"),
    ("Can I schedule a meeting about my investment portfolio?", "investing", "none", "canonical_topic_only"),
    ("I want to invest some money.", "investing", "none", "canonical_topic_only"),
    ("I need help with mutual funds.", "investing", "none", "canonical_topic_only"),
    ("Looking to discuss stocks with an advisor.", "investing", "none", "canonical_topic_only"),
    ("I'd like a wealth management consultation.", "investing", "none", "canonical_topic_only"),
    ("Can you set up an appointment about asset management?", "investing", "none", "canonical_topic_only"),
    ("I want to discuss my investments.", "investing", "none", "canonical_topic_only"),
    ("Could we talk about my portfolio?", "investing", "none", "canonical_topic_only"),
    ("Need to discuss wealth planning.", "investing", "none", "canonical_topic_only"),
    # mortgage (10)
    ("I'd like to discuss a mortgage.", "mortgage", "none", "canonical_topic_only"),
    ("Can I book a meeting about a home loan?", "mortgage", "none", "canonical_topic_only"),
    ("I need advice on a house loan.", "mortgage", "none", "canonical_topic_only"),
    ("Mortgages — can I get advice?", "mortgage", "none", "canonical_topic_only"),
    ("I want to talk about a property loan.", "mortgage", "none", "canonical_topic_only"),
    ("Looking for real estate financing options.", "mortgage", "none", "canonical_topic_only"),
    ("Mortgage advice please.", "mortgage", "none", "canonical_topic_only"),
    ("Can we discuss hypothek?", "mortgage", "none", "canonical_topic_only"),
    ("I'm interested in immobilienfinanzierung.", "mortgage", "none", "canonical_topic_only"),
    ("Looking to refinance my mortgage.", "mortgage", "none", "canonical_topic_only"),
    # pension (10)
    ("I'd like to talk about my pension.", "pension", "none", "canonical_topic_only"),
    ("Can we discuss retirement options?", "pension", "none", "canonical_topic_only"),
    ("I need help with my pillar 3.", "pension", "none", "canonical_topic_only"),
    ("Looking for pension advice.", "pension", "none", "canonical_topic_only"),
    ("Can I book a meeting about my retirement plan?", "pension", "none", "canonical_topic_only"),
    ("I want to discuss my pillar 3a.", "pension", "none", "canonical_topic_only"),
    ("Altersvorsorge — I need advice.", "pension", "none", "canonical_topic_only"),
    ("Vorsorge planning — can we talk?", "pension", "none", "canonical_topic_only"),
    ("Old-age provision questions please.", "pension", "none", "canonical_topic_only"),
    ("Pensions — I'd like to plan.", "pension", "none", "canonical_topic_only"),

    # ────────────────────────────────────────────────────────────────────
    # paraphrase_topic_only (30) — topic intent, NO synonym substring
    # ────────────────────────────────────────────────────────────────────
    # investing paraphrases (10)
    ("I want to grow my money.", "investing", "none", "paraphrase_topic_only"),
    ("I'd like to put my savings to work.", "investing", "none", "paraphrase_topic_only"),
    ("Can we talk about my financial future?", "investing", "none", "paraphrase_topic_only"),
    ("I'm interested in earning passive income.", "investing", "none", "paraphrase_topic_only"),
    ("Looking to build long-term financial security.", "investing", "none", "paraphrase_topic_only"),
    ("How do I plan for the next decade financially?", "investing", "none", "paraphrase_topic_only"),
    ("Can I discuss my brokerage account?", "investing", "none", "paraphrase_topic_only"),
    ("I want to set up systematic savings plans.", "investing", "none", "paraphrase_topic_only"),
    ("Need help with diversification strategies.", "investing", "none", "paraphrase_topic_only"),
    ("I'd like advice on building a nest egg.", "investing", "none", "paraphrase_topic_only"),
    # mortgage paraphrases (10)
    ("I want to buy a flat and need financing.", "mortgage", "none", "paraphrase_topic_only"),
    ("Looking for help purchasing my first apartment.", "mortgage", "none", "paraphrase_topic_only"),
    ("Need to refinance the house I bought 10 years ago.", "mortgage", "none", "paraphrase_topic_only"),
    ("Can I get advice on borrowing for a condo?", "mortgage", "none", "paraphrase_topic_only"),
    ("I'm planning to buy a place to live and need a loan.", "mortgage", "none", "paraphrase_topic_only"),
    ("How do I finance a chalet purchase?", "mortgage", "none", "paraphrase_topic_only"),
    ("Need help with my home-buying finances.", "mortgage", "none", "paraphrase_topic_only"),
    ("Want to discuss borrowing for residential property.", "mortgage", "none", "paraphrase_topic_only"),
    ("I'm purchasing my second residence soon, need a loan.", "mortgage", "none", "paraphrase_topic_only"),
    ("Could we discuss the financing of a Wohnung purchase?", "mortgage", "none", "paraphrase_topic_only"),
    # pension paraphrases (10)
    ("Planning for my golden years.", "pension", "none", "paraphrase_topic_only"),
    ("I want to stop working in 15 years — can we plan?", "pension", "none", "paraphrase_topic_only"),
    ("Need advice on tax-advantaged savings for later life.", "pension", "none", "paraphrase_topic_only"),
    ("How do I prepare financially for after age 65?", "pension", "none", "paraphrase_topic_only"),
    ("Looking to build security for when I'm no longer employed.", "pension", "none", "paraphrase_topic_only"),
    ("Want to discuss my AHV strategy.", "pension", "none", "paraphrase_topic_only"),
    ("Can I get advice on my third-pillar account?", "pension", "none", "paraphrase_topic_only"),
    ("I need help planning my later-life income.", "pension", "none", "paraphrase_topic_only"),
    ("Looking at long-term savings for when I stop working.", "pension", "none", "paraphrase_topic_only"),
    ("Need to plan for life after work.", "pension", "none", "paraphrase_topic_only"),

    # ────────────────────────────────────────────────────────────────────
    # canonical_medium_only (30) — explicit medium term, no topic term
    # ────────────────────────────────────────────────────────────────────
    # branch (10)
    ("Can I come to the branch for the meeting?", "none", "branch", "canonical_medium_only"),
    ("I'd like to meet at the branch office.", "none", "branch", "canonical_medium_only"),
    ("Let's do it in-person.", "none", "branch", "canonical_medium_only"),
    ("Prefer to meet in person at your office.", "none", "branch", "canonical_medium_only"),
    ("Can we have a face to face meeting?", "none", "branch", "canonical_medium_only"),
    ("I'd like to come to the Filiale.", "none", "branch", "canonical_medium_only"),
    ("Meeting at your office works for me.", "none", "branch", "canonical_medium_only"),
    ("At the branch please.", "none", "branch", "canonical_medium_only"),
    ("I'll come to your nearest branch.", "none", "branch", "canonical_medium_only"),
    ("Want to meet in-person if possible.", "none", "branch", "canonical_medium_only"),
    # online (10)
    ("Can we do it online?", "none", "online", "canonical_medium_only"),
    ("A video call works for me.", "none", "online", "canonical_medium_only"),
    ("Let's schedule a video meeting.", "none", "online", "canonical_medium_only"),
    ("I'd prefer zoom if that's possible.", "none", "online", "canonical_medium_only"),
    ("Can we set up a Teams meeting?", "none", "online", "canonical_medium_only"),
    ("Online would be more convenient.", "none", "online", "canonical_medium_only"),
    ("Let's do a virtual meeting.", "none", "online", "canonical_medium_only"),
    ("Videoconference is fine.", "none", "online", "canonical_medium_only"),
    ("A web meeting suits me.", "none", "online", "canonical_medium_only"),
    ("I'd like to do this over video chat.", "none", "online", "canonical_medium_only"),
    # phone (10)
    ("Could you call me?", "none", "phone", "canonical_medium_only"),
    ("I'd prefer a phone call.", "none", "phone", "canonical_medium_only"),
    ("Phone meeting works for me.", "none", "phone", "canonical_medium_only"),
    ("Let's do it by phone.", "none", "phone", "canonical_medium_only"),
    ("Just ring me when convenient.", "none", "phone", "canonical_medium_only"),
    ("Telephone meeting please.", "none", "phone", "canonical_medium_only"),
    ("I'd like to do this by telefon.", "none", "phone", "canonical_medium_only"),
    ("Anruf gerne.", "none", "phone", "canonical_medium_only"),
    ("I'll take a phone call.", "none", "phone", "canonical_medium_only"),
    ("Phone is best for me.", "none", "phone", "canonical_medium_only"),

    # ────────────────────────────────────────────────────────────────────
    # paraphrase_medium_only (30) — medium intent, NO synonym substring
    # ────────────────────────────────────────────────────────────────────
    # branch paraphrases (10)
    ("Can I drop by your nearest location?", "none", "branch", "paraphrase_medium_only"),
    ("I'd like to come in physically.", "none", "branch", "paraphrase_medium_only"),
    ("Could we meet at a counter?", "none", "branch", "paraphrase_medium_only"),
    ("Let me visit you at the bank.", "none", "branch", "paraphrase_medium_only"),
    ("I prefer to come to your premises.", "none", "branch", "paraphrase_medium_only"),
    ("Meeting on-site works for me.", "none", "branch", "paraphrase_medium_only"),
    ("Can I walk into the building for this?", "none", "branch", "paraphrase_medium_only"),
    ("I'll come to your front desk.", "none", "branch", "paraphrase_medium_only"),
    ("Let's meet at the bricks-and-mortar location.", "none", "branch", "paraphrase_medium_only"),
    ("Can I sit down with someone there?", "none", "branch", "paraphrase_medium_only"),
    # online paraphrases (10)
    ("Can we do this over the internet?", "none", "online", "paraphrase_medium_only"),
    ("Let's set up a screen-sharing session.", "none", "online", "paraphrase_medium_only"),
    ("I'd prefer a remote consultation.", "none", "online", "paraphrase_medium_only"),
    ("Can we use Skype or something similar?", "none", "online", "paraphrase_medium_only"),
    ("A digital meeting works for me.", "none", "online", "paraphrase_medium_only"),
    ("Let's do a web conference.", "none", "online", "paraphrase_medium_only"),
    ("Could we connect over Google Meet?", "none", "online", "paraphrase_medium_only"),
    ("I'd like to do this from home over the web.", "none", "online", "paraphrase_medium_only"),
    ("Can we set up a Webex?", "none", "online", "paraphrase_medium_only"),
    ("Let's just do it on a webcam.", "none", "online", "paraphrase_medium_only"),
    # phone paraphrases (10)
    ("Can we just talk by voice?", "none", "phone", "paraphrase_medium_only"),
    ("Could you reach me on my mobile?", "none", "phone", "paraphrase_medium_only"),
    ("I'd like to use a landline conversation.", "none", "phone", "paraphrase_medium_only"),
    ("Let's do it by voice only.", "none", "phone", "paraphrase_medium_only"),
    ("A voice-only chat works for me.", "none", "phone", "paraphrase_medium_only"),
    ("Can I have a quick word with someone over a line?", "none", "phone", "paraphrase_medium_only"),
    ("Could we use audio only?", "none", "phone", "paraphrase_medium_only"),
    ("I'd prefer a verbal conversation.", "none", "phone", "paraphrase_medium_only"),
    ("Audio chat works for me.", "none", "phone", "paraphrase_medium_only"),
    ("Just give me a buzz when you can.", "none", "phone", "paraphrase_medium_only"),

    # ────────────────────────────────────────────────────────────────────
    # canonical_both (30) — both topic AND medium are synonym-list members
    # ────────────────────────────────────────────────────────────────────
    ("I'd like to discuss investing at the branch.", "investing", "branch", "canonical_both"),
    ("Investment consultation at the branch office please.", "investing", "branch", "canonical_both"),
    ("Can I come in person for portfolio advice?", "investing", "branch", "canonical_both"),
    ("Wealth management meeting at the Filiale please.", "investing", "branch", "canonical_both"),
    ("Can we discuss investments via video call?", "investing", "online", "canonical_both"),
    ("Portfolio review online would work.", "investing", "online", "canonical_both"),
    ("Wealth management consultation over Teams please.", "investing", "online", "canonical_both"),
    ("Phone call about my stocks please.", "investing", "phone", "canonical_both"),
    ("Can you call me to discuss investing?", "investing", "phone", "canonical_both"),
    ("I'd like to discuss a mortgage at the branch.", "mortgage", "branch", "canonical_both"),
    ("Home loan meeting in person please.", "mortgage", "branch", "canonical_both"),
    ("Hypothek advice at your office.", "mortgage", "branch", "canonical_both"),
    ("Mortgage consultation via video meeting please.", "mortgage", "online", "canonical_both"),
    ("Online mortgage review.", "mortgage", "online", "canonical_both"),
    ("Real estate financing over zoom.", "mortgage", "online", "canonical_both"),
    ("Call me about a home loan.", "mortgage", "phone", "canonical_both"),
    ("Mortgage advice by phone please.", "mortgage", "phone", "canonical_both"),
    ("Pension planning meeting at the branch.", "pension", "branch", "canonical_both"),
    ("Retirement consultation in person please.", "pension", "branch", "canonical_both"),
    ("Pillar 3 advice at your office.", "pension", "branch", "canonical_both"),
    ("Retirement planning via Teams.", "pension", "online", "canonical_both"),
    ("Pension review online.", "pension", "online", "canonical_both"),
    ("Video meeting about my pension please.", "pension", "online", "canonical_both"),
    ("Phone call about my retirement plan.", "pension", "phone", "canonical_both"),
    ("Telephone consultation about pillar 3 please.", "pension", "phone", "canonical_both"),
    ("Can I do mortgage advice in person at your branch?", "mortgage", "branch", "canonical_both"),
    ("Investing meeting via video chat please.", "investing", "online", "canonical_both"),
    ("Pillar 3 consultation by phone please.", "pension", "phone", "canonical_both"),
    ("Home loan via virtual meeting.", "mortgage", "online", "canonical_both"),
    ("Wealth management at the branch office.", "investing", "branch", "canonical_both"),
]


def synonym_hits(text: str, syns: set[str]) -> list[str]:
    """Lowercased substring presence — same logic as anti-bleed audit."""
    t = text.lower()
    return sorted({s for s in syns if s in t})


def main() -> None:
    topic_syns = all_topic_synonyms()
    medium_syns = all_medium_synonyms()

    out: list[dict[str, Any]] = []
    for i, (utterance, topic, medium, row_kind) in enumerate(ROWS, start=1):
        topic_subs = synonym_hits(utterance, topic_syns)
        medium_subs = synonym_hits(utterance, medium_syns)
        # Anti-bleed sanity at row-author time:
        # - canonical rows MUST contain at least one synonym for their labelled class
        # - paraphrase rows MUST NOT contain any synonym for their labelled class
        if row_kind == "canonical_topic_only" and not topic_subs:
            raise AssertionError(f"canonical_topic_only row #{i} has no topic synonym: {utterance!r}")
        if row_kind == "paraphrase_topic_only" and topic_subs:
            raise AssertionError(f"paraphrase_topic_only row #{i} contains topic synonym {topic_subs!r}: {utterance!r}")
        if row_kind == "canonical_medium_only" and not medium_subs:
            raise AssertionError(f"canonical_medium_only row #{i} has no medium synonym: {utterance!r}")
        if row_kind == "paraphrase_medium_only" and medium_subs:
            raise AssertionError(f"paraphrase_medium_only row #{i} contains medium synonym {medium_subs!r}: {utterance!r}")
        if row_kind == "canonical_both" and (not topic_subs or not medium_subs):
            raise AssertionError(f"canonical_both row #{i} missing topic or medium synonym: {utterance!r}")

        out.append(
            {
                "utterance_id": f"claude_authored_{i:03d}",
                "utterance": utterance,
                "source_dataset": "claude_authored",
                "source_service": "in_chat_authoring",
                "topic_proposed": topic,
                "contact_medium_proposed": medium,
                "synonym_substrings_present": {"topic": topic_subs, "medium": medium_subs},
                "is_hard_negative": False,
                "verified_topic": None,
                "verified_medium": None,
                "verified_includes_paraphrase": None,
                "verified": False,
                "row_kind": row_kind,
                "verification_notes": None,
            }
        )

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", encoding="utf-8") as f:
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Distribution summary
    by_kind: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    by_medium: dict[str, int] = {}
    for r in out:
        by_kind[r["row_kind"]] = by_kind.get(r["row_kind"], 0) + 1
        by_topic[r["topic_proposed"]] = by_topic.get(r["topic_proposed"], 0) + 1
        by_medium[r["contact_medium_proposed"]] = by_medium.get(r["contact_medium_proposed"], 0) + 1

    print(f"wrote {OUT_FILE} -- {len(out)} rows")
    print(f"  by row_kind: {by_kind}")
    print(f"  by topic_proposed: {by_topic}")
    print(f"  by contact_medium_proposed: {by_medium}")


if __name__ == "__main__":
    main()

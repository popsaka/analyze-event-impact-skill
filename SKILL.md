---
name: analyze-event-impact
description: Analyze how wars, policy changes, regulation, geopolitics, public-opinion shocks, supply disruptions, earnings, or other events may affect prices, sectors, commodities, currencies, or single names. Use when the user asks for event-driven market analysis, wants a client-facing impact note, or needs proprietary research/context turned into a structured view of first-order and second-order market effects.
---

# Analyze Event Impact

## Overview

Use this skill to convert an event into a defensible market-impact analysis.

Treat the skill as the workflow shell, not the moat. The moat is the private context: historical analogs, supply-chain logic, asset sensitivities, house views, and watchlists. Use a strong model, but reduce model variance by giving it better context, a tighter reasoning path, and a fixed output schema.

Use the model as a logic pressure tester, not a fact copier. The goal is not merely to restate the news. The goal is to test the user's frame, find expectation gaps, and expose weak links in the implied pricing narrative.

## Working Rules

- Separate `facts`, `inference`, and `unknowns`.
- Treat `market consensus` and `priced-in degree` as first-class inputs.
- Prefer `event -> transmission channel -> affected variable -> asset response -> timing`.
- Prioritize `expectation gap` over generic summary.
- State assumptions explicitly when the event is incomplete or unconfirmed.
- Reduce confidence when context is thin; do not fill gaps with generic macro commentary.
- Avoid naked directional calls unless the user explicitly asks for trading implications.
- Treat fine-tuning as a later optimization for style or stable structured labels, not the primary way to inject changing market knowledge.

## Minimum Inputs

Get these inputs before writing a full answer. If the user wants a fast first pass, proceed with assumptions and label them.

- Exact event: what happened, where, when, confirmed or rumor.
- Event stage: start, escalation, digestion, stabilization, or reversal.
- Market consensus: what the crowd appears to believe already.
- Priced-in degree: what the user thinks the market has already discounted.
- Ignored variables: what the user believes the market is underweighting.
- Asset universe: commodity, index, sector, FX, rates, crypto, single names.
- Time horizon: intraday, 1-3 days, 1-4 weeks, structural.
- Audience: internal discussion, client note, sales talking points, PM memo.
- Available private context: house view, prior event writeups, watchlists, analog cases.

If the user has a private knowledge base, ask them to paste or attach the most decision-relevant parts.

If the user does not have a private knowledge base, do not block. Ask only for:
- their core hypothesis
- what they think the market already priced in
- what variable they think the market is missing
- the asset and time horizon

This keeps the skill useful for ordinary clients while still improving sharply when proprietary context is available.

## Load Context

1. Read [intake-template.md](./references/intake-template.md) when the user has not yet provided a solid reference frame.
2. Read [event-impact-framework.md](./references/event-impact-framework.md).
3. Read [private-context-template.md](./references/private-context-template.md) when house knowledge or proprietary mappings are relevant.
4. Load only the needed local materials: event libraries, supply-chain maps, sensitivity tables, policy calendars, positioning notes, client watchlists.
5. Verify live facts and timestamps before discussing recent events.
6. Prefer high-signal internal context over long generic internet summaries.

## Delivery Formats

Always produce a readable in-chat answer first.

When the output is meant for sharing, also generate:
- a Markdown report as the editable source of truth
- a PDF version for distribution

Use the bundled script:

```bash
./scripts/render_report_pdf.py /path/to/report.md /path/to/report.pdf --preview-png
```

The script prefers a styled `reportlab` renderer when available and falls back to macOS built-in text rendering otherwise.

For prettier output on machines where dependencies can be installed:

```bash
python3 -m pip install reportlab
```

## Workflow

Use this exact sequence.

### 1) Event confirmation (internal thinking step, do not output by default)

- Classify as `A 已发生 / B 未发生（反事实） / C 信息不足`.
- Require at least 2 independent timestamped sources.
- Do not rely on model memory for recent events.
- This step is an internal intermediate state unless user explicitly asks to see evidence.

### 2) Event-stage assessment (must output)

If event is `A 已发生`, explicitly assess:
- major follow-up nodes after initial event (timeline bullets)
- current event status (escalating / digesting / stabilizing / reversing)
- target asset price path since event start
- what the price path implies about market consensus and priced-in degree

For occurred events, pull live market state before writing conclusions:
- target asset spot + recent performance
- key macro drivers used in your thesis (e.g., USD/oil/rates proxies)
- market-structure proxies (volatility, positioning, funding, ETF flow, OI, etc.)

For BTC/crypto client-facing answers, prefer these micro indicators (at least 3 when available):
- AHR999 (position anchor)
- Fear & Greed Index
- 200D MA deviation or Mayer Multiple
- RSI(14)
- Funding + OI change

Use local helper script for AHR999 + micro pack first:
```bash
python3 ./scripts/fetch_ahr999.py --symbol BTC --pretty
```
The script returns AHR999 and common micro indicators in one JSON (Fear&Greed / RSI14 / MA200 deviation / funding / OI).

AHR999 source order:
1) Coinglass public endpoint
2) Coinglass OpenAPI (if key is set)
3) Local formula fallback (CoinGecko + public AHR999 formula)

If AHR999 still returns unavailable, keep analysis running with confidence haircut and explicitly label AHR999 as unavailable.

If retrieval is partial, proceed with explicit confidence haircut and label missing indicators.

### 3) Quick take (must be one line)

Provide exactly one line containing numbers:
- most likely path
- probability (%)
- expected range for `1~3 days`
- expected range for `1 month`

### 4) Why (two layers)

Then explain in two concise sections:
- `宏观分析`
- `微观分析`

Each section should be compact, mechanism-based, and include concrete levels/ranges/thresholds where possible.

For `微观分析`, enforce this format per indicator:
- `指标名 = 当前值` + `一句指导意义` (how this value guides bias/risk/action)
- Keep each indicator explanation to one short sentence.

## Output Format

Default output order:

1. `Quick Take` (one line only, with probability + 1~3天区间 + 1个月区间)
2. `事件阶段与市场共识` (event nodes, current stage, price path, priced-in reading)
3. `原因`:
   - 宏观分析
   - 微观分析（每个指标都要“数值 + 一句话指导意义”）

Rules:
- Do not dump the A/B/C confirmation block by default; keep it internal.
- If status is `B` or `C`, label the answer as scenario simulation.
- Avoid tutorial tone; write for decision support.
- Keep numbers mandatory in the quick take line.

Optional only when user asks:
- source evidence block
- scenario table
- transmission map
- full memo + PDF export

## Failure Modes

Avoid these common mistakes:
- turning every shock into generic `risk-off`
- mixing confirmed facts with speculative links
- blindly trusting the user's `priced-in` estimate
- giving a single universal answer across all horizons
- skipping industry mechanics or supply-chain detail
- writing long prose when a table or tree would communicate faster
- treating the skill itself as the source of truth instead of loading real context

## Reference Maintenance

Keep the skill lean. Put durable domain knowledge in `references/` or nearby project files, not in this file.

When the team learns a new repeatable pattern, add it as:
- a new row in the analog library
- a new sensitivity rule
- a new counterexample
- a clearer client output example

Keep the boundary clean:
- the knowledge base answers `what do we know`
- this skill answers `how do we reason from it`

This is how the skill improves over time without pretending to retrain the model.

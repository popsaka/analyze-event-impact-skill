# analyze-event-impact-skill

Event-driven market-impact analysis skill for OpenClaw.

> Turns a client’s event question into a structured, decision-ready output with:  
> **event confirmation → stage assessment → one-line quick take → macro/micro reasoning**.

## What this skill is for

Use it when users ask: “How will this event affect price?”
- wars / geopolitics
- regulation / policy
- earnings / supply shocks
- narrative or sentiment events

It is optimized for **client-facing clarity**, not academic verbosity.

## Key features

- Hard-gated event confirmation logic (A/B/C internal state)
- One-line Quick Take with required numeric ranges:
  - probability
  - 1–3 day range
  - 1 month range
- Macro + Micro reasoning block
- Micro section requires:
  - indicator value
  - one-sentence practical meaning
- Built-in AHR999 + micro signal tooling

## Included scripts

### `scripts/fetch_ahr999.py`
Fetches AHR999 and a micro-indicator pack in one command.

Output includes:
- AHR999 (multi-source fallback)
- Fear & Greed
- RSI(14)
- MA200 deviation
- Funding rate (8h)
- OI 1d change

Source priority for AHR999:
1. Coinglass public endpoint
2. Coinglass OpenAPI (if key is provided)
3. Local formula fallback (CoinGecko + public formula)

## Usage

```bash
python3 scripts/fetch_ahr999.py --symbol BTC --pretty
```

Optional env for OpenAPI fallback:

```bash
export COINGLASS_API_KEY=your_key
# or
export COINGLASS_OPEN_API_KEY=your_key
```

## Skill output contract (default)

1. **Quick Take** (exactly one line, numeric)
2. **Event Stage & Market Consensus**
3. **Why**
   - Macro analysis
   - Micro analysis (value + one-line implication per indicator)

## Repository description (suggested)

OpenClaw skill for event-driven price-impact analysis with one-line numeric quick take, macro/micro framework, and AHR999 micro-signal fallback tooling.

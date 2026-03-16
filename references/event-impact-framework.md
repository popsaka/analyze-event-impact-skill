# Event Impact Framework

Use this file as the default reasoning skeleton. Fill only the sections that matter for the current event.

## 1. Build the reference frame

Before reasoning, pin down:

- What exactly changed today?
- Which stage is the event in: start, escalation, digestion, stabilization, or reversal?
- What does the market appear to believe already?
- How much does the user think is priced in?
- Which variable is the market most likely underweighting?

Treat `priced-in` as a hypothesis to test, not a number to obey.

## 2. Classify the event

### 2.1 Ten common event types

| Event type | What usually changes first | What to verify early | Common misread |
| --- | --- | --- | --- |
| War / geopolitics | Transport, sanctions, energy, shipping, defense spend, safe-haven flows | Physical disruption, sanctions scope, duration, chokepoints | Treating headlines as real supply loss |
| Single-company event | Guidance, financing, balance-sheet stress, management credibility | Official filing text, size/timing, accompanying financing actions | Treating one headline as the full valuation driver |
| Macro / rates / liquidity | Real yields, USD, growth expectations, risk appetite | Regime context, prior positioning, revision path | Overreacting to one print in isolation |
| Regulation / enforcement | Compliance cost, listing access, legal overhang | Effective date, scope, carve-outs, enforcement path | Treating announcement as immediate implementation |
| Exchange / market mechanics | Funding, OI, depth, liquidation intensity | Rule change specifics, timestamp, affected symbols | Confusing microstructure shock with fundamentals |
| Protocol / tokenomics change | Emission, burn, staking incentives, user economics | Activation timing, parameter sensitivity, adoption path | Assuming governance text equals real adoption |
| Security / credit event | Withdrawal pressure, trust discount, counterparty contagion | Loss size, recovery odds, solvency/liquidity gap | Underestimating second-order contagion |
| Supply shock | Volume, inventory, unlock flow, substitute capacity | Duration, spare capacity, buffer inventory | Treating temporary shock as structural |
| Narrative rotation | Relative flows, valuation spread, leadership shift | Trigger catalyst, breadth, crowdedness | Mistaking noise for regime shift |
| Positioning squeeze | Funding/OI/liquidation cascades, basis distortions | Leverage concentration and liquidation map | Interpreting forced flow as durable trend |

### 2.2 Collapse to 4 parent families + default emphasis

- A 外生冲击（war/macro/regulation/security）: default **逻辑70 / 数据30**
- B 内生基本面（single-company/protocol/supply）: default **数据70 / 逻辑30**
- C 微观结构（exchange mechanics/squeeze）: default **数据70 / 逻辑30**
- D 叙事制度切换（narrative rotation）: default **逻辑70 / 数据30**

Use this as a starting point, then adjust by observability/latency/reflexivity.

### 2.3 Single-company data checklist (when applicable)

Minimum factual checklist before conclusion:
- corporate action size + timestamp (e.g., treasury sold, financing amount, share issuance)
- official stated reason vs market interpretation
- 5-point price path around event window (D-1/D0/D1/D3/D5)
- at least one valuation proxy (P/S, EV/Sales, P/E if meaningful)
- market cap and at least 2 peers for relative move comparison

If any of the above is missing, label it explicitly and reduce confidence.

## 3. Find the expectation gap

Ask:

- What outcome is consensus?
- Which branch of the scenario tree is underpriced?
- Is the current price move linear while the underlying risk is non-linear?
- Is the market reacting to the headline, or to what the headline implies for a deeper variable?

If you cannot locate a plausible expectation gap, do not force one.

## 4. Map the transmission chain

Work through these links in order:

1. What changed?
2. Which economic variable changes first?
3. Which companies, sectors, or assets are directly exposed?
4. Which substitutes, complements, or downstream players move next?
5. Which markets may react mainly through positioning or sentiment?

## 5. Check the usual channels

- Physical supply
- Demand destruction
- Input costs
- Inventory and logistics
- Policy response
- FX pass-through
- Funding or liquidity conditions
- Positioning unwind
- Narrative or sentiment amplification

## 6. Split by horizon

| Horizon | Question |
| --- | --- |
| Immediate | What reprices first if the headline is true? |
| 1-3 days | What follow-through depends on confirmation or flow? |
| 1-4 weeks | Which second-order effects matter once desks digest the event? |
| Structural | What remains true even after the headline premium fades? |

## 7. Score confidence

- High: facts are verified, the mechanism is direct, and analogs are strong.
- Medium: at least one major link is inferred but plausible.
- Low: the event is rumor-heavy, the asset mapping is weak, or there are no useful analogs.

## 8. Force a counterview

Before finalizing, answer:

- What is the strongest alternative explanation?
- What evidence would prove this thesis wrong?
- What may already be priced in?
- Which missing context would change the conclusion fastest?

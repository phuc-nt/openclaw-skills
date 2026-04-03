# Recipe: Expense Tracker

Track expenses via natural language Telegram messages.

## How It Works

```
User: "spent 150k on lunch"
Agent: Parses → 150,000 VND, "lunch", category: Food
Agent: Appends to Google Sheets
Agent: "✅ Logged: 150k — Lunch (Food)"
```

## SOUL.md Addition

```markdown
## Expense Tracker
When user mentions spending ("spent", "paid", "bought", "cost"):
1. Parse: amount, description, category (Food/Transport/Bills/Shopping/Entertainment/Other)
2. Append to Google Sheets via: gws sheets +append
3. Confirm with short message

Categories: Food, Transport, Bills, Shopping, Entertainment, Health, Education, Other
```

## Google Sheets Setup

Create a spreadsheet "Expenses 2026" with columns:

| Date | Amount | Description | Category |
|---|---|---|---|
| 2026-04-03 | 150000 | Lunch | Food |

Agent creates the sheet on first use if it doesn't exist.

## Document Processor (Bonus)

For receipt photos:

```markdown
## Document Processor
When user sends a photo of receipt/invoice:
1. Read image with vision
2. Extract: date, amount, vendor, type
3. Append to Sheets + upload original to Drive
4. Confirm: "✅ Receipt: 800k — Electric bill (04/2026)"
```

No new scripts needed — uses built-in vision + existing gws skills.

## Weekly Summary

Add to Weekly Review cron:

```
"6. Expenses: gws sheets +read --spreadsheet-id SHEET_ID --range 'Sheet1!A:D'"
```

Agent calculates totals by category and includes in weekly scorecard.

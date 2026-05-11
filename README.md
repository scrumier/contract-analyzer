# contract-analyzer

Automated extraction of key clauses from supplier contracts.

## What it does

Given a set of supplier PDF contracts, the tool extracts the information a CFO or legal team actually needs: parties involved, contract dates, amounts, penalties, renewal and termination conditions.

The output is a structured HTML report with a flagged list of items that warrant attention — unusual clauses, missing fields, tight deadlines, or high-risk penalty terms.

## How it works

1. PDFs are parsed and the text is extracted
2. A language model (Claude via OpenRouter) reads each contract and returns structured data in a defined format
3. The tool applies a set of rules to identify points of vigilance
4. An HTML report is generated, readable without any technical knowledge

## Stack

- Python
- pdfplumber for text extraction
- Claude (via OpenRouter) for structured extraction
- HTML report output

## Use case

Designed for finance and legal teams who need to review large volumes of supplier contracts quickly. The tool does not replace legal review — it surfaces the key data so humans can focus their attention.

## Author

Sonam — [github.com/scrumier](https://github.com/scrumier)
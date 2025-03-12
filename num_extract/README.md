# Financial Data Extraction Tool

This project extracts financial information from PDF documents using pure Python, without any external APIs.

## Requirements

- Python 3.6+
- PyPDF2 library

## Installation

```bash
pip install PyPDF2
```

## Usage

1. Ensure your financial PDF documents are in the `numai/data/FY25 Air Force Working Capital Fund/pdf/` directory
2. Run the extraction script:

```bash
python extract_financial_data.py
```

3. Results will be saved to `numai/results/results.json`

## How It Works

The script performs the following steps:
1. Extracts text content from all PDF documents in the specified directory
2. Identifies tables and structured data using pattern matching
3. Extracts financial values, context information, and modifiers using multiple pattern strategies
4. Scores each financial data point to determine the most relevant match
5. Outputs structured JSON with the extracted financial information

The tool specifically looks for "Total Revenue FY 2025" in the "AFWCF Financial Summary" and correctly interprets values with modifiers like "Millions" to calculate the full numeric value.

## Output Format

```json
{
  "raw_value": "30,704.1",
  "context": "Total Revenue FY 2025",
  "modifier": "Millions",
  "interpreted_value": 30704100000,
  "page_number": 13,
  "table_name": "AFWCF Financial Summary"
}
```

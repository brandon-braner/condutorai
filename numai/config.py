from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='NUMAI_',
        env_file='.env',
        env_file_encoding='utf-8',
        )  
    

    gemini_api_key: str 
    gemini_model: str
    numai_dir: Path = Path(__file__).parent.resolve()
    data_dir: Path = numai_dir / "data"
    results_dir: Path = numai_dir / "results"

    prompt: str = """
## Task: Comprehensive Numerical Data Extraction from PDF


**Input:** The attached PDF document named "FY25 Air Force working Capital.pdf".

**Output:**  A structured data output (preferably in a format like JSON or a CSV-ready string) containing *all* numerical values found within the document, along with their correctly interpreted magnitudes.  The output should include:

1.  **Raw Value:** The number *exactly* as it appears in the PDF (e.g., "1,088.6", "28,239.2", "5.0", "(364.7)").  Include any commas, periods, or parentheses.
2.  **Context:**  A short string describing the context of the number.  This is *crucial* for interpreting the magnitude. Examples:
    *   "Total Revenue FY 2023"
    *   "Civilian End Strength FY 2024"
    *   "AF Blue FY 2025 4Rs - Risk Mitigation"
    *   "CSAG-M AOR FY 2025"
    *   "Page 3 - AFWCF Overview" (if a clear label isn't available)
    * The title of a table.
3.  **Modifier:** A string indicating the magnitude modifier, if present.  This should be standardized to one of the following:
    *   `"Millions"` (for "Millions", "Million", "M", or "$M")
    *   `"Billions"` (for "Billions", "Billion", or "B")
    *   `"Thousands"` (for "Thousands", "Thousand", or "K")
    *   `"None"` (if no modifier is present)
    *   `"Percent"` (if a percentage)
4.  **Interpreted Value:** The numerical value, converted to its *full* numerical representation (as a standard integer or floating-point number).  Apply the modifier correctly:
    *   `1,088.6 Millions`  ->  `1088600000`
    *   `(46.6) Millions` -> `-46600000`
    *   `2.0 Percent` -> `0.02`
    * `33,848 None` -> `33848`
5. **Page Number:** The page of the PDF where the number is present.
6. **Table Name**: If the number comes from a table, include the name of the table.

**Specific Instructions and Considerations:**

1.  **Table Extraction:**
    *   Recognize table structures, including headers and row labels.  Use these headers and labels to populate the `Context` field.
    *   Be aware of table headers that specify units (e.g., "(Dollars in Millions)", "($M)", "(Hours in Thousands)").  Apply these modifiers to *all* numbers within the scope of that header. This means for all numbers in that column or for all numbers in the table if specified for the whole table.
    *   If a table cell contains multiple numbers (which is less common but possible), extract *each* number individually.

2.  **Text Extraction:**
    *   Extract numbers that appear within the running text of the document.
    *   Use the surrounding text (e.g., a few words before and after) to provide context.  Look for keywords like "million", "billion", "thousand", "percent", etc., *immediately* following the number.
    * Be aware of negative numbers that are shown as a number in parentheses. Such as (46.6) should be read as -46.6.

3.  **Number Formats:**
    *   Handle numbers with commas (e.g., "28,239.2").
    *   Handle numbers with decimal points (e.g., "5.0").
    *   Handle numbers with parentheses, interpreting them as negative values (e.g., "(364.7)").
    *   Handle numbers with percentages.
    * Handle words that are numbers such as "one", "two", "three", etc.

4.  **Modifier Handling:**
    *   Be case-insensitive to modifiers ("Million", "million", "M", "MILLION" should all be treated the same).
    *   If a number is immediately followed by a recognized modifier word, use that modifier.
    *   If a number is within a table with a header-specified modifier, use that modifier.
    *   If no modifier is found, assume a modifier of "None".

5. **Ambiguity Resolution:**
    *   If there's ambiguity about the context of a number, provide the best possible guess based on surrounding text and page number.  It's better to have *some* context than none.
    *   If there's ambiguity about the modifier, and both a word modifier and a table header modifier are present, prioritize word modifier. For example: "10.1 Million Dollars" under a table called (Numbers in Thousands) we would still multiple 10.1 by a million.

6. **Output format:**
Return the largest number you find based on the number and modifier.


    {
        "raw_value": "28,239.2",
        "context": "Total Revenue FY 2023",
        "modifier": "Millions",
        "interpreted_value": 28239200000,
        "page_number": 9,
        "table_name": "AFWCF Financial Summary"
    }
"""




def get_settings() -> Settings:
    return Settings()

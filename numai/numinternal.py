import pdfplumber
import camelot
import re
import json
import pandas as pd
from numai.config import get_settings
# Function to standardize modifiers
def standardize_modifier(modifier_text):
    """
    Standardizes various modifier text representations to a consistent format.
    Args: modifier_text (str): A text representation of a numeric modifier.
    
    Returns: str: A standardized modifier ('Millions', 'Billions', 'Thousands', 'Percent', or 'None')."
    """
    modifier_text = modifier_text.lower().strip()
    if modifier_text in ['million', 'millions', 'm', '$m']:
        return 'Millions'
    elif modifier_text in ['billion', 'billions', 'b']:
        return 'Billions'
    elif modifier_text in ['thousand', 'thousands', 'k']:
        return 'Thousands'
    elif modifier_text in ['percent', '%']:
        return 'Percent'
    else:
        return 'None'

# Function to interpret the value based on raw value and modifier
def interpret_value(raw_value, modifier):
    """
    Interprets the value based on raw value and modifier.
    Args:
        raw_value (str): The raw value extracted from the PDF.
        modifier (str): The modifier extracted from the PDF.
    Returns:
        int or float: The interpreted value.
    """
    try:
        # Remove commas and handle parentheses for negative numbers
        cleaned_value = raw_value.replace(',', '')
        is_negative = cleaned_value.startswith('(') and cleaned_value.endswith(')')
        if is_negative:
            cleaned_value = cleaned_value[1:-1]
            cleaned_value = '-' + cleaned_value
        
        # Convert to float
        numeric_value = float(cleaned_value)
        
        # Apply modifier
        if modifier == 'Millions':
            numeric_value *= 1_000_000
        elif modifier == 'Billions':
            numeric_value *= 1_000_000_000
        elif modifier == 'Thousands':
            numeric_value *= 1_000
        elif modifier == 'Percent':
            numeric_value /= 100
        # If 'None', no change needed
        
        # Return as integer if no decimal places, otherwise float
        if numeric_value.is_integer():
            return int(numeric_value)
        return numeric_value
    except ValueError:
        return None

# Function to convert written numbers to digits
def convert_written_number(text):
    """
    Converts written numbers to digits.
    Args:
        text (str): A string containing a written number.
    Returns:
        int or None: The corresponding digit if the text is a written number, otherwise None.
    """
    number_words = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9
    }
    text = text.lower().strip()
    if text in number_words:
        return str(number_words[text])
    return None

# Function to extract numbers from text
def extract_numbers_from_text(page, page_num):
    """
    Extracts numbers from text on a given page.
    Args:
        page: The page object from pdfplumber.
        page_num (int): The page number.
    Returns:
        list: A list of dictionaries containing extracted numbers.
    """
    text = page.extract_text()
    if not text:
        return []
    
    results = []
    lines = text.split('\n')
    
    for line in lines:
        # Look for written numbers
        words = line.split()
        for word in words:
            written_num = convert_written_number(word)
            if written_num:
                context = ' '.join(words[max(0, words.index(word)-3):words.index(word)+4])
                results.append({
                    'raw_value': written_num,
                    'context': context,
                    'modifier': 'None',
                    'interpreted_value': interpret_value(written_num, 'None'),
                    'page_number': page_num,
                    'table_name': ''
                })
        
        # Regular expression to find numbers (including negatives in parentheses)
        number_pattern = r'(\(?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?)(?:\s*(million|billion|thousand|percent|m|b|k|%))?'
        matches = re.finditer(number_pattern, line, re.IGNORECASE)
        
        for match in matches:
            raw_value = match.group(1)
            modifier_text = match.group(2) or ''
            modifier = standardize_modifier(modifier_text)
            
            # Get context (few words before and after)
            start_idx = max(0, match.start() - 50)
            end_idx = min(len(line), match.end() + 50)
            context = line[start_idx:end_idx].strip()
            if not context:
                context = f"Page {page_num} - No clear context"
            
            interpreted_value = interpret_value(raw_value, modifier)
            
            results.append({
                'raw_value': raw_value,
                'context': context,
                'modifier': modifier,
                'interpreted_value': interpreted_value,
                'page_number': page_num,
                'table_name': ''
            })
    
    return results

# Function to extract numbers from tables
def extract_numbers_from_tables(pdf_path, page_num):
    """
    Extracts numbers from tables on a given page.
    Args:
        pdf_path (str): The path to the PDF file.
        page_num (int): The page number.
    Returns:
        list: A list of dictionaries containing extracted numbers.
    """
    try:
        tables = camelot.read_pdf(pdf_path, pages=str(page_num+1), flavor='lattice')
    except Exception as e:
        print(f"Error reading tables on page {page_num+1}: {e}")
        return []
    
    results = []
    
    for table in tables:
        df = table.df
        table_name = ''
        
        # Look for table title in the preceding text or first row
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num]
            text = page.extract_text()
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if any(cell in line for cell in df.iloc[0]):
                    table_name = line.strip()
                    break
            if not table_name and len(df) > 0:
                table_name = ' '.join(df.iloc[0].astype(str)).strip()
            if not table_name:
                table_name = f"Table on Page {page_num+1}"
        
        # Check for modifier in table header
        header_modifier = 'None'
        for cell in df.iloc[0]:
            cell_lower = str(cell).lower()
            if 'million' in cell_lower or '$m' in cell_lower:
                header_modifier = 'Millions'
                break
            elif 'billion' in cell_lower:
                header_modifier = 'Billions'
                break
            elif 'thousand' in cell_lower:
                header_modifier = 'Thousands'
                break
            elif 'percent' in cell_lower or '%' in cell_lower:
                header_modifier = 'Percent'
                break
        
        # Process each cell in the table
        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                cell = str(df.iloc[row_idx, col_idx]).strip()
                # Skip header row for number extraction
                if row_idx == 0 and not cell.replace(',', '').replace('.', '').isdigit():
                    continue
                
                number_pattern = r'(\(?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?)(?:\s*(million|billion|thousand|percent|m|b|k|%))?'
                matches = re.finditer(number_pattern, cell, re.IGNORECASE)
                
                for match in matches:
                    raw_value = match.group(1)
                    cell_modifier_text = match.group(2) or ''
                    cell_modifier = standardize_modifier(cell_modifier_text)
                    
                    # Use cell modifier if present; otherwise use header modifier
                    modifier = cell_modifier if cell_modifier != 'None' else header_modifier
                    
                    # Get context from row/col headers
                    row_label = str(df.iloc[row_idx, 0]) if col_idx > 0 else ''
                    col_label = str(df.iloc[0, col_idx]) if row_idx > 0 else ''
                    context = f"{row_label} {col_label}".strip()
                    if not context:
                        context = table_name
                    
                    interpreted_value = interpret_value(raw_value, modifier)
                    
                    results.append({
                        'raw_value': raw_value,
                        'context': context,
                        'modifier': modifier,
                        'interpreted_value': interpreted_value,
                        'page_number': page_num + 1,
                        'table_name': table_name
                    })
    
    return results

# Main function to process the PDF
def process_pdf(pdf_path: str):
    """
        Process a PDF file to extract and analyze numerical values from text and tables.
        
        Args:
            pdf_path (str): Path to the PDF file to be processed.
        
        Returns:
            tuple[list, dict]: A tuple containing:
                - A list of extracted number results with context and metadata
                - The largest number found in the PDF (or None if no numbers found)
        
        Extracts numbers from both text and table formats, filters out invalid results,
        and identifies the largest numerical value in the document.
    """
    all_results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")
        
        for page_num in range(total_pages):
            print(f"Processing page {page_num + 1}")
            
            # Extract numbers from text
            page = pdf.pages[page_num]
            text_results = extract_numbers_from_text(page, page_num + 1)
            all_results.extend(text_results)
            
            # Extract numbers from tables
            table_results = extract_numbers_from_tables(pdf_path, page_num)
            all_results.extend(table_results)
    
    # Filter out None interpreted values
    all_results = [result for result in all_results if result['interpreted_value'] is not None]
    
    # Find the largest number
    if all_results:
        largest_number = max(all_results, key=lambda x: x['interpreted_value'])
        return all_results, largest_number
    else:
        return [], None

# Main execution
def process_local_pdf(pdf_path:str):
    settings = get_settings()
    pdf_path = f"{settings.data_dir}/{pdf_path}"
    try:
        all_numbers, largest_number = process_pdf(pdf_path)
        
        # Output all numbers as JSON
        with open('extracted_numbers.json', 'w') as f:
            json.dump(all_numbers, f, indent=4)
        
        # Print the largest number
        if largest_number:
            print("\nLargest number found:")
            print(json.dumps(largest_number, indent=4))
        else:
            print("No numbers found in the PDF.")
            
        # Optionally, save to CSV
        if all_numbers:
            df = pd.DataFrame(all_numbers)
            df.to_csv('extracted_numbers.csv', index=False)
            print("\nAll numbers have been saved to 'extracted_numbers.csv'")
            
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
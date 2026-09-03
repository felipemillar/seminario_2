import os
import subprocess
import re
import unicodedata
from bs4 import BeautifulSoup, NavigableString

def normalize_text(text):
    return unicodedata.normalize('NFC', text)

def html_to_md(element, in_list=False, in_table=False):
    if isinstance(element, NavigableString):
        return element.string
        
    tag = element.name
    if not tag:
        return ""
        
    # Process tables customly to preserve cell integrity and avoid double lines
    if tag == 'table':
        trs = element.find_all('tr')
        rows_md = []
        for i, tr in enumerate(trs):
            cells = []
            for cell in tr.find_all(['td', 'th'], recursive=False):
                cell_content = "".join(html_to_md(c, in_list=False, in_table=True) for c in cell.children).strip()
                cell_content = cell_content.replace("\n", "<br>").replace("|", "\\|")
                cells.append(cell_content)
            
            if not cells:
                continue
            row_str = "| " + " | ".join(cells) + " |"
            rows_md.append(row_str)
            if i == 0:
                sep = "| " + " | ".join(["---"] * len(cells)) + " |"
                rows_md.append(sep)
        return "\n" + "\n".join(rows_md) + "\n"

    child_mds = []
    for child in element.children:
        child_mds.append(html_to_md(child, in_list=in_list or (tag in ['ul', 'ol', 'li']), in_table=in_table))
    content = "".join(child_mds)
    
    if tag == 'h1':
        return f"\n# {content.strip()}\n"
    elif tag == 'h2':
        return f"\n## {content.strip()}\n"
    elif tag == 'h3':
        return f"\n### {content.strip()}\n"
    elif tag == 'h4':
        return f"\n#### {content.strip()}\n"
    elif tag == 'h5':
        return f"\n##### {content.strip()}\n"
    elif tag == 'h6':
        return f"\n###### {content.strip()}\n"
    elif tag == 'p':
        if in_table or in_list:
            return content.strip()
        return f"\n{content.strip()}\n"
    elif tag in ['b', 'strong']:
        stripped = content.strip()
        if not stripped:
            return content
        left_spaces = content[:len(content) - len(content.lstrip())]
        right_spaces = content[len(content.rstrip()):]
        return f"{left_spaces}**{stripped}**{right_spaces}"
    elif tag in ['i', 'em']:
        stripped = content.strip()
        if not stripped:
            return content
        left_spaces = content[:len(content) - len(content.lstrip())]
        right_spaces = content[len(content.rstrip()):]
        return f"{left_spaces}*{stripped}*{right_spaces}"
    elif tag == 'li':
        parent_tag = element.parent.name if element.parent else 'ul'
        item_text = content.strip()
        if parent_tag == 'ol':
            return f"1. {item_text}\n"
        else:
            return f"- {item_text}\n"
    elif tag in ['ul', 'ol']:
        list_content = "\n".join([line for line in content.split("\n") if line.strip()])
        return f"\n{list_content}\n"
    elif tag == 'br':
        return "\n"
    elif tag == 'sup':
        return f"^{content.strip()}^"
    elif tag in ['html', 'body', 'span', 'div', 'font']:
        return content
    else:
        return content

def clean_for_count(text):
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove markdown symbols
    text = re.sub(r"[\*\#\_\|\^`~-]", " ", text)
    tokens = text.split()
    words = []
    for t in tokens:
        # Strip trailing and leading punctuation
        t_clean = re.sub(r"^[^\w]+|[^\w]+$", "", t)
        # Strip all punctuation inside the word (like parenthesis)
        t_clean = re.sub(r"[^\w]", "", t_clean)
        if not t_clean:
            continue
        # Strip trailing numbers (citations or code indexes) in both raw and MD
        if re.search(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ]\d+$", t_clean):
            t_clean = re.sub(r"\d+$", "", t_clean)
        # Ignore purely numeric tokens
        if re.match(r"^\d+$", t_clean):
            continue
        words.append(t_clean)
    return words

def convert_file(docx_path, md_path):
    # 1. Extract raw text from docx for verification
    result_txt = subprocess.run(['textutil', '-convert', 'txt', '-stdout', docx_path], capture_output=True, text=True)
    if result_txt.returncode != 0:
        raise RuntimeError(f"textutil txt failed: {result_txt.stderr}")
    raw_text = result_txt.stdout
    raw_words = clean_for_count(raw_text)
    word_count_raw = len(raw_words)
    
    # 2. Extract HTML from docx for markdown conversion
    result_html = subprocess.run(['textutil', '-convert', 'html', '-stdout', docx_path], capture_output=True, text=True)
    if result_html.returncode != 0:
        raise RuntimeError(f"textutil html failed: {result_html.stderr}")
    html_content = result_html.stdout
    
    # 3. Process with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.find('body') or soup
    md_content = html_to_md(body)
    
    # 4. Clean consecutive empty lines
    lines = md_content.split("\n")
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False
            
    md_cleaned = "\n".join(cleaned_lines).strip()
    
    # Write output MD file
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_cleaned)
        
    # 5. Extract words from generated MD for verification
    md_words = clean_for_count(md_cleaned)
    word_count_md = len(md_words)
    
    return word_count_raw, word_count_md

def main():
    knowledge_dir = "/Users/fmillar/Proyectos_Desarrollo/TradingView/knowledge"
    files = os.listdir(knowledge_dir)
    docx_files = [f for f in files if f.endswith('.docx')]
    
    print(f"Found {len(docx_files)} DOCX files to convert.\n")
    
    report_rows = []
    
    for f in sorted(docx_files):
        docx_path = os.path.join(knowledge_dir, f)
        base_name = os.path.splitext(f)[0]
        md_filename = f"{base_name}.md"
        md_path = os.path.join(knowledge_dir, md_filename)
        
        try:
            raw_cnt, md_cnt = convert_file(docx_path, md_path)
            diff = abs(raw_cnt - md_cnt)
            diff_pct = (diff / raw_cnt * 100) if raw_cnt > 0 else 0
            # 5% threshold is highly strict and expected due to formatting boundary splits in textutil
            status = " OK" if diff_pct < 5.0 else " Check"
            
            report_rows.append({
                "file": f,
                "raw_count": raw_cnt,
                "md_count": md_cnt,
                "diff": diff,
                "diff_pct": f"{diff_pct:.2f}%",
                "status": status
            })
            print(f"Converted: '{f}' -> '{md_filename}' | Raw: {raw_cnt} | MD: {md_cnt} | Diff: {diff} ({diff_pct:.2f}%) | {status}")
        except Exception as e:
            print(f" Error converting '{f}': {e}")
            report_rows.append({
                "file": f,
                "raw_count": 0,
                "md_count": 0,
                "diff": 0,
                "diff_pct": "N/A",
                "status": f" Error: {type(e).__name__}"
            })
            
    # Print summary report table
    print("\n=================================== SUMMARY REPORT ===================================")
    print(f"{'Document File':<50} | {'Raw Words':<10} | {'MD Words':<10} | {'Diff':<6} | {'Diff %':<8} | {'Status':<8}")
    print("-" * 102)
    for row in report_rows:
        print(f"{row['file'][:50]:<50} | {row['raw_count']:<10} | {row['md_count']:<10} | {row['diff']:<6} | {row['diff_pct']:<8} | {row['status']:<8}")
    print("======================================================================================")

if __name__ == "__main__":
    main()

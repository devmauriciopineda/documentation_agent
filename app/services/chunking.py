import requests
from bs4 import BeautifulSoup


def extract_content_from_url(url):
    """Extracts content from a URL."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, and non-visible elements
    for tag in soup(
        ["script", "style", "noscript", "header", "footer", "nav", "aside"]
    ):
        tag.decompose()

    # Group elements under their closest heading
    sections = []
    current_section = None
    for elem in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "pre", "code"]
    ):
        if elem.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # New heading, create new section
            section = {
                "type": elem.name,
                "content": elem.get_text(strip=True),
                "children": [],
            }
            sections.append(section)
            current_section = section
        else:
            # Create the element dictionary
            child = {}
            if elem.name in ["ul", "ol"]:
                items = [li.get_text(strip=True) for li in elem.find_all("li")]
                if not items:
                    continue
                child["type"] = (
                    "ordered_list" if elem.name == "ol" else "unordered_list"
                )
                child["content"] = items
            elif elem.name in ["pre", "code"]:
                code_text = elem.get_text("\n", strip=True)
                if not code_text:
                    continue
                child["type"] = "code"
                child["content"] = code_to_markdown(code_text)
            else:
                text = elem.get_text(strip=True)
                if not text:
                    continue
                child["type"] = elem.name
                child["content"] = text
            # Add to the children of the closest heading
            if current_section is not None:
                current_section["children"].append(child)
            else:
                # If there is no previous heading, add as root section
                sections.append(child)

    return sections


def code_to_markdown(code_text):
    """Converts a plain text code block to markdown format."""
    return f"```\n{code_text}\n```"


def section_to_markdown(section, level=1):
    """Converts a hierarchical section to markdown text, recursively."""
    md = ""
    if section['type'] in [f'h{i}' for i in range(1, 7)]:
        hashes = '#' * int(section['type'][1])
        md += f"{hashes} {section['content']}\n\n"
    elif section['type'] == 'code':
        md += f"{section['content']}\n\n"
    elif section['type'] == 'ordered_list':
        for idx, item in enumerate(section['content'], 1):
            md += f"{idx}. {item}\n"
        md += "\n"
    elif section['type'] == 'unordered_list':
        for item in section['content']:
            md += f"- {item}\n"
        md += "\n"
    elif section['type'] == 'p':
        md += f"{section['content']}\n\n"
    else:
        md += f"{section['content']}\n\n"
    # Process children if they exist
    if 'children' in section and section['children']:
        for child in section['children']:
            md += section_to_markdown(child, level + 1)
    return md


def flatten_markdown_chunks(sections, max_length=1024):
    """
    Converts the hierarchical structure to flat chunks
    with order and content in markdown.
    """
    all_md = ""
    for section in sections:
        all_md += section_to_markdown(section)
    # Split into chunks of maximum max_length
    chunks = []
    current = ""
    for part in all_md.split('\n\n'):
        if not part.strip():
            continue
        if len(current) + len(part) + 2 > max_length:
            if current:
                chunks.append(current.strip())
            current = part + '\n\n'
        else:
            current += part + '\n\n'
    if current.strip():
        chunks.append(current.strip())
    # Create a list of dictionaries with order, content, and length
    markdown_chunks = [
        {"order": i + 1, "content": chunk, "length": len(chunk)}
        for i, chunk in enumerate(chunks)
    ]
    return markdown_chunks

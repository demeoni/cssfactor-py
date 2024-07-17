# File: css_factor.py

import re
from typing import List, Tuple, Dict

def parse_css(css: str) -> Dict[str, List[Tuple[str, str]]]:
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

    # Split the CSS into rules
    rules = re.findall(r'([^{]+)\s*{\s*([^}]+)\s*}', css)

    parsed_css = {}
    for selector, declarations in rules:
        selector = selector.strip()
        declarations = [tuple(decl.strip().split(':', 1)) for decl in declarations.split(';') if decl.strip()]
        parsed_css[selector] = declarations

    return parsed_css

def factor_css(css: Dict[str, List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, str]]]:
    # Group declarations by their values
    grouped_declarations = {}
    for selector, declarations in css.items():
        for prop, value in declarations:
            if (prop, value) not in grouped_declarations:
                grouped_declarations[(prop, value)] = []
            grouped_declarations[(prop, value)].append(selector)

    # Create new CSS with factored declarations
    factored_css = {}
    for (prop, value), selectors in grouped_declarations.items():
        new_selector = ', '.join(selectors)
        if new_selector not in factored_css:
            factored_css[new_selector] = []
        factored_css[new_selector].append((prop, value))

    return factored_css

def render_css(css: Dict[str, List[Tuple[str, str]]]) -> str:
    output = []
    for selector, declarations in css.items():
        output.append(f"{selector} {{")
        for prop, value in declarations:
            output.append(f"    {prop}: {value};")
        output.append("}")
    return '\n'.join(output)

def process_css(css_input: str, mode: str) -> str:
    parsed_css = parse_css(css_input)

    if mode == 'factor':
        processed_css = factor_css(parsed_css)
    elif mode == 'explode':
        # For simplicity, we'll just return the parsed CSS without factoring
        processed_css = parsed_css
    else:  # identity
        processed_css = parsed_css

    return render_css(processed_css)

def remove_brackets(css: str) -> str:
    # Remove any leftover { , [ , ] , } characters
    return re.sub(r'[{}\[\]]', '', css)

# Example usage
if __name__ == "__main__":
    css_input = """
    :root {
        --shared-bg-color: #F7C59F !important;
        --primary-color: #c86248 !important;
    }
    body {
        background-color: var(--shared-bg-color);
        color: var(--primary-color);
    }
    """
    result = process_css(css_input, 'factor')
    print(result)
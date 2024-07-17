import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
import argparse
import sys

@dataclass
class Stylesheet:
    charset: Optional[str]
    imports: List[Tuple[str, List[str]]]
    statements: List['Statement']

@dataclass
class Statement:
    pass

@dataclass
class Ruleset(Statement):
    selectors: List['Selector']
    declarations: List['Declaration']

@dataclass
class Media(Statement):
    media: List[str]
    statements: List[Statement]

@dataclass
class Page(Statement):
    pseudo_page: Optional[str]
    declarations: List['Declaration']

@dataclass
class Selector:
    simple_selectors: List[Tuple['SimpleSelector', 'Combinator']]

@dataclass
class SimpleSelector:
    element_name: Optional[str]
    details: List['Detail']

@dataclass
class Detail:
    pass

@dataclass
class Id(Detail):
    value: str

@dataclass
class Class(Detail):
    value: str

@dataclass
class Attrib(Detail):
    name: str

@dataclass
class AttribEq(Detail):
    name: str
    value: str

@dataclass
class AttribInc(Detail):
    name: str
    value: str

@dataclass
class AttribDM(Detail):
    name: str
    value: str

@dataclass
class Pseudo(Detail):
    value: str

@dataclass
class PseudoFunc(Detail):
    name: str
    value: str

class Combinator:
    ANCESTOR = ' '
    PRECEDED = ' + '
    PARENT = ' > '
    NO_MORE = ''

@dataclass
class Declaration:
    property: str
    values: List['Value']
    important: bool

@dataclass
class Value:
    pass

@dataclass
class Number(Value):
    value: float

@dataclass
class Percentage(Value):
    value: float

@dataclass
class Length(Value):
    value: str

@dataclass
class Ems(Value):
    value: float

@dataclass
class Exs(Value):
    value: float

@dataclass
class Angle(Value):
    value: str

@dataclass
class Time(Value):
    value: str

@dataclass
class Freq(Value):
    value: str

@dataclass
class StringV(Value):
    value: str

@dataclass
class Ident(Value):
    value: str

@dataclass
class Uri(Value):
    value: str

@dataclass
class HexColour(Value):
    value: str

@dataclass
class Slash(Value):
    pass

@dataclass
class Comma(Value):
    pass

@dataclass
class Function(Value):
    name: str
    values: List[Value]

# Tokenizer
def tokenize(css: str, progress_callback=None) -> List[Tuple[str, str]]:
    token_specification = [
        ('S',            r'[ \t\r\n\f]+'),
        ('COMMENT',      r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'),
        ('INCLUDES',     r'~='),
        ('DASHMATCH',    r'\|='),
        ('LBRACE',       r'\{'),
        ('PLUS',         r'\+'),
        ('GREATER',      r'>'),
        ('COMMA',        r','),
        ('STRING',       r'"[^"]*"|\'[^\']*\''),
        ('IDENT',        r'[-]?[_a-zA-Z][_a-zA-Z0-9-]*'),
        ('HASH',         r'#[_a-zA-Z0-9-]+'),
        ('NUMBER',       r'[-+]?[0-9]*\.?[0-9]+'),
        ('PERCENTAGE',   r'[-+]?[0-9]*\.?[0-9]+%'),
        ('LENGTH',       r'[-+]?[0-9]*\.?[0-9]+(?:em|ex|px|cm|mm|in|pt|pc)'),
        ('ANGLE',        r'[-+]?[0-9]*\.?[0-9]+(?:deg|rad|grad)'),
        ('TIME',         r'[-+]?[0-9]*\.?[0-9]+(?:ms|s)'),
        ('FREQ',         r'[-+]?[0-9]*\.?[0-9]+(?:Hz|kHz)'),
        ('IMPORTANT',    r'!important'),
        ('COLON',        r':'),
        ('SEMICOLON',    r';'),
        ('RBRACE',       r'}'),
        ('LPAREN',       r'\('),
        ('RPAREN',       r'\)'),
        ('LBRACKET',     r'\['),
        ('RBRACKET',     r'\]'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    tokens = []
    for i, mo in enumerate(re.finditer(tok_regex, css)):
        kind = mo.lastgroup
        value = mo.group()
        if kind != 'COMMENT':  # Skip comments
            tokens.append((kind, value))
        if progress_callback:
            progress_callback(int((i + 1) / len(css) * 100))
    return tokens

# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.progress_callback = None
        self.max_iterations = 10000  # Safeguard against infinite loops

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def parse(self) -> Stylesheet:
        try:
            self.log("Starting to parse charset")
            charset = self.parse_charset()
            self.log(f"Parsed charset: {charset}")

            self.log("Starting to parse imports")
            imports = self.parse_imports()
            self.log(f"Parsed imports: {imports}")

            self.log("Starting to parse statements")
            statements = self.parse_statements()
            self.log(f"Parsed {len(statements)} statements")

            return Stylesheet(charset, imports or [], statements or [])
        except Exception as e:
            error_msg = f"Error during parsing: {str(e)}"
            self.errors.append(error_msg)
            self.log(error_msg)
            return Stylesheet(None, [], [])

    def parse_charset(self) -> Optional[str]:
        if self.match('IDENT', 'charset'):
            self.consume('S')
            if self.match('STRING'):
                charset = self.previous()[1]
                self.consume('SEMICOLON')
                return charset
        return None


    def parse_imports(self) -> List[Tuple[str, List[str]]]:
        imports = []
        while self.match('IDENT', 'import'):
            self.consume('S')
            if self.match('STRING', 'URI'):
                url = self.previous()[1]
                media = []
                if self.match('IDENT'):
                    media = [self.previous()[1]]
                    while self.match('COMMA'):
                        self.consume('S')
                        if self.match('IDENT'):
                            media.append(self.previous()[1])
                self.consume('SEMICOLON')
                imports.append((url, media))
        return imports

    def parse_statements(self) -> List[Statement]:
        statements = []
        while not self.is_at_end():
            self.log(f"Parsing statement at position {self.current}")
            if self.match('IDENT', 'media'):
                statements.append(self.parse_media())
            elif self.match('IDENT', 'page'):
                statements.append(self.parse_page())
            else:
                try:
                    statements.append(self.parse_ruleset())
                except Exception as e:
                    self.log(f"Error parsing ruleset: {str(e)}")
                    self.synchronize()
            if self.progress_callback:
                self.progress_callback(self.current)
        return statements

    def parse_media(self) -> Media:
        self.consume('S')
        media = [self.consume('IDENT')[1]]
        while self.match('COMMA'):
            self.consume('S')
            media.append(self.consume('IDENT')[1])
        self.consume('LBRACE')
        statements = []
        while not self.match('RBRACE'):
            statements.append(self.parse_ruleset())
        return Media(media, statements)

    def parse_page(self) -> Page:
        self.consume('S')
        pseudo_page = None
        if self.match('COLON'):
            pseudo_page = self.consume('IDENT')[1]
        self.consume('LBRACE')
        declarations = self.parse_declarations()
        self.consume('RBRACE')
        return Page(pseudo_page, declarations)

    def parse_ruleset(self) -> Ruleset:
        selectors = self.parse_selectors()
        self.consume('LBRACE')
        declarations = self.parse_declarations()
        self.consume('RBRACE')
        return Ruleset(selectors, declarations)

    def parse_selectors(self) -> List[Selector]:
        selectors = [self.parse_selector()]
        while self.match('COMMA'):
            self.consume('S')
            selectors.append(self.parse_selector())
        return selectors

    def parse_selector(self) -> Selector:
        simple_selectors = []
        simple_selectors.append((self.parse_simple_selector(), self.parse_combinator()))
        while not self.check('COMMA') and not self.check('LBRACE'):
            simple_selectors.append((self.parse_simple_selector(), self.parse_combinator()))
        return Selector(simple_selectors)

    def parse_simple_selector(self) -> SimpleSelector:
        element_name = None
        details = []
        if self.match('IDENT'):
            element_name = self.previous()[1]
        elif self.match('ASTERISK'):
            element_name = '*'

        while self.match('HASH', 'DOT', 'LBRACKET', 'COLON'):
            if self.previous()[0] == 'HASH':
                details.append(Id(self.previous()[1]))
            elif self.previous()[0] == 'DOT':
                details.append(Class(self.consume('IDENT')[1]))
            elif self.previous()[0] == 'LBRACKET':
                details.append(self.parse_attribute())
            elif self.previous()[0] == 'COLON':
                details.append(self.parse_pseudo())

        return SimpleSelector(element_name, details)

    def parse_attribute(self) -> Detail:
        name = self.consume('IDENT')[1]
        if self.match('RBRACKET'):
            return Attrib(name)
        elif self.match('EQUALS'):
            value = self.consume('STRING', 'IDENT')[1]
            self.consume('RBRACKET')
            return AttribEq(name, value)
        elif self.match('INCLUDES'):
            value = self.consume('STRING', 'IDENT')[1]
            self.consume('RBRACKET')
            return AttribInc(name, value)
        elif self.match('DASHMATCH'):
            value = self.consume('STRING', 'IDENT')[1]
            self.consume('RBRACKET')
            return AttribDM(name, value)

    def parse_pseudo(self) -> Detail:
        if self.match('IDENT'):
            return Pseudo(self.previous()[1])
        elif self.match('FUNCTION'):
            name = self.previous()[1]
            self.consume('S')
            if self.match('IDENT'):
                value = self.previous()[1]
            else:
                value = ''
            self.consume('RPAREN')
            return PseudoFunc(name, value)

    def parse_combinator(self) -> str:
        if self.match('S'):
            return Combinator.ANCESTOR
        elif self.match('PLUS'):
            self.consume('S')
            return Combinator.PRECEDED
        elif self.match('GREATER'):
            self.consume('S')
            return Combinator.PARENT
        else:
            return Combinator.NO_MORE

    def parse_declarations(self) -> List[Declaration]:
        declarations = []
        while not self.check('RBRACE'):
            try:
                self.consume_whitespace()
                if self.check('RBRACE'):  # Check again after consuming whitespace
                    break
                property = self.consume('IDENT')[1]
                self.consume_whitespace()
                self.consume('COLON')
                self.consume_whitespace()
                values = self.parse_values()
                important = False
                if self.match('IMPORTANT'):
                    important = True
                declarations.append(Declaration(property, values, important))
                self.consume_whitespace()
                if not self.match('SEMICOLON'):
                    break
                self.consume_whitespace()
            except Exception as e:
                self.errors.append(f"Error parsing declaration: {str(e)}")
                self.synchronize()
        return declarations

    def synchronize(self):
        while not self.is_at_end():
            if self.previous()[0] == 'SEMICOLON':
                return
            if self.check('RBRACE'):
                return
            self.advance()

    def consume(self, *types):
        for type in types:
            if self.check(type):
                return self.advance()
        error_msg = f"Expected {types}, found {self.peek()[0]}"
        self.errors.append(error_msg)
        raise Exception(error_msg)

    def log(self, message):
        print(f"Parser: {message}", file=sys.stderr)
        self.errors.append(message)

    # whitespace remover
    def consume_whitespace(self):
        while self.match('S'):
            pass

    def parse_values(self) -> List[Value]:
        values = []
        while not self.check('IMPORTANT') and not self.check('SEMICOLON') and not self.check('RBRACE'):
            if self.match('NUMBER'):
                values.append(Number(float(self.previous()[1])))
            elif self.match('PERCENTAGE'):
                values.append(Percentage(float(self.previous()[1][:-1])))
            elif self.match('LENGTH'):
                values.append(Length(self.previous()[1]))
            elif self.match('EMS'):
                values.append(Ems(float(self.previous()[1][:-2])))
            elif self.match('EXS'):
                values.append(Exs(float(self.previous()[1][:-2])))
            elif self.match('ANGLE'):
                values.append(Angle(self.previous()[1]))
            elif self.match('TIME'):
                values.append(Time(self.previous()[1]))
            elif self.match('FREQ'):
                values.append(Freq(self.previous()[1]))
            elif self.match('STRING'):
                values.append(StringV(self.previous()[1]))
            elif self.match('IDENT'):
                values.append(Ident(self.previous()[1]))
            elif self.match('URI'):
                values.append(Uri(self.previous()[1]))
            elif self.match('HASH'):
                values.append(HexColour(self.previous()[1]))
            elif self.match('SLASH'):
                values.append(Slash())
            elif self.match('COMMA'):
                values.append(Comma())
            elif self.match('FUNCTION'):
                name = self.previous()[1]
                self.consume('S')
                function_values = self.parse_values()
                self.consume('RPAREN')
                values.append(Function(name, function_values))
            else:
                self.errors.append(f"Unexpected token in value: {self.peek()[0]}")
                self.advance()  # Skip the unexpected token
            self.consume_whitespace()
        return values

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek()[0] == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.current >= len(self.tokens)

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

def factor_css(stylesheet: Stylesheet, progress_callback=None) -> Stylesheet:
    factored_statements = []
    total_statements = len(stylesheet.statements) if stylesheet.statements is not None else 0
    for i, statement in enumerate(stylesheet.statements or []):
        if isinstance(statement, Ruleset):
            factored_statements.extend(factor_ruleset(statement))
        elif isinstance(statement, Media):
            factored_media = Media(statement.media, factor_css(Stylesheet(None, [], statement.statements)).statements)
            factored_statements.append(factored_media)
        else:
            factored_statements.append(statement)
        if progress_callback:
            progress_callback(int((i + 1) / total_statements * 100) if total_statements > 0 else 100)
    return Stylesheet(stylesheet.charset, stylesheet.imports, factored_statements)

def factor_ruleset(ruleset: Ruleset) -> List[Ruleset]:
    # Split ruleset into individual declarations
    split_rulesets = []
    for selector in ruleset.selectors:
        for declaration in ruleset.declarations:
            split_rulesets.append(Ruleset([selector], [declaration]))

    # Sort split rulesets by selector and then by declaration
    split_rulesets.sort(key=lambda r: (str(r.selectors[0]), str(r.declarations[0])))

    # Group rulesets with the same selector
    grouped_rulesets = []
    current_group = []
    for ruleset in split_rulesets:
        if not current_group or str(ruleset.selectors[0]) == str(current_group[0].selectors[0]):
            current_group.append(ruleset)
        else:
            grouped_rulesets.append(Ruleset(current_group[0].selectors, [r.declarations[0] for r in current_group]))
            current_group = [ruleset]
    if current_group:
        grouped_rulesets.append(Ruleset(current_group[0].selectors, [r.declarations[0] for r in current_group]))

    return grouped_rulesets

def render_stylesheet(stylesheet: Stylesheet) -> str:
    output = []
    if stylesheet.charset:
        output.append(f'@charset {stylesheet.charset};')
    if stylesheet.imports:
        for url, media in stylesheet.imports:
            output.append(f'@import {url} {" ".join(media)};')
    if stylesheet.statements:
        for statement in stylesheet.statements:
            output.append(render_statement(statement))
    return '\n'.join(output)

def render_statement(statement: Statement) -> str:
    if isinstance(statement, Ruleset):
        selectors = ', '.join(render_selector(selector) for selector in statement.selectors)
        declarations = '; '.join(render_declaration(decl) for decl in statement.declarations)
        return f'{selectors} {{ {declarations} }}'
    elif isinstance(statement, Media):
        return f'@media {", ".join(statement.media)} {{ {"; ".join(render_statement(s) for s in statement.statements)} }}'
    elif isinstance(statement, Page):
        pseudo = f':{statement.pseudo_page}' if statement.pseudo_page else ''
        declarations = '; '.join(render_declaration(decl) for decl in statement.declarations)
        return f'@page{pseudo} {{ {declarations} }}'

def render_selector(selector: Selector) -> str:
    return ''.join(f'{render_simple_selector(ss)}{combinator}' for ss, combinator in selector.simple_selectors)

def render_simple_selector(simple_selector: SimpleSelector) -> str:
    element = simple_selector.element_name or ''
    details = ''.join(render_detail(detail) for detail in simple_selector.details)
    return f'{element}{details}'

def render_detail(detail: Detail) -> str:
    if isinstance(detail, Id):
        return f'#{detail.value}'
    elif isinstance(detail, Class):
        return f'.{detail.value}'
    elif isinstance(detail, Attrib):
        return f'[{detail.name}]'
    elif isinstance(detail, AttribEq):
        return f'[{detail.name}="{detail.value}"]'
    elif isinstance(detail, AttribInc):
        return f'[{detail.name}~="{detail.value}"]'
    elif isinstance(detail, AttribDM):
        return f'[{detail.name}|="{detail.value}"]'
    elif isinstance(detail, Pseudo):
        return f':{detail.value}'
    elif isinstance(detail, PseudoFunc):
        return f':{detail.name}({detail.value})'

def render_declaration(declaration: Declaration) -> str:
    values = ' '.join(render_value(value) for value in declaration.values)
    important = ' !important' if declaration.important else ''
    return f'{declaration.property}: {values}{important}'

def render_value(value: Value) -> str:
    if isinstance(value, Number):
        return str(value.value)
    elif isinstance(value, Percentage):
        return f'{value.value}%'
    elif isinstance(value, Length):
        return value.value
    elif isinstance(value, Ems):
        return f'{value.value}em'
    elif isinstance(value, Exs):
        return f'{value.value}ex'
    elif isinstance(value, Angle):
        return value.value
    elif isinstance(value, Time):
        return value.value
    elif isinstance(value, Freq):
        return value.value
    elif isinstance(value, StringV):
        return value.value
    elif isinstance(value, Ident):
        return value.value
    elif isinstance(value, Uri):
        return value.value
    elif isinstance(value, HexColour):
        return value.value
    elif isinstance(value, Slash):
        return '/'
    elif isinstance(value, Comma):
        return ','
    elif isinstance(value, Function):
        values = ' '.join(render_value(v) for v in value.values)
        return f'{value.name}({values})'

def explode_css(stylesheet: Stylesheet, progress_callback=None) -> Stylesheet:
    exploded_statements = []
    total_statements = len(stylesheet.statements)
    for i, statement in enumerate(stylesheet.statements):
        if isinstance(statement, Ruleset):
            exploded_statements.extend(explode_ruleset(statement))
        elif isinstance(statement, Media):
            exploded_media = Media(statement.media, explode_css(Stylesheet(None, [], statement.statements)).statements)
            exploded_statements.append(exploded_media)
        else:
            exploded_statements.append(statement)
        if progress_callback:
            progress_callback(int((i + 1) / total_statements * 100))
    return Stylesheet(stylesheet.charset, stylesheet.imports, exploded_statements)

def explode_ruleset(ruleset: Ruleset) -> List[Ruleset]:
    exploded_rulesets = []
    for selector in ruleset.selectors:
        for declaration in ruleset.declarations:
            exploded_rulesets.append(Ruleset([selector], [declaration]))
    return exploded_rulesets

def main():
    parser = argparse.ArgumentParser(description='Factor CSS stylesheets.')
    parser.add_argument('--mode', choices=['factor', 'explode', 'identity'], default='factor',
                        help='Processing mode (default: factor)')
    args = parser.parse_args()

    css_input = sys.stdin.read()
    tokens = list(tokenize(css_input))
    css_parser = Parser(tokens)
    stylesheet = css_parser.parse()

    print("Parsing errors:", file=sys.stderr)
    for error in css_parser.errors:
        print(error, file=sys.stderr)

    if args.mode == 'factor':
        factored_stylesheet = factor_css(stylesheet)
        print(render_stylesheet(factored_stylesheet))
    elif args.mode == 'explode':
        exploded_stylesheet = explode_css(stylesheet)
        print(render_stylesheet(exploded_stylesheet))
    elif args.mode == 'identity':
        print(render_stylesheet(stylesheet))

if __name__ == "__main__":
    main()
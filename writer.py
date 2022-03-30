import html
import io
import re
from typing import List, Text

from more_itertools import peekable
from pandoc.types import *

COMPLETE_TOKEN = '\u2612'
INCOMPLETE_TOKEN = '\u2610'

code_block_template = """
<ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="5fb808ca-6a39-4ae5-943e-3b42b3a504fc">
    <ac:plain-text-body>
        <![CDATA[{text}]]>
    </ac:plain-text-body>
</ac:structured-macro>'
"""


def escape_text(text: Text):
    return html.escape(text)


def is_task_action(block):
    match block:
        case Plain([Str('\u2612'), Space(), *_]):
            return True
        case Plain([Str('\u2610'), Space(), *_]):
            return True
        case _:
            return False


def is_task_item(blocks):
    return all(is_task_action(block) or is_task_list(block) for block in blocks)


def is_task_list(block):
    match block:
        case BulletList(blocks_list):
            return all(is_task_item(blocks) for blocks in blocks_list)
        case _:
            return False


def unpack_target(target):
    match target:
        case (url, title):
            return escape_text(url), escape_text(title)
        case _:
            raise AssertionError(f"Not Target: {target}")


class Parser:

    def __init__(self):
        self._buffer = io.StringIO()

    def do_pandoc(self, doc):
        match doc:
            case Pandoc(meta, blocks):
                # TODO: meta
                for block in blocks:
                    self.do_block(block)
            case _:
                raise AssertionError(f"Not Pandoc: {doc}")

    def do_inlines(self, inlines: List[Inline]):
        for inline in inlines:
            self.do_inline(inline)

    def do_inline(self, el: Inline):

        match el:
            case Str(text):
                self._buffer.write(escape_text(text))
            case Emph(inlines):
                self._buffer.write("<em>")
                self.do_inlines(inlines)
                self._buffer.write("</em>")
            case Underline(inlines):
                self._buffer.write("<u>")
                self.do_inlines(inlines)
                self._buffer.write("</u>")
            case Strong(inlines):
                self._buffer.write("<strong>")
                self.do_inlines(inlines)
                self._buffer.write("</strong>")
            case Strikeout(inlines):
                self._buffer.write('<span style="text-decoration: line-through;">')
                self.do_inlines(inlines)
                self._buffer.write("</span>")
            case Superscript(inlines):
                self._buffer.write("<sup>")
                self.do_inlines(inlines)
                self._buffer.write("</sup>")
            case Subscript(inlines):
                self._buffer.write("<sub>")
                self.do_inlines(inlines)
                self._buffer.write("</sub>")
            case SmallCaps(inlines):
                raise AssertionError(f"SmallCaps: {el}")
            case Quoted(quote_type, inlines):
                match quote_type:
                    case DoubleQuote():
                        self._buffer.write("&ldquo;")
                        self.do_inlines(inlines)
                        self._buffer.write("&rdquo;")
                    case SingleQuote():
                        self._buffer.write("&lsquo;")
                        self.do_inlines(inlines)
                        self._buffer.write("&rsquo;")
                    case _:
                        raise Exception(f"Quoted: {el}")
            case Cite(citations, inlines):
                self.do_inlines(inlines)
            case Code(attr, text):
                self._buffer.write("<code>")
                self._buffer.write(escape_text(text))
                self._buffer.write("</code>")
            case Space():
                self._buffer.write(" ")
            case SoftBreak():
                self._buffer.write(" ")
            case LineBreak():
                self._buffer.write("<br />")
            case Math(math_type, text):
                raise Exception(f"Math: {el}")
            case RawInline(format, text):
                if format != Format("html"):
                    raise AssertionError(f"RawInline {el}")
                self._buffer.write(escape_text(text))
            case Link(attr, inlines, target):
                # TODO: alt-text
                url, title = unpack_target(target)
                if title != "":
                    raise AssertionError(el)
                self._buffer.write(f'<a href="{url}">')
                self.do_inlines(inlines)
                self._buffer.write("</a>")
            case Image(attr, inlines, target):
                # TODO: alt-text
                self._buffer.write("<ac:image>")
                url, _ = unpack_target(target)
                self._buffer.write(f'<ri:url ri:value="{url}"/>')
                self._buffer.write("</ac:image>")
            case Note(blocks):
                raise AssertionError(f"Note: {el}")
            case Span(attr, inlines):
                raise AssertionError(f"Span: {el}")
            case _:
                raise AssertionError(f"Not Inline: {el}")

    def do_para(self, el):
        match el:
            # Paper use **text** for level 3 header.
            case Para([Strong(inlines)]):
                self._buffer.write("<h3>")
                self.do_inlines(inlines)
                self._buffer.write("</h3>\n")
            case Para(inlines):
                self._buffer.write("<p>")
                self.do_inlines(inlines)
                self._buffer.write("</p>")
            case _:
                raise AssertionError(f"unexpected Para: {el}")

    def do_block(self, el: Block):

        match el:
            case Plain(inlines):
                self.do_inlines(inlines)
            case Para(_):
                self.do_para(el)
            case LineBlock(inlines_list):
                self._buffer.write("<p>")
                for inlines in inlines_list:
                    self.do_inlines(inlines)
                self._buffer.write("</p>\n")
            case CodeBlock(attr, text):
                self._buffer.write(code_block_template.format(text=text))
            case RawBlock(format, text):
                raise AssertionError(f"RawBlock: {el}")
            case BlockQuote(blocks):
                self._buffer.write("<blockquote>\n")
                for block in blocks:
                    self.do_block(block)
                self._buffer.write("</blockquote>\n")
            case OrderedList(_, blocks_list):
                self._buffer.write("<ol>\n")
                for blocks in blocks_list:
                    self._buffer.write("<li>")
                    for block in blocks:
                        self.do_block(block)
                    self._buffer.write("</li>\n")
                self._buffer.write("</ol>\n")
            case BulletList(list_blocks):
                if is_task_list(el):
                    self.do_task_list(el)
                else:
                    self._buffer.write("<ul>\n")
                    for blocks in list_blocks:
                        self._buffer.write("<li>")
                        for block in blocks:
                            self.do_block(block)
                        self._buffer.write("</li>\n")
                    self._buffer.write("</ul>\n")
            case DefinitionList(_):
                raise AssertionError(f"DefinitionList: {el}")
            case Header(level, attr, inlines):
                self._buffer.write(f"<h{level}>")
                self.do_inlines(inlines)
                self._buffer.write(f"</h{level}>\n")
            case HorizontalRule():
                self._buffer.write("<hr />\n")
            case Table(attr, caption, col_specs, table_head, table_bodies, table_foot):
                self._buffer.write("<table>\n")
                self.do_table_head(table_head)
                for table_body in table_bodies:
                    self.do_table_body(table_body)
                self._buffer.write("</table>\n")
            case Div(attr, blocks):
                raise AssertionError(f"Div: {el}")
            case Null():
                raise AssertionError(f"Null: {el}")
            case _:
                raise AssertionError(f"unexpected element {el}")

    """
    task_list = [task_item]
    task_item = [task_action | task_list]
    task_action = "- [ ] ..." | "- [x] ..."
    """

    def do_task_action(self, block):

        """
        <ac:task-status>incomplete</ac:task-status>
        <ac:task-body>task list item</ac:task-body>
        """

        match block:
            case Plain([Str('\u2610'), Space(), *rest]):
                self._buffer.write("<ac:task>\n")
                self._buffer.write("<ac:task-status>incomplete</ac:task-status>\n")
                self._buffer.write("<ac:task-body>")
                self.do_inlines(rest)
                self._buffer.write("</ac:task-body>\n")
                self._buffer.write("</ac:task>\n")
            case Plain([Str('\u2612'), Space(), *rest]):
                self._buffer.write("<ac:task>\n")
                self._buffer.write("<ac:task-status>complete</ac:task-status>\n")
                self._buffer.write("<ac:task-body>")
                self.do_inlines(rest)
                self._buffer.write("</ac:task-body>\n")
                self._buffer.write("</ac:task>\n")
            case _:
                raise AssertionError(f"{block} is not a task item")

    def do_task_item(self, blocks):
        for block in blocks:
            if is_task_action(block):
                self.do_task_action(block)
            elif is_task_list(block):
                self.do_task_list(block)
            else:
                raise AssertionError("Not task item: {blocks}")

    def do_task_list(self, block):

        match block:
            case BulletList(blocks_list):
                self._buffer.write("<ac:task-list>")
                for blocks in blocks_list:
                    self.do_task_item(blocks)
                self._buffer.write("</ac:task-list>\n")
            case _:
                raise AssertionError(f"{block} is not a task list")

    def do_table_head(self, table_head: TableHead):
        match table_head:
            case TableHead(attr, rows):
                if len(rows) > 1:
                    raise AssertionError(f"more than one rows in TableHead: {rows}")
                if len(rows) == 0:
                    return
                row = rows[0]
                self.do_row(row, is_header=True)
            case _:
                raise AssertionError(f"{table_head} is not TableHead")

    def do_table_body(self, table_body: TableBody):
        match table_body:
            case TableBody(attr, row_head_columns, headers, rows):
                for row in rows:
                    self.do_row(row, is_header=False)
            case _:
                raise AssertionError(f"{table_body} is not TableBody")

    def do_row(self, row: Row, is_header: bool):
        match row:
            case Row(attr, cells):
                self._buffer.write("<tr>")
                for cell in cells:
                    self._buffer.write("<th>" if is_header else "<td>")
                    self.do_cell(cell)
                    self._buffer.write("</th>" if is_header else "</td>")
                self._buffer.write("</tr>")
            case _:
                return AssertionError(f"not a Row: {row}")

    def do_cell(self, cell: Cell):
        match cell:
            case Cell(attr, alignment, row_span, col_span, blocks):
                for block in blocks:
                    self.do_table_block(block)
            case _:
                return AssertionError(f"not a Cell: {cell}")

    def do_table_block(self, el: Block):
        match el:
            case Plain(inlines):
                groups = split_br(inlines)
                if is_table_task_list(groups):
                    bullet_list = convert_bullet_list(peekable(groups), 0)
                    self.do_block(bullet_list)
                else:
                    for group in groups:
                        self.do_block(Para(group))
            case _:
                self.do_block(el)


def split_br(inlines: List[Inline]):
    groups = []
    group = []
    for el in inlines:
        if el == RawInline(Format("html"), "<br>"):
            groups.append(group)
            group = []
        else:
            group.append(el)
    if group:
        groups.append(group)

    return groups


def is_table_task_list(groups: List[List[Inline]]):
    return groups and all(is_table_task_item(group) for group in groups)


def is_table_task_item(inlines: List[Inline]) -> bool:
    match inlines:
        case [Str("-"), Space(), *_]:
            return True
        case [Space(), Str("-"), Space(), *_]:
            return True
        case _:
            return False


def convert_bullet_list(groups, level):
    list_blocks = []
    while True:
        group = groups.peek(None)
        if group is None:
            return BulletList(list_blocks)

        if level == 0:
            match group:
                case [Str("-"), Space(), *rest]:
                    list_blocks.append([Plain(rest)])
                    next(groups)
                case [Space(), Str("-"), Space(), *rest]:
                    bullet_list = convert_bullet_list(groups, 1)
                    list_blocks[-1].append(bullet_list)
                case _:
                    raise AssertionError(f"{group}")

        elif level == 1:
            match group:
                case [Str("-"), Space(), *_]:
                    return BulletList(list_blocks)
                case [Space(), Str("-"), Space(), *rest]:
                    next(groups)
                    list_blocks.append([Plain(rest)])
                case _:
                    raise AssertionError(f"{group}")

    return BulletList(list_blocks)


def convert_page(path: str) -> str:
    with open(path) as f:
        content = f.read()

    # replace [ ] with - [ ]
    regex1 = re.compile(r"^(\s*)\[ \]( .+)$", flags=re.MULTILINE)
    content = regex1.sub(r"\1- [ ]\2", content)
    # replace [x] with - [x]
    regex2 = re.compile(r"^(\s*)\[x\]( .+)$", flags=re.MULTILINE)
    content = regex2.sub(r"\1- [x]\2", content)
    # append new line after ^----------$
    regex3 = re.compile(r"^----------$", flags=re.MULTILINE)
    content = regex3.sub("----------\n", content)

    doc = pandoc.read(source=content, format="markdown-raw_tex-tex_math_dollars")
    parser = Parser()
    parser.do_pandoc(doc)
    return parser._buffer.getvalue()


if __name__ == "__main__":
    print(convert_page(
        "/Users/zhangfan/src/python/paper2conf/out/Infrastructure/Persistent " "Systems/Teams/Metadata Services/Edgestore/Onboarding/Diffing In The " "Edgestore Clients.paper"))

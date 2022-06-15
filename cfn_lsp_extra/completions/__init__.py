"""
Completion logic.
"""
from typing import List

from pygls.lsp.types.basic_structures import Position
from pygls.lsp.types.language_features.completion import CompletionItem
from pygls.lsp.types.language_features.completion import CompletionList
from pygls.lsp.types.language_features.completion import InsertTextFormat
from pygls.workspace import Document

from cfn_lsp_extra.decode.extractors import ResourcePropertyExtractor

from ..aws_data import AWSContext
from ..aws_data import AWSPropertyName
from ..aws_data import AWSResourceName
from ..aws_data import Tree
from ..decode.extractors import ResourceExtractor
from .functions import intrinsic_function_completions


def completions_for(
    template_data: Tree, aws_context: AWSContext, document: Document, position: Position
) -> CompletionList:
    """Return a list of completion items for the user's position in document."""
    line, char = position.line, position.character
    resource_lookup = ResourceExtractor().extract(template_data)
    res_span = resource_lookup.at(line, char)
    if res_span:
        return resource_completions(res_span.value, aws_context, document.lines, line)
    prop_lookup = ResourcePropertyExtractor().extract(template_data)
    prop_span = prop_lookup.at(line, char)
    if prop_span:
        return property_completions(prop_span.value, aws_context)
    return intrinsic_function_completions(document, position)


def property_completions(
    name: AWSPropertyName, aws_context: AWSContext
) -> CompletionList:
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=s, documentation=aws_context.description(name.parent / s)
            )
            for s in aws_context.same_level(name)
        ],
    )


def resource_completions(
    name: AWSResourceName,
    aws_context: AWSContext,
    document_lines: List[str],
    current_line: int,
) -> CompletionList:
    split = name.value.split("::")
    if len(split) <= 1:
        items = [
            CompletionItem(label=res, insert_text=res + "::")
            for res in aws_context.resource_prefixes()
        ]
    else:
        use_snippet = (
            current_line == len(document_lines) - 1
            or not document_lines[current_line + 1].strip()
        )
        items = [
            CompletionItem(
                label=s,
                documentation=aws_context.description(name.parent / s),
                insert_text=s.rsplit("::", 1)[-1]
                + (
                    "\n" + resource_snippet(AWSResourceName(value=s), aws_context)
                    if use_snippet
                    else ""
                ),
                insert_text_format=InsertTextFormat.Snippet if use_snippet else None,
            )
            for s in aws_context.same_level(name)
            if s.startswith("::".join(split[:-1]))
        ]
    return CompletionList(is_incomplete=False, items=items)


def resource_snippet(name: AWSResourceName, aws_context: AWSContext) -> str:
    props = "Properties:\n"
    required_props = (
        p for p, v in aws_context[name]["properties"].items() if v["required"]
    )
    for idx, prop in enumerate(required_props):
        props += f"\t{prop}: ${idx + 1}\n"
    # $0 defines the final tab stop
    return props + "\t$0"

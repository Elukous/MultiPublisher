import mistune


# Mistune 3.x: use the dedicated AST renderer mode
_md_ast = mistune.create_markdown(renderer='ast')


def parse_markdown(md_text: str) -> list[dict]:
    """Parse markdown text into mistune AST (list of token dicts).

    Each token has 'type' (heading, paragraph, block_code, list, etc.)
    and 'children' for nested content.

    Args:
        md_text: Raw markdown string.

    Returns:
        List of AST token dicts from mistune.
    """
    return _md_ast(md_text)

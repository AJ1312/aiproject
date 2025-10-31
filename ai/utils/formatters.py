"""Output formatting utilities for non-API features."""
import re


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(text: str) -> None:
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print('─' * 80)


def print_result(text: str) -> None:
    """Print a result line."""
    print(f"  {text}")


def format_percentage(value: float) -> str:
    """Format a percentage value."""
    return f"{value:.2f}%"


def format_table_row(columns: list, widths: list) -> str:
    """Format a table row with specified column widths."""
    return " | ".join(str(col).ljust(width) for col, width in zip(columns, widths))


def print_box(title: str, lines: list) -> None:
    """Print content in a box."""
    max_width = max(len(line) for line in [title] + lines)
    border = "═" * (max_width + 4)
    
    print(f"╔{border}╗")
    print(f"║  {title.ljust(max_width)}  ║")
    print(f"╠{border}╣")
    for line in lines:
        print(f"║  {line.ljust(max_width)}  ║")
    print(f"╚{border}╝")


def clean_gemini_output(text: str) -> str:
    """Sanitize Gemini/LLM text output:

    - Replace long runs of asterisks (***, ****, ...) with a single em-dash divider
    - Remove lines that consist only of separators (asterisks, dashes, underscores)
    - Collapse repeated divider lines
    - Trim leading/trailing whitespace
    """
    if not text:
        return text

    # Replace sequences of 3+ asterisks with a single em-dash marker
    text = re.sub(r"\*{3,}", "—", text)

    # Remove lines that are only separators like --- or *** or ___ (2 or more)
    lines = [ln for ln in text.splitlines() if not re.match(r"^\s*([*_\-]){2,}\s*$", ln)]

    # Collapse consecutive em-dash-only lines
    cleaned = []
    prev_div = False
    for ln in lines:
        is_div = bool(re.match(r"^\s*—+\s*$", ln))
        if is_div and prev_div:
            continue
        cleaned.append(ln)
        prev_div = is_div

    return "\n".join(cleaned).strip()


__all__ = [
    "print_header",
    "print_section",
    "print_result",
    "format_percentage",
    "format_table_row",
    "print_box",
    "clean_gemini_output",
]

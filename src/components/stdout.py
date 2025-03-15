CURSOR_UP = "\033[A"
CLEAR_FROM_CURSOR = "\033[0K"
CLEAR_LINE = "\033[2K"


def cli_unprint(lines: int = 1, force_final_clear: bool = False):
    """
    Clears as many lines in the terminal as the provided argument 'lines',
    and returns the cursor to the beginning of the cleared lines
    """
    print(f"{CLEAR_FROM_CURSOR}{CURSOR_UP}" * lines)

    if force_final_clear:
        print(CLEAR_LINE)

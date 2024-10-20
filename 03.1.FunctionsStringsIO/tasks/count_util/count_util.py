def count_util(text: str, flags: str | None = None) -> dict[str, int]:
    """
    :param text: text to count entities
    :param flags: flags in command-like format - can be:
        * -m stands for counting characters
        * -l stands for counting lines
        * -L stands for getting length of the longest line
        * -w stands for counting words
    More than one flag can be passed at the same time, for example:
        * "-l -m"
        * "-lLw"
    Ommiting flags or passing empty string is equivalent to "-mlLw"
    :return: mapping from string keys to corresponding counter, where
    keys are selected according to the received flags:
        * "chars" - amount of characters
        * "lines" - amount of lines
        * "longest_line" - the longest line length
        * "words" - amount of words
    """
    if not flags or flags.strip() == '':
        flags = 'mlLw'

    result: dict[str, int] = {}

    count_chars = 'm' in flags
    count_lines = 'l' in flags
    count_longest_line = 'L' in flags
    count_words = 'w' in flags

    if count_chars:
        result['chars'] = len(text)

    lines = text.splitlines()
    if count_lines:
        result['lines'] = len(text.split('\n')) - 1

    if count_longest_line:
        longest_line_length = max(len(line) for line in lines) if lines else 0
        result['longest_line'] = longest_line_length

    if count_words:
        words = text.split()
        result['words'] = len(words)

    return result

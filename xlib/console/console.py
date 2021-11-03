from typing import Generator

_progress_symbols = "|/-\\"

def progress_bar_iterator(iterable, count : int = None, desc = '', suppress_print=False) -> Generator:
    if count is None:
        count = len(iterable)
    if not suppress_print:
        progress_bar_print(0, count, desc)
    for i, item in enumerate(iterable):
        yield item
        if not suppress_print:
            progress_bar_print(i + 1, count, desc)

def progress_bar_print(n, n_count, desc = ''):
    str_max_len = 80

    prefix_str = f'{desc} |'
    prefix_str_len = len(prefix_str)

    suffix_str = f'| {n}/{n_count}'
    bar_len = str_max_len - (prefix_str_len+len(suffix_str))

    bar_head = '#'*int( (n/ max(1,n_count) )*bar_len)
    if n != n_count:
        bar_head += _progress_symbols[n % len(_progress_symbols)]
    bar_tail = '-'*( bar_len - len(bar_head) )

    out = prefix_str + bar_head + bar_tail + suffix_str
    print(out, end = '\r')
    if n == n_count:
        print()
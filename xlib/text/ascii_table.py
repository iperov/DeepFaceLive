import re
from typing import Union, List
_opts_halign = {'l':0,'c':1,'r':2}
_opts_valign = {'t':0,'m':1,'b':2}

"""
test = [
            '|c99 TABLE NAME',
            '|3 3-span left align\n multiline row |rb2 2-span right bottom align',
            '|c WWWWWWWWWW |c WWWWWWWWWW |c WWWWWWWWWW |c WWWWWWWWWW |c WWWWWWWWWW',
            '|c3 center aligned 3-span |r2 2-span right align',
            '|r 0 |c3 Center align\nmulti\nline\nrow |l 1.00',
            '|r 1 |r3 Right align\nmulti\nline\nrow |l 1.00',
            '| ? | s',
            '| ? | Three |c Two | asdasd | asdasd',
            '| ? |3 asdasdasdasdasdasdasdasdasdasdasda |3 asdasd',
        ]
"""

class Column:
    __slots__ = ['halign', 'valign', 'span', 'content']

    def __init__(self, halign : int = 0, valign : int = 0, span : int = 1, content : str = None):
        self.halign, self.valign, self.span, self.content = halign, valign, span, content

    def __str__(self):  return f'{self.content} s:{self.span}'
    def __repr__(self): return self.__str__()

    def split(self, sep : Union[str,int], maxsplit=-1) -> List['Column']:
        result = []
        if isinstance(sep, int):
            c_split = [ self.content[:sep], self.content[sep:] ]
        else:
            c_split = self.content.split(sep, maxsplit=maxsplit)

        if len(c_split) == 1:
            return [self]
        for c in c_split:
            col = Column()
            col.halign = self.halign
            col.valign = self.valign
            col.span = self.span
            col.content = c
            result.append(col)
        return result

    def copy(self, content=...):
        if content is Ellipsis:
            content=self.content

        column = Column()
        column.halign = self.halign
        column.valign = self.valign
        column.span = self.span
        column.content = content
        return column

def ascii_table(table_def : List[str],
                min_table_width : int = None,
                max_table_width : int = None,
                fixed_table_width : int = None,
                style_borderless = False,
                left_border : str= '|',
                right_border : str = '|',
                border : str= '|',
                row_symbol : str = '-',
                col_def_delim = '|',
                ) -> str:
    """

    arguments

        table_def   list of str

            |[options] data - defines new column

            options:
                halign: l - left (default), c - center, r - right
                valign: t - top  (default), m - center, b - bottom
                1..N - col span

            example: ['|c99 TABLE NAME',
                      '|l first col |r second col']
    """
    if style_borderless:
        left_border, right_border, border, row_symbol = None, None, ' | ', None
        
    if fixed_table_width is not None:
        min_table_width = fixed_table_width
        max_table_width = fixed_table_width
        
    if min_table_width is not None and max_table_width is not None:
        if min_table_width > max_table_width:
            raise ValueError('min_table_width > max_table_width')

    col_spacing = len(border) if border is not None else 0
    cols_count = 0
    
    # Parse columns in table_def
    rows : List[List[Column]] = []
    for raw_line in table_def:
        # Line must starts with column definition
        if len(raw_line) == 0 or raw_line[0] != col_def_delim:
            raise ValueError(f'Line does not start with | symbol, content: "{raw_line}"')

        # Parsing raw columns
        row : List[Column] = []
        i_raw_col = 0
        raw_line_split = raw_line.split(col_def_delim)[1:]
        raw_line_split_len = len(raw_line_split)

        for n_raw_col, raw_col in enumerate(raw_line_split):
            # split column options and content
            col_opts, col_content = ( raw_col.split(' ', maxsplit=1) + [''] )[:2]

            # Parse column options
            col = Column(content=col_content)
            for col_opt in re.findall('[lcr]|[tmb]|[0-9]+', col_opts.lower()):
                h = _opts_halign.get(col_opt, None)
                if h is not None:
                    col.halign = h
                    continue
                v = _opts_valign.get(col_opt, None)
                if v is not None:
                    col.valign = v
                    continue
                col.span = max(1, int(col_opt))
            row.append(col)

            if n_raw_col != raw_line_split_len-1:
                i_raw_col += col.span
            else:
                # total max columns, by last column without span
                cols_count = max(cols_count, i_raw_col+1)

        rows.append(row)

    # Cut span of last cols to fit cols_count
    for row in rows:
        row[-1].span = cols_count - (sum(col.span for col in row) - row[-1].span)

    # Compute cols border indexes
    cols_border = [0]*cols_count
    for i_col_max in range(cols_count+1):
        for row in rows:
            i_col = 0
            col_border = 0
            for col in row:
                i_col += col.span
                col_max_len = max([ len(x.strip()) for x in col.content.split('\n')])
                col_border = cols_border[i_col-1] = max(cols_border[i_col-1], col_border + col_max_len)
                if i_col >= i_col_max:
                    break
                col_border += col_spacing

    # fix zero cols border
    for i_col, col_border in enumerate(cols_border):
        if i_col != 0 and col_border == 0:
            cols_border[i_col] = cols_border[i_col-1]

    table_width = cols_border[-1] + (len(left_border) if left_border is not None else 0) + \
                                    (len(right_border) if right_border is not None else 0)
                                    
    # Determine size of table width 
    table_width_diff = 0
    if max_table_width is not None:
        table_width_diff = max(table_width_diff, table_width - max_table_width)
    if min_table_width is not None:
        table_width_diff = min(table_width_diff, table_width - min_table_width)

    if table_width_diff != 0:
        # >0 :shrink, <0 :expand table
        diffs = [ x-y for x,y in zip(cols_border, [0]+cols_border[:-1] ) ]

        while table_width_diff != 0:
            if table_width_diff > 0:
                max_diff = max(diffs)
                if max_diff <= col_spacing:
                    raise Exception('Unable to shrink the table to fit max_table_width.')

                diffs[ diffs.index(max_diff) ] -= 1
            else:
                diffs[ diffs.index(min(diffs)) ] += 1

            table_width_diff += 1 if table_width_diff < 0 else -1

        for i in range(len(cols_border)):
            cols_border[i] = diffs[i] if i == 0 else cols_border[i-1] + diffs[i]

        # recompute new table_width
        table_width = cols_border[-1] + (len(left_border) if left_border is not None else 0) + \
                                        (len(right_border) if right_border is not None else 0)

    # Process columns for \n and col width
    new_rows : List[List[List[Column]]] = []
    for row in rows:
        row_len = len(row)

        # Gather multi rows for every col
        cols_sub_rows = []

        i_col = 0
        col_border = 0
        for col in row:
            i_col += col.span
            col_border_next = cols_border[i_col-1]

            col_width = col_border_next-col_border

            # slice col to sub rows by \n separator and col_width
            col_content_split = [ x.strip() for x in col.content.split('\n') ]
            cols_sub_rows.append([ x[i:i+col_width].strip() for x in col_content_split
                                                            for i in range(0, len(x), col_width) ])

            col_border = col_border_next + col_spacing

        cols_sub_rows_max = max([len(x) for x in cols_sub_rows])

        for n, (col, col_sub_rows) in enumerate(zip(row, cols_sub_rows)):
            valign = col.valign

            unfilled_rows = cols_sub_rows_max-len(col_sub_rows)
            if valign == 0: # top
                col_sub_rows = col_sub_rows + ['']*unfilled_rows
            elif valign == 1: # center
                top_pad = unfilled_rows // 2
                bottom_pad = unfilled_rows - top_pad
                col_sub_rows = ['']*top_pad + col_sub_rows + ['']*bottom_pad
            elif valign == 2: # bottom
                col_sub_rows = ['']*unfilled_rows + col_sub_rows

            cols_sub_rows[n] = col_sub_rows

        sub_rows = [ [None]*row_len for _ in range(cols_sub_rows_max) ]
        for n_col, col in enumerate(row):
            for i in range(cols_sub_rows_max):
                sub_rows[i][n_col] = col.copy(content=cols_sub_rows[n_col][i])

        new_rows.append(sub_rows)

    rows = new_rows

    # Composing final lines
    lines = []

    row_line = row_symbol[0]*table_width if row_symbol is not None else None
    if row_line is not None:
        lines.append(row_line)
    for sub_rows in rows:
        
        
        for row in sub_rows:
            line = ''

            if left_border is not None:
                line += left_border

            i_col = 0
            for col in row:
                col_content = col.content

                if i_col == 0:
                    col_border0 = 0
                else:
                    if border is not None:
                        line += border
                    col_border0 = cols_border[i_col-1] + col_spacing

                i_col += col.span

                col_border1 = cols_border[i_col-1]

                col_space = col_border1 - col_border0
                col_remain_space = col_space-len(col_content)

                halign = col.halign
                if halign == 0: # left
                    col_content = col_content + ' '*col_remain_space
                elif halign == 1: # center
                    col_left_pad = col_remain_space // 2
                    col_right_pad = col_remain_space - col_left_pad
                    col_content = ' '*col_left_pad + col_content + ' '*col_right_pad
                elif halign == 2: # right
                    col_content = ' '*col_remain_space + col_content

                line += col_content

            if right_border is not None:
                line += right_border

            lines.append(line)
            
        if len(sub_rows) != 0 and row_line is not None:
            lines.append(row_line)

    return '\n'.join(lines)
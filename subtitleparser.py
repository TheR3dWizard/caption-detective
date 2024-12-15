from itertools import groupby
from collections import namedtuple


def parse_subs(fpath):
    # "chunk" our input file, delimited by blank lines
    with open(fpath) as f:
        res = [list(g) for b, g in groupby(f, lambda x: bool(x.strip())) if b]

    Subtitle = namedtuple('Subtitle', 'sub_id start end text')

    subs = []

    # grouping
    for sub in res:
        if len(sub) >= 3:  # not strictly necessary, but better safe than sorry
            sub = [x.strip() for x in sub]
            sub_id, start_end, *content = sub  # py3 syntax
            start, end = start_end.split(' --> ')

            # ints only
            sub_id = int(sub_id)

            # join multi-line text
            text = ', '.join(content)

            subs.append(Subtitle(
                sub_id,
                start,
                end,
                text
            ))

    es_ready_subs = []

    for index, sub_object in enumerate(subs):
        prev_sub_text = ''
        next_sub_text = ''

        if index > 0:
            prev_sub_text = subs[index - 1].text + ' '

        if index < len(subs) - 1:
            next_sub_text = ' ' + subs[index + 1].text

        es_ready_subs.append(dict(
            **sub_object._asdict(),
            overlapping_text=prev_sub_text + sub_object.text + next_sub_text
        ))

    return es_ready_subs


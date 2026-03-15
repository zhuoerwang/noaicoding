def pretty_print(tree: list) -> list[str]:
    n = len(tree)
    h = n.bit_length()
    max_width = 2 ** h - 1
    res = []
    for level in range(h):
        line = [' '] * max_width
        step = 2 ** (h - level) # last level is 1
        offset = (step // 2) - 1
        for j in range(2 ** level):
            idx = 2 ** level + j - 1
            if idx < len(tree) and tree[idx] is not None:
                line[offset + step * j] = str(tree[idx])
            else:
                line[offset + step * j] = '*'

        res.append(''.join(line).rstrip())

    return res

res = pretty_print([1, 2, 3, 4])
for row in res:
    print(row)
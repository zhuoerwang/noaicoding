def calculate_charge(usage: list[list[int, int]],
                     default_price: int,
                     overrides: list[list[int, int, int]]) -> int:
    res = 0
    overrides.sort(key=lambda x:x[0])

    for start, end in usage:
        pos = start
        for s, e, override_price in overrides:
            if s >= end:
                break
            
            if e <= start:
                continue
            
            if s > pos:
                res += (s - pos) * default_price
            
            o_left = max(pos, s)
            o_right = min(end, e)
            res += (o_right - o_left) * override_price
            pos = o_right
        
        if pos < end:
            res += (end - pos) * default_price

    return res

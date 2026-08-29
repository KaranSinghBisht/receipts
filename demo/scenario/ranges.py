def parse_range(text):
    if '-' not in text:
        return None
    lo, hi = text.split('-')
    return (int(lo), int(hi))

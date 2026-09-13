def detect_language(text: str) -> str:
    text = text.lower()

    bisaya_keywords = [
        'unsaon', 'asa', 'unsa', 'kanus-a', 'pila', 'ngano',
        'palihug', 'nako', 'nimo', 'ug', 'mao', 'adto'
    ]

    tagalog_keywords = [
        'paano', 'saan', 'ano', 'kailan', 'magkano', 'bakit',
        'po', 'opo', 'kailangan', 'para', 'bayad', 'pumunta'
    ]

    import re
    bis_count = sum(1 for word in bisaya_keywords if re.search(r'\b' + re.escape(word) + r'\b', text))
    tl_count = sum(1 for word in tagalog_keywords if re.search(r'\b' + re.escape(word) + r'\b', text))

    if bis_count > tl_count and bis_count > 0:
        return "bis"
    elif tl_count > bis_count and tl_count > 0:
        return "tl"
    return "en"
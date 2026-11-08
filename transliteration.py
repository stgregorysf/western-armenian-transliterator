import re


CUSTOM_MAP = {
    # Capitalized and multi-character common words/clusters
    'Եւ': 'Yév',
    'եւ': 'yév',
    'ընդ': 'ûnt',
    'հոգւոյդ': 'hokvooyt',
    'քում': 'koom',
    'Աստուած': 'Asdvadz',
    'Որ': 'Vor',
    'որ': 'vor',
    'Տէր': 'Dér',
    'ողորմեա': 'voghormya',
    'զմեզ': 'ûzméz',
    'կեցո': 'gétso',
    'Սուրբ': 'Soorp',
    'մեր': 'mér',
    'Ամէն': 'Amén',
    'Յիսուս': 'Hisoos',

    # Individual letters and phonetic elements based on dataset patterns
    'Ա': 'A',
    'ա': 'a',
    'Բ': 'P',
    'բ': 'p',
    'Գ': 'K',
    'գ': 'k',
    'Դ': 'T',
    'դ': 't',
    'Ե': 'Yé',
    'ե': 'é',
    'Զ': 'Z',
    'զ': 'z',
    'Է': 'É',
    'է': 'é',
    'Ը': 'Û',
    'ը': 'û',
    'Թ': 'T',
    'թ': 't',
    'Ժ': 'Zh',
    'ժ': 'zh',
    'Ի': 'I',
    'ի': 'i',
    'Լ': 'L',
    'լ': 'l',
    'Խ': 'Kh',
    'խ': 'kh',
    'Ծ': 'Dz',
    'ծ': 'dz',
    'Կ': 'G',
    'կ': 'g',
    'Հ': 'H',
    'հ': 'h',
    'Ձ': 'Dz',
    'ձ': 'dz',
    'Ղ': 'Gh',
    'ղ': 'gh',
    'Ճ': 'J',
    'ճ': 'j',
    'Մ': 'M',
    'մ': 'm',
    'Յ': 'Y',
    'յ': 'y',
    'Ն': 'N',
    'ն': 'n',
    'Շ': 'Sh',
    'շ': 'sh',
    'Ո': 'O',
    'ո': 'o',
    'Չ': 'Ch',
    'չ': 'ch',
    'Պ': 'B',
    'պ': 'b',
    'Ջ': 'J',
    'ջ': 'j',
    'Ռ': 'R',
    'ռ': 'r',
    'Ս': 'S',
    'ս': 's',
    'Վ': 'V',
    'վ': 'v',
    'Տ': 'D',
    'տ': 'd',
    'Ր': 'R',
    'ր': 'r',
    'Ց': 'Ts',
    'ց': 'ts',
    'Ւ': 'V',
    'ւ': 'v',
    'Փ': 'P',
    'փ': 'p',
    'Ք': 'K',
    'ք': 'k',
    'Օ': 'O',
    'օ': 'o',
    'Ֆ': 'F',
    'ֆ': 'f',
}

def parse_transliteration_data(filepath):
    """Parses the training file and extracts Armenian-to-transliteration pairs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = content.split('----------------------------------------')
    training_pairs = []
    
    for section in sections:
        lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
        if len(lines) >= 2:
            armenian_text = lines[0]
            translit_text = lines[1]
            training_pairs.append((armenian_text, translit_text))
            
    return training_pairs

import re

# Define context-dependent rules as an ordered list of (compiled_regex, replacement) tuples.
# Order is preserved, mimicking your original sequential logic.
CONTEXT_RULES = [
    # 1. Word-initial 'Յ' / 'յ' -> 'H' / 'h'
    (re.compile(r'\bՅ'), 'H'),
    (re.compile(r'\bյ'), 'h'),
    
    # 2. Specific multi-character digraphs & edge cases
    (re.compile(r'նս'), 'nûs'),
    (re.compile(r'իւ'), 'yoo'),
    (re.compile(r'Ուա|ուա|ուԱ|ՈւԱ'), 'Va'),
    (re.compile(r'կր'), 'gûr'),
    (re.compile(r'ւոյ'), 'vo'),
    (re.compile(r'ոյ'), 'ooy'),
    (re.compile(r'եա'), 'ya'),
    (re.compile(r'զԵ'), 'zé'),
    (re.compile(r'նն'), 'nûn'),
    (re.compile(r'սն'), 'sûn'),
    (re.compile(r'սր'), 'sûr'),
    
    # 3. General digraphs
    (re.compile(r'Ու'), 'Oo'),
    (re.compile(r'ու'), 'oo'),
    
    # 4. Word-initial vowels requiring context conversion
    (re.compile(r'\bո'), 'vo'),
    (re.compile(r'\bՈ'), 'Vo'),
    (re.compile(r'\bե'), 'yé'),
    (re.compile(r'\bԵ'), 'Yé'),
    
    # 5. Remaining medial 'ո' / 'Ո'
    (re.compile(r'ո'), 'o'),
    (re.compile(r'Ո'), 'O'),
]

def transliterate(armenian_text, custom_map=CUSTOM_MAP):
    """
    Transliterates Unicode Armenian text into Latin characters 
    using an ordered rule pipeline and a fallback character map.
    """
    tokens = re.findall(r'\w+|\W+', armenian_text)
    result = []
    
    # Pre-compile the fallback character mapping regex (sorted by length descending)
    sorted_keys = sorted(custom_map.keys(), key=len, reverse=True)
    fallback_pattern = re.compile('|'.join(re.escape(k) for k in sorted_keys))
    
    for token in tokens:
        if any(c.isalpha() for c in token):
            word = token
            
            # Apply context-dependent rules sequentially through the pipeline
            for pattern, replacement in CONTEXT_RULES:
                word = pattern.sub(replacement, word)
            
            # Apply standard character mapping for remaining single characters
            word = fallback_pattern.sub(lambda m: custom_map[m.group(0)], word)
            
            result.append(word)
        else:
            result.append(token)
            
    return ''.join(result)

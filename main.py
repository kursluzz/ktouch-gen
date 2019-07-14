import yaml
import re
import uuid

# settings
row_len = 60
rows_num = 10
min_chars_word = 2
max_chars_word = 6
words_file = 'dictionary.txt'  # language words, each in new line, ordered by most used first


with open(words_file, 'r') as f:
    words = f.read()

with open('chars.yaml', 'r') as ch:
    all_chars: dict = yaml.safe_load(ch)
lessons_char_list: list = all_chars['letters']
lessons_symbol_list: list = all_chars['symbols']


def get_letters_lesson_text(new_chars: str, prev_chars: str):
    def _zip_list_of_lists(l):
        return list(sum(list(zip(*l)), ()))
    # each word will have to contain one of new chars (one after another). Rest of new chars and previous chars will be
    # filled randomly. The words will be selected from existing words list, ordered by most used first.
    # select lists of words for each char from new chars
    char_lists = []
    for char in new_chars:
        all_chars = f'{new_chars}{prev_chars}'
        char_words = re.findall(r'^[%s]*[%s]+[%s]*$' % (all_chars, char, all_chars), words, re.MULTILINE)
        char_lists.append([w for w in char_words if len(w) >= min_chars_word and len(w) <= max_chars_word])

    # merge char_lists
    flat_word_list = _zip_list_of_lists(char_lists)

    possible_max_words = row_len * rows_num // (min_chars_word + 1)

    if len(flat_word_list) < possible_max_words:
        # flat_word_list *= possible_max_words // len(flat_word_list) + 1
        for char_list in char_lists:
            if len(char_list) < possible_max_words:
                char_list *= possible_max_words // len(char_list)
            # char_lists = [char_list * (possible_max_words // len(char_list)) for char_list in char_lists]
        flat_word_list = _zip_list_of_lists(char_lists)
    else:
        flat_word_list = flat_word_list[:possible_max_words + 1]

    rows = []
    for row_i in range(rows_num):

        row = []
        while True:
            row.append(flat_word_list.pop(0))
            if len(' '.join(row)) + max_chars_word // 2 > row_len:
                rows.append(' '.join(row))
                break
    return "\n".join(rows)


def get_symbols_lesson_text(symbols, letters):
    char_words = re.findall(r'^[%s]*$' % letters, words, re.MULTILINE)
    symbols_len = len(symbols)
    rows = []

    for row_i in range(rows_num):
        i = 0
        row = []
        while True:
            row.append(f'{char_words.pop(0)}{symbols[i % symbols_len]}')
            i += 1
            if len(' '.join(row)) + max_chars_word // 2 > row_len:
                break
        rows.append(' '.join(row))
    return "\n".join(rows)


def to_xml(lesons_list: list):
    xml_str = ''
    for lesson in lesons_list:
        xml_str = f"""{xml_str}
  <lesson>
   <id>{{{uuid.uuid4()}}}</id>
   <title>{lesson['title']}</title>
   <newCharacters>{lesson['new_chars']}</newCharacters>
   <text>{lesson['text']}</text>
  </lesson>"""
    return f"""<?xml version="1.0"?>
<course>
 <id>{{{uuid.uuid4()}}}</id>
 <title>Hebrew</title>
 <description>Created by Oleg Tendler &lt;kursluzz@gmail.com&gt; Israel 2019
Lessons generation script: https://github.com/kursluzz/ktouch-gen
Homepage: https://kursluzz.wordpress.com/</description>
 <keyboardLayout>hebrew</keyboardLayout>
 <lessons>{xml_str}
 </lessons>
</course>"""


lessons = []
for lesson_i, new_lesson_chars in enumerate(lessons_char_list):
    prev_lesson_chars = ''.join(lessons_char_list[:lesson_i])
    lessons.append({
        'title': f'אותיות {new_lesson_chars}',
        'new_chars': f'{new_lesson_chars}',
        'text': get_letters_lesson_text(new_lesson_chars, prev_lesson_chars),
    })
for lesson_i, new_lesson_chars in enumerate(lessons_symbol_list):
    lessons.append({
        'title': f'תוים {new_lesson_chars}',
        'new_chars': f'{new_lesson_chars}',
        'text': get_symbols_lesson_text(new_lesson_chars, ''.join(lessons_char_list)),
    })
print(to_xml(lessons))

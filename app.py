# coding=utf-8
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.widgets import TextArea

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    def __init__(self, form, q):
        super(ReusableForm, self).__init__(form)
        self.name = TextAreaField(q, validators=[validators.required()])


freq_he = {
    u'א': 4.66,
    u'ב': 5.36,
    u'ג': 1.78,
    u'ד': 2.66,
    u'ה': 8.40,
    u'ו': 11.20,
    u'ז': 0.93,
    u'ח': 2.20,
    u'ט': 1.78,
    u'י': 11.70,
    u'כ': 1.88,
    u'ל': 6.20,
    u'מ': 5.13,
    u'נ': 3.65,
    u'ס': 2.23,
    u'ע': 2.65,
    u'פ': 2.29,
    u'צ': 1.30,
    u'ק': 2.62,
    u'ר': 6.65,
    u'ש': 4.24,
    u'ת': 5.46}
freq_list_he = []
for k, v in freq_he.items():
    freq_list_he.append((v, k))
freq_list_he.sort()
freq_letters_he = []
for v, k in freq_list_he:
    freq_letters_he.append(k)

d_he = {u'א': 0,
        u'ב': 1,
        u'ג': 2,
        u'ד': 3,
        u'ה': 4,
        u'ו': 5,
        u'ז': 6,
        u'ח': 7,
        u'ט': 8,
        u'י': 9,
        u'כ': 10,
        u'ל': 11,
        u'מ': 12,
        u'נ': 13,
        u'ס': 14,
        u'ע': 15,
        u'פ': 16,
        u'צ': 17,
        u'ק': 18,
        u'ר': 19,
        u'ש': 20,
        u'ת': 21}

last_letters_map_he = {
    u'ך': u'כ',
    u'ם': u'מ',
    u'ף': u'פ',
    u'ן': u'נ',
    u'ץ': u'צ'
}
inv_d_he = {v: k for k, v in d_he.items()}

last_letters_map_en = {}

freq_en = {'Z': 0.07, 'J': 0.10, 'Q': 0.11, 'X': 0.17, 'K': 0.69, 'V': 1.11, 'B': 1.49, 'P': 1.82, 'G': 2.03,
           'W': 2.09, 'Y': 2.11, 'F': 2.30, 'M': 2.61, 'C': 2.71, 'U': 2.88, 'L': 3.98, 'D': 4.32, 'H': 5.92,
           'R': 6.02, 'S': 6.28, 'N': 6.95, 'I': 7.31, 'O': 7.68, 'A': 8.12, 'T': 9.10, 'E': 12.02}
freq_list_en = []
for k, v in freq_en.items():
    freq_list_en.append((v, k))
freq_list_en.sort()
freq_letters_en = []
for v, k in freq_list_en:
    freq_letters_en.append(k)
ab = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
d_en = {k: i for i, k in enumerate(ab)}
inv_d_en = {v: k for k, v in d_en.items()}


def lenakot(text):
    new_text = text[:]
    for letter in text:
        if letter not in d and letter not in last_letters_map:
            new_text = new_text.replace(letter, '')
    return new_text


def last_letter_replce(text):
    for last_letter in last_letters_map:
        text = text.replace(last_letter, last_letters_map[last_letter])
    return text


def shift(letter, offset):
    number = (d[letter] + offset) % len(d)
    return inv_d[number]


def code(text, key):
    cypher_text = u''
    for letter in text:
        cypher_text = cypher_text + shift(letter, key)
    return cypher_text


def shift_back(letter, offset):
    number = (d[letter] - offset) % len(d)
    return inv_d[number]


def decode(cypher_text, key):
    text = u''
    for letter in cypher_text:
        text = text + shift_back(letter, key)
    return text


def vigenere(text, key):
    cypher_text = u''
    for i in range(len(text)):
        cypher_text += shift(text[i], d[key[i % len(key)]])
    return cypher_text


def decypher_vigenere(cypher_text, key):
    text = u''
    for i in range(len(cypher_text)):
        text += shift_back(cypher_text[i], d[key[i % len(key)]])
    return text


def friedman_test(freq, ct):
    sum = 0
    for i in range(len(d)):
        sum += freq[i][0] * (freq[i][0] - 1)

    ic = sum / (float((len(ct)) * (len(ct) - 1)))
    ic = (ic) / (0.0385)
    print(ic)
    if ic > 1.5:
        return True
    else:
        return False


def create_freq(group):
    dic = {}
    for letter in d:
        dic[letter] = (group.count(letter))

    l = []
    for key, val in dic.items():
        l.append((val, key))
    l.sort()
    return l


def rank_offset(letters, offset):
    shifted = u''
    for letter in letters:
        shifted += shift(letter, offset)
    freq = create_freq(shifted)
    current_freq_letters = []
    for v, k in freq:
        current_freq_letters.append(k)
    rank = len(set(current_freq_letters[:5]) & set(freq_letters[:5]))
    rank += len(set(current_freq_letters[-5:]) & set(freq_letters[-5:]))
    return rank


def check_key_len(cypher_text):
    return len(cypher_text) // 400


def break_vigenere(cypher_text):
    for i in range(check_key_len(cypher_text)):
        print(i + 1)
        groups = []
        for x in range(i + 1):
            groups.append([])
        result = True
        for group in range(len(groups)):
            for j in range(group, len(cypher_text), len(groups)):
                groups[group].append(cypher_text[j])
            freq = create_freq(groups[group])
            result = result and friedman_test(freq, groups[group])
        if result:
            print('KEY len {}'.format(i + 1))
            break
    else:
        return ''
    key = u''
    for group in groups:
        ranks = []
        for i in range(len(d)):
            ranks.append((rank_offset(group, i), i))
        ranks.sort()
        print(inv_d[(len(d) - ranks[-1][1]) % len(d)])
        key += inv_d[(len(d) - ranks[-1][1]) % len(d)]
    return key


def detect_language(text):
    for letter in text:
        if letter.upper() in d_en:
            return "en"
        if letter in d_he:
            return "he"


class PostForm(Form):
    plain = StringField(u'Text', widget=TextArea())
    key = StringField(u'Text', widget=TextArea())
    cypher_text = StringField(u'Text', widget=TextArea())
    cypher = StringField(u'Text', widget=TextArea())
    decypher = StringField(u'Text', widget=TextArea())


@app.route("/", methods=['GET', 'POST'])
def hello():
    global d, inv_d, last_letters_map, freq_letters

    PostForm.cypher_text = StringField(u'Text', widget=TextArea())
    PostForm.decypher = StringField(u'Text', widget=TextArea())
    plain_text = request.form.get('plain')
    key = request.form.get('key')
    if plain_text and key:
        language = detect_language(plain_text)
        if language == "en":
            d = d_en
            inv_d = inv_d_en
            last_letters_map = last_letters_map_en
            freq_letters = freq_letters_en
        else:
            d = d_he
            inv_d = inv_d_he
            last_letters_map = last_letters_map_he
            freq_letters = freq_letters_he
        clean_text = lenakot(plain_text.upper())
        clean_key = lenakot(key.upper())
        if language == "he":
            clean_text = last_letter_replce(clean_text)
            clean_key = last_letter_replce(clean_key)

        if clean_key:
            cypher = vigenere(clean_text, clean_key)
            PostForm.cypher_text = TextAreaField("TextArea", default=cypher)

    cypher_text = request.form.get('cypher')
    if cypher_text:
        language = detect_language(plain_text)
        if language == "en":
            d = d_en
            inv_d = inv_d_en
            last_letters_map = last_letters_map_en
            freq_letters = freq_letters_en
        else:
            d = d_he
            inv_d = inv_d_he
            last_letters_map = last_letters_map_he
            freq_letters = freq_letters_he
        key = break_vigenere(cypher_text)
        if key:
            flash('The Key is: {}'.format(key))
            PostForm.decypher = TextAreaField("TextArea", default=decypher_vigenere(cypher_text, key))
        else:
            flash(u'Impossible to break')

    return render_template('index.html', form=PostForm())


if __name__ == "__main__":
    app.run(threaded=True, port=5000)

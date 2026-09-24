import json
import re
import sys

PATH = 'hydraulic-lifting-table-troubleshooting-repair-guide.html'
html = open(PATH, encoding='utf-8').read()
ok = True

blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
faq = None
schema_types = []
for block in blocks:
    try:
        data = json.loads(block)
        schema_types.append(data.get('@type'))
        if data.get('@type') == 'FAQPage':
            faq = data
    except json.JSONDecodeError as exc:
        print('INVALID JSON-LD:', exc)
        ok = False
for required in ('Article', 'FAQPage', 'Organization'):
    if required not in schema_types:
        print('MISSING SCHEMA:', required)
        ok = False

if faq is None:
    print('FAQPage missing')
    ok = False
else:
    ld_pairs = [
        (item['name'].strip(), item['acceptedAnswer']['text'].strip())
        for item in faq['mainEntity']
    ]
    faq_visible = html.split(
        '<h2 class="text-2xl font-bold mb-4">Frequently Asked Questions</h2>', 1
    )[1].split('<div class="bg-slate-100', 1)[0]
    visible_questions = re.findall(
        r'<h3 class="font-black text-slate-800 mb-2">(.*?)</h3>',
        faq_visible,
        re.DOTALL,
    )
    visible_answers = re.findall(
        r'<p class="text-sm text-slate-600 leading-relaxed">(.*?)</p>',
        faq_visible,
        re.DOTALL,
    )
    print('FAQPage:', len(ld_pairs), '| visible Q/A:', len(visible_questions), len(visible_answers))
    if len(ld_pairs) != 4 or len(visible_questions) != 4 or len(visible_answers) != 4:
        ok = False
    for i, (question, answer) in enumerate(ld_pairs):
        if i >= len(visible_questions) or question != visible_questions[i].strip() or answer != visible_answers[i].strip():
            print('FAQ mismatch:', i)
            ok = False

required_text = [
    '500 kg', '30-40 cm',
    '150 kg', '300 kg', '21-22 cm', '28-30 cm',
    '200 / 300 / 1000 kg', '126 / 90 / 100 cm',
    '500 / 800 / 1000 W', '12V lead-acid',
    'Lifts slowly', 'Oil leak', 'Platform shakes', 'Will not lower',
    'qualified service personnel', 'mechanical support',
    'safety-critical fault', 'return-to-service', 'Fault report', 'Unloaded test', 'Controlled load test',
]
for text in required_text:
    if text not in html:
        print('MISSING:', text)
        ok = False

competitors = [
    'TOYOTA', 'HYSTER', 'JUNGHEINRICH', 'CROWN', 'LINDE', 'STILL',
    'CLARK', 'YALE', 'KOMATSU', 'NISSAN', 'MITSUBISHI', 'CATERPILLAR',
    'TCM', 'DOOSAN', 'HELI', 'HANGCHA', 'BLUE GIANT', 'ADVANCE',
    'SUTHERLAND', 'PENTA', 'NORDIC', 'HYMO', 'BOLLHOFF', 'BAISHENG',
    'NOBLIFT', 'SEWON', 'SOVEMA', 'CENTAUR', 'VERLINDE', 'NILFISK',
]
for competitor in competitors:
    if re.search(r'\b' + re.escape(competitor) + r'\b', html, re.IGNORECASE):
        print('COMPETITOR:', competitor)
        ok = False

for placeholder in ('jsonFaqs', "' + $", 'PLACEHOLDER', 'TODO'):
    if placeholder in html:
        print('PLACEHOLDER:', placeholder)
        ok = False

for image_id in (
    'A505d7d6b6672420fba365dc1d6b58e57l',
    'Ab91ddc1baa794faa9f42ee2cebc54d02A',
    'Acac15ecc1a39475ca3b876397b848aecV',
    'H094d445ef7544ed0b8eea6b6d0d98b9bQ',
):
    if image_id not in html:
        print('MISSING IMAGE:', image_id)
        ok = False

if 'hydraulic-lifting-table-safety-maintenance-guide.html' not in html:
    print('MISSING LINK TO BLOG 15')
    ok = False

print('ALL OK:', ok)
sys.exit(0 if ok else 1)

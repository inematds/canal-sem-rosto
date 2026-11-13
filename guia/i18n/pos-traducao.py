#!/usr/bin/env python3
"""Correções depois do traduz-pagina-codex.py (EN/ES): banners por idioma, nome do método, frases que o
tradutor quebrou (revisor independente, 13/11/2026), datas e decimais no EN, links dos kits irmãos no idioma.
Uso: python3 guia/i18n/pos-traducao.py   (idempotente; falha se uma troca obrigatória não casar)"""
import re
from pathlib import Path

G = Path(__file__).resolve().parent.parent

COMUM = [
    ('src="../assets/banner-grade.jpg"', 'src="../assets/banner-grade-{l}.jpg"'),
    ('src="../assets/banner.jpg"', 'src="../assets/banner-{l}.jpg"'),
    ('https://inematds.github.io/youtube-bombando/guia/"', 'https://inematds.github.io/youtube-bombando/guia/{l}/"'),
    ('https://inematds.github.io/curiosidade-viral/guia/"', 'https://inematds.github.io/curiosidade-viral/guia/{l}/"'),
]

EN = [
    ('<h1>Your channel can grow <span class="amb">no face on camera</span></h1>',
     '<h1>Your channel can grow <span class="amb">without showing your face</span></h1>'),
    ('aceless channel with radar', 'aceless channel with a radar'),
    ('Topics the kit removed <span class="amb">from this round</span>', 'Topics the kit pulled <span class="amb">from this round</span>'),
    ('You <strong>not required</strong> from this part to understand what\'s above.',
     'You <strong>don\'t need</strong> this part to understand what\'s above.'),
    ('saida/pautas.md</code> e <code>', 'saida/pautas.md</code> and <code>'),
    ('<h2>What\'s next <span class="amb">in the repository</span></h2>', '<h2>What comes <span class="amb">in the repository</span></h2>'),
    ('<th>Archive</th>', '<th>File</th>'),
    ('It made <b>3 times or more</b> the usual number? Then', 'Did it get <b>3 times or more</b> the usual number? Then'),
    ('It got <b>3 times or more</b> the usual number? Then', 'Did it get <b>3 times or more</b> the usual number? Then'),
    ('Every suggested format has its own voice, test, or explanation', 'Every suggested format has your voice, your test, or your explanation'),
    ('aria-label="Switch topic"', 'aria-label="Toggle theme"'), ('title="Switch topic"', 'title="Toggle theme"'),
    ('Faceless <span class="amb">isn\'t anonymous</span>', 'Faceless <span class="amb">doesn\'t mean authorless</span>'),
    ('<span class="c"># "no third-party sources found" = you can proceed</span>',
     '<span class="c"># "nenhuma fonte de terceiro encontrada" (no third-party source found; the kit prints in Portuguese) = you can proceed</span>'),
]
ES = [
    ('anal sin mostrar el rostro con radar', 'anal sin rostro con radar'),
    ('Los temas que el kit descartó <span class="amb">de esta ronda</span>', 'Los temas que el kit sacó <span class="amb">de esta ronda</span>'),
    ('Tú <strong>no hace falta</strong> de esta parte para entender lo que está arriba.',
     '<strong>No necesitas</strong> esta parte para entender lo que está arriba.'),
    ('saida/pautas.md</code> e <code>', 'saida/pautas.md</code> y <code>'),
    ('¿¿Hizo', '¿Hizo'),
    ('. Hizo <b>3 veces o más</b> lo habitual?', '. ¿Hizo <b>3 veces o más</b> lo habitual?'),
    ('Ejecuta tu radar', 'Ejecútalo sobre tu radar'),
    ('<h2>Del radar a la <span class="amb">tema</span></h2>', '<h2>Del radar al <span class="amb">tema</span></h2>'),
    ('Sin mostrar el rostro <span class="amb">no carece de autoría</span>', 'Sin rostro <span class="amb">no es sin autoría</span>'),
    ('<span class="c"># "no se encontró ninguna fuente de terceros" = puedes continuar</span>',
     '<span class="c"># "nenhuma fonte de terceiro encontrada" (ninguna fuente de terceros; el kit responde en portugués) = puedes continuar</span>'),
]

MESES = {'11': 'Nov', '02': 'Feb'}


def datas_en(t):
    t = t.replace('1º/02/2027', 'Feb 1, 2027').replace('2/1/2027', 'Feb 1, 2027')
    t = re.sub(r'\b11/(1[23])/2026\b', r'Nov \1, 2026', t)
    t = re.sub(r'\b(1[23])/11/2026\b', r'Nov \1, 2026', t)
    return t


def decimais_en(t):
    # vírgula decimal → ponto fora de <pre>/<script>/<style> (27,3× → 27.3×; 63,0% → 63.0%)
    partes = re.split(r'(<pre>.*?</pre>|<script>.*?</script>|<style>.*?</style>)', t, flags=re.S)
    for i in range(0, len(partes), 2):
        partes[i] = re.sub(r'(\d),(\d)(?=[\d]*\s?[×%x])', r'\1.\2', partes[i])
    return ''.join(partes)


for l, trocas in (('en', EN), ('es', ES)):
    p = G / l / 'index.html'
    t = p.read_text(encoding='utf-8')
    for a, b in COMUM:
        t = t.replace(a, b.format(l=l))
    for a, b in trocas:
        if a in t:
            t = t.replace(a, b)
        else:
            if b not in t:
                print(f'{l}: aviso, não casou (conferir à mão): {a[:70]}')
    if l == 'en':
        t = decimais_en(datas_en(t))
    p.write_text(t, encoding='utf-8')
    print(l, 'ok')

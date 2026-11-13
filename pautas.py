#!/usr/bin/env python3
"""Transforma dados locais do radar em assuntos, sem publicar fontes."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
import math
from pathlib import Path
import re
from statistics import median
import sys
import unicodedata

BASE = Path(__file__).resolve().parent
PADRAO = Path('~/projetos/youtube-bombando/painel/dados.json').expanduser()
# Onde o radar costuma estar: ao lado deste kit, na pasta de projetos ou na pasta pessoal.
CANDIDATOS = [Path(__file__).resolve().parent.parent / 'youtube-bombando/painel/dados.json', PADRAO,
              Path('~/youtube-bombando/painel/dados.json').expanduser()]


def achar_radar():
    """Primeiro dados.json do radar que existir; se nenhum existir, o caminho padrão (dá a mensagem de erro)."""
    return next((c for c in CANDIDATOS if c.is_file()), PADRAO)
CUIDADO = 'O YouTube não monetiza conteúdo repetitivo ou de molde sem contribuição original; mostre seu teste e sua análise.'
ETAPAS = ['Escolher o assunto no radar', 'Escrever um roteiro com gancho', 'Produzir sem rosto com autoria', 'Publicar com promessa clara', 'Medir no radar após 7 dias']
FAIXAS = ['curto (< 8 min)', 'médio (8–20 min)', 'longo (20–60 min)', 'maratona (> 60 min)', 'sem duração']


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto).casefold()) if unicodedata.category(c) != 'Mn')


def carregar(caminho):
    with Path(caminho).expanduser().open(encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict) or not isinstance(dados.get('videos', []), list):
        raise ValueError('Estrutura inválida')
    return dados


def ler_temas():
    return json.loads((BASE / 'temas.json').read_text(encoding='utf-8'))


def numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def br(valor, casas=0):
    if valor is None:
        return 'sem dados'
    return format(valor, f',.{casas}f').replace(',', '_').replace('.', ',').replace('_', '.')


def filtrar(videos, piso_views=1000, fator=3, amostra=5):
    return [v for v in videos if isinstance(v, dict)
            and v.get('categoria') in {'Conteúdo', 'Conteúdo + quem fala'}
            and v.get('porte') in {'pequeno', 'médio'}
            and all(numero(v.get(k)) and v[k] >= limite for k, limite in
                    [('views', piso_views), ('fator_canal', fator), ('n_amostra', amostra)])]


def tema_de(titulo, temas=None):
    temas = ler_temas() if temas is None else temas
    texto = normalizar(titulo or '')
    # Temas de reação têm precedência, mesmo se o dicionário for reordenado.
    for tema in sorted(temas, key=lambda t: not t.get('evitar_sem_rosto', False)):
        for palavra in tema['palavras']:
            p = normalizar(palavra)
            if re.search(r'(?<!\w)' + re.escape(p) + r'(?!\w)', texto):
                return tema
    return {'rotulo': 'geral do nicho', 'palavras': []}


def faixa_de(duracao):
    if not numero(duracao) or duracao < 0:
        return FAIXAS[4]
    if duracao < 480:
        return FAIXAS[0]
    if duracao <= 1200:
        return FAIXAS[1]
    if duracao <= 3600:
        return FAIXAS[2]
    return FAIXAS[3]


def agrupar(videos, temas=None):
    grupos = defaultdict(list)
    for v in videos:
        tema = tema_de(v.get('titulo'), temas)['rotulo']
        nichos = v.get('nichos') or []
        if not isinstance(nichos, list):
            nichos = []
        for nicho in sorted({n.strip() for n in nichos if isinstance(n, str) and n.strip()}):
            grupos[(nicho, tema)].append(v)
    return grupos


def canais_distintos(videos):
    # Liga o nome ao ID quando só parte dos registros traz o ID.
    ids_por_nome = defaultdict(set)
    for v in videos:
        if v.get('channel_id') and v.get('canal'):
            ids_por_nome[normalizar(v['canal'])].add(str(v['channel_id']))
    canais = set()
    for v in videos:
        cid, nome = v.get('channel_id'), normalizar(v.get('canal') or '')
        if cid:
            canais.add(('id', str(cid)))
        elif nome:
            ids = ids_por_nome[nome]
            if len(ids) == 1:
                canais.add(('id', next(iter(ids))))
            elif not ids:
                canais.add(('nome', nome))
        # Ausência de identidade nunca prova um canal distinto.
    return len(canais)


def formato(tema, faixa):
    if 'comparação' in tema:
        texto = 'comparação lado a lado com teste real na tela e a sua conclusão'
    elif 'novidade' in tema:
        texto = 'notícia comentada com a sua opinião e um teste próprio'
    elif any(t in tema for t in ['curso', 'automação', 'prompts', 'erros', 'visual']):
        texto = 'tutorial de tela gravada com a sua narração explicando cada passo'
    else:
        texto = 'explicação com quadro/diagrama animado e a sua voz, usando um exemplo próprio'
    complemento = {FAIXAS[0]: '; resolva uma dúvida com uma demonstração', FAIXAS[1]: '; mostre um caso do começo ao fim', FAIXAS[2]: '; desenvolva um projeto com etapas', FAIXAS[3]: '; organize em capítulos com práticas diferentes', FAIXAS[4]: '; defina a duração depois de testar o roteiro'}
    return texto + complemento[faixa]


def resumo(nicho, tema, videos):
    fatores = [v['fator_canal'] for v in videos]
    idades = [v['idade_h'] for v in videos if numero(v.get('idade_h')) and v['idade_h'] >= 0]
    contagem = Counter(faixa_de(v.get('duracao')) for v in videos)
    faixa = min(contagem, key=lambda f: (-contagem[f], FAIXAS.index(f)))
    return dict(assunto=f'{tema} em {nicho}', videos=len(videos), canais=canais_distintos(videos),
                fator_mediano=median(fatores), fator_max=max(fatores),
                views_somadas=sum(v['views'] for v in videos), faixa_mais_comum=faixa,
                idade_mediana_h=median(idades) if idades else None)


def montar_pautas(dados, n=10, piso_views=1000, fator=3, amostra=5):
    temas = ler_temas()
    grupos = agrupar(filtrar(dados.get('videos', []), piso_views, fator, amostra), temas)
    evitar = {t['rotulo']: t.get('motivo') for t in temas if t.get('evitar_sem_rosto')}
    pautas, fracos, fora = [], [], []
    for (nicho, tema), videos in grupos.items():
        item = resumo(nicho, tema, videos)
        if tema in evitar:
            motivo = evitar[tema] or 'depende de reação ou personagem'
            item['motivo'] = motivo[0].upper() + motivo[1:] + '; fora do método sem rosto.'
            fora.append(item)
        elif item['canais'] < 2:
            fracos.append(item)
        else:
            item['por_que'] = (f"{br(item['videos'])} vídeos de {br(item['canais'])} canais pequenos/médios fizeram "
                               f"{br(item['fator_mediano'], 1)}× (mediana) o normal do próprio canal; faixa mais comum: {item['faixa_mais_comum']}.")
            item['formato_sem_rosto'] = formato(tema, item['faixa_mais_comum'])
            item['cuidado'] = CUIDADO
            pautas.append(item)
    chave = lambda p: (-p['canais'], -p['fator_mediano'], -p['views_somadas'], p['assunto'])
    pautas.sort(key=chave)
    contexto = []
    porque = dados.get('porque') or {}
    for nicho, info in (porque.get('nichos') or {}).items():
        for categoria in (info or {}).get('categorias') or []:
            if categoria.get('categoria') == 'Conteúdo' and numero(categoria.get('pct_views')):
                contexto.append(f"em {nicho}, {br(categoria['pct_views'], 1)}% das views vieram de vídeos que furaram a bolha pelo conteúdo")
    try:
        data = datetime.fromisoformat(dados.get('gerado_em') or '').isoformat()
    except (ValueError, TypeError):
        data = 'sem data'
    resultado = dict(gerado_em=data, filtro=dict(n=n, piso_views=piso_views, fator=fator, amostra=amostra,
                     portes=['pequeno', 'médio'], categorias=['Conteúdo', 'Conteúdo + quem fala'], minimo_canais=2),
                     mensagem=f'só {len(pautas)} assuntos passaram no filtro desta rodada' if len(pautas) < n else f'{n} assuntos selecionados nesta rodada',
                     pautas=pautas[:n], sinais_fracos=sorted(fracos, key=chave), fora_do_metodo=sorted(fora, key=chave),
                     peso_do_conteudo=contexto, etapas=ETAPAS)
    # Nichos também são entrada externa: não permitir que carreguem uma fonte.
    from checa_sem_fonte import termos_de
    fontes = termos_de(dados)
    def limpar(obj):
        if isinstance(obj, str):
            for fonte in sorted(fontes, key=len, reverse=True):
                obj = re.sub(re.escape(fonte), '[fonte omitida]', obj, flags=re.I)
            return re.sub(r'https?://\S+', '[link omitido]', obj)
        if isinstance(obj, list):
            return [limpar(v) for v in obj]
        if isinstance(obj, dict):
            return {k: limpar(v) for k, v in obj.items()}
        return obj
    return limpar(resultado)


def render_md(r):
    f = r['filtro']
    linhas = ['# Pautas sem rosto', '', f"Data do radar: {r['gerado_em']}", '', r['mensagem'] + '.', '',
              f"Filtro: conteúdo ou conteúdo + quem fala; porte pequeno/médio; fator ≥ {br(f['fator'], 1)}×; views ≥ {br(f['piso_views'])}; amostra ≥ {br(f['amostra'])}; pelo menos 2 canais; até {br(f['n'])} pautas.", '',
              'O radar mostra uma chance, sem promessa de dinheiro ou views.', '', '## Peso do conteúdo', '']
    linhas += [f'- {s}.' for s in r['peso_do_conteudo']] or ['Sem dados nesta rodada.']
    def seguro(s):
        return str(s).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').replace('<', '&lt;').replace('>', '&gt;')
    for i, p in enumerate(r['pautas'], 1):
        linhas += ['', f"## {i}. {seguro(p['assunto'])}", '', p['por_que'], '',
                   '| Vídeos | Canais | Fator máximo | Views somadas | Idade mediana (h) |', '| --- | --- | --- | --- | --- |',
                   f"| {br(p['videos'])} | {br(p['canais'])} | {br(p['fator_max'], 1)}× | {br(p['views_somadas'])} | {br(p['idade_mediana_h'], 1)} |", '',
                   '**Formato:** ' + p['formato_sem_rosto'] + '.', '', '**Cuidado:** ' + p['cuidado']]
    for chave, titulo in [('sinais_fracos', 'Sinais fracos'), ('fora_do_metodo', 'Fora do método')]:
        linhas += ['', '## ' + titulo, '']
        for p in r[chave]:
            linhas += [f"- {seguro(p['assunto'])}: {br(p['videos'])} vídeos; {br(p['canais'])} canais; mediana {br(p['fator_mediano'], 1)}×; máximo {br(p['fator_max'], 1)}×; {br(p['views_somadas'])} views; {p['faixa_mais_comum']}; idade mediana {br(p['idade_mediana_h'], 1)} h." + (' ' + p['motivo'] if 'motivo' in p else '')]
        if not r[chave]:
            linhas.append('Nenhum nesta rodada.')
    linhas += ['', '## As 5 etapas', ''] + [f'{i}. {s}.' for i, s in enumerate(r['etapas'], 1)]
    return '\n'.join(linhas) + '\n'


def positivo(texto):
    valor = float(texto)
    if not math.isfinite(valor) or valor <= 0:
        raise argparse.ArgumentTypeError('use um número positivo')
    return valor


def inteiro(texto):
    valor = int(texto)
    if valor <= 0:
        raise argparse.ArgumentTypeError('use um inteiro positivo')
    return valor


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('caminho', nargs='?', default=None)
    parser.add_argument('--saida', default='saida')
    parser.add_argument('--n', type=inteiro, default=10)
    parser.add_argument('--piso-views', type=inteiro, default=1000)
    parser.add_argument('--fator', type=positivo, default=3)
    parser.add_argument('--amostra', type=inteiro, default=5)
    parser.add_argument('--detalhes', action='store_true')
    args = parser.parse_args(argv)
    try:
        dados = carregar(args.caminho or achar_radar())
        resultado = montar_pautas(dados, args.n, args.piso_views, args.fator, args.amostra)
        pasta = Path(args.saida).expanduser()
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / 'pautas.md').write_text(render_md(resultado), encoding='utf-8')
        (pasta / 'pautas.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        privado = pasta / 'detalhes-PRIVADO.md'
        if args.detalhes:
            linhas = ['# PRIVADO — não publique este arquivo', '']
            grupos = agrupar(filtrar(dados.get('videos', []), args.piso_views, args.fator, args.amostra))
            for (nicho, tema), videos in grupos.items():
                linhas += [f'## {tema} em {nicho}', '']
                linhas += [f"- {v.get('titulo') or '(sem título)'} — {v.get('canal') or '(sem canal)'}" for v in videos]
            privado.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
            privado.chmod(0o600)
        print(resultado['mensagem'] + '.')
        f = resultado['filtro']
        print(f"Filtro: pequeno/médio, conteúdo; fator ≥ {br(f['fator'], 1)}×; views ≥ {br(f['piso_views'])}; amostra ≥ {br(f['amostra'])}; ≥ 2 canais.")
        print('Relatórios pautas.md e pautas.json gravados.')
        if args.detalhes or privado.exists():
            print('Há detalhes privados: não publique este arquivo.')
        return 0
    except FileNotFoundError:
        print('Dados ou dicionário não encontrados. O radar youtube-bombando grava o arquivo em <pasta do radar>/painel/dados.json '
              '(depois da primeira coleta). Procurei em: ' + ', '.join(str(c) for c in CANDIDATOS) + '. '
              'Passe o caminho, ex.: python3 pautas.py ../youtube-bombando/painel/dados.json. '
              'Para testar sem o radar: python3 pautas.py exemplos/dados-sintetico.json', file=sys.stderr)
    except (OSError, ValueError, TypeError, AttributeError):
        print('Não foi possível ler os dados ou gravar os arquivos. Confira o JSON, o dicionário e as permissões.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Procura referências de terceiros sem revelar o texto completo."""
import argparse
import json
from pathlib import Path
import sys
import unicodedata

EXTENSOES = {'.md', '.json', '.html', '.txt', '.py', '.yaml', '.srt'}
STOPWORDS = {'sobre', 'todos', 'todas', 'como', 'para', 'canal', 'video', 'videos', 'conteudo', 'youtube', 'chatgpt', 'inteligencia artificial'}


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.casefold()) if unicodedata.category(c) != 'Mn')


def termos_de(dados):
    temas = json.loads(Path(__file__).with_name('temas.json').read_text(encoding='utf-8'))
    comuns = STOPWORDS | {normalizar(p) for t in temas for p in t['palavras']}
    # Os nichos são escolha do próprio usuário (config do radar), não fonte de terceiro:
    # um canal chamado igual a um produto ("Claude") não pode apagar o nicho "claude code".
    nichos = {n for n in dados.get('nichos', []) if isinstance(n, str)}
    nichos |= {n for v in dados.get('videos', []) if isinstance(v, dict) for n in (v.get('nichos') or []) if isinstance(n, str)}
    # Só as palavras de nicho com 2+ palavras; um nicho igual ao nome de um canal continua sendo fonte.
    comuns |= {normalizar(w) for n in nichos if len(n.split()) > 1 for w in n.split()}
    return {valor.strip() for v in dados.get('videos', []) if isinstance(v, dict)
            for campo in ('canal', 'titulo', 'pessoa', 'id', 'channel_id')
            for valor in [v.get(campo)] if isinstance(valor, str) and len(valor.strip()) >= 5
            and normalizar(valor.strip()) not in comuns}


def arquivos_de(caminhos):
    encontrados = set()
    for caminho in caminhos:
        raiz = Path(caminho)
        if not raiz.exists():
            raise FileNotFoundError
        for p in (raiz.rglob('*') if raiz.is_dir() else [raiz]):
            if '.git' in p.parts or p.name == 'detalhes-PRIVADO.md' or p.is_symlink():
                continue
            if p.is_file() and p.suffix.lower() in EXTENSOES:
                encontrados.add(p)
    return sorted(encontrados)


def verificar(dados, caminhos):
    termos = sorted(termos_de(dados), key=str.casefold)
    achados = []
    for arquivo in arquivos_de(caminhos):
        for linha, texto in enumerate(arquivo.read_text(encoding='utf-8').splitlines(), 1):
            for termo in termos:
                if termo.casefold() in texto.casefold():
                    achados.append((arquivo, linha, termo[0] + '***' + termo[-1]))
    return achados


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dados')
    p.add_argument('caminhos', nargs='+')
    args = p.parse_args(argv)
    radar = Path(args.dados).expanduser()
    if not radar.is_file():
        print(f'Não achei o arquivo do radar: {radar}. O radar youtube-bombando grava em <pasta do radar>/painel/dados.json '
              '(ex.: ../youtube-bombando/painel/dados.json ou ~/projetos/youtube-bombando/painel/dados.json).', file=sys.stderr)
        return 2
    faltam = [c for c in args.caminhos if not Path(c).exists()]
    if faltam:
        print('Não achei: ' + ', '.join(faltam), file=sys.stderr)
        return 2
    try:
        dados = json.loads(radar.read_text(encoding='utf-8'))
        achados = verificar(dados, args.caminhos)
    except (OSError, ValueError, AttributeError, TypeError):
        print(f'Não foi possível verificar: {radar} não é um dados.json válido do radar, ou um arquivo não é texto.', file=sys.stderr)
        return 2
    for arquivo, linha, termo in achados:
        print(f'{arquivo}:{linha}:{termo}')
    if not achados:
        print('nenhuma fonte de terceiro encontrada')
    return int(bool(achados))


if __name__ == '__main__':
    sys.exit(main())

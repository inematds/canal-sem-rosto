# Canal sem rosto com radar

[![Seu canal sem rosto](guia/assets/banner.jpg)](https://inematds.github.io/canal-sem-rosto/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

> Você pode ter um canal sem mostrar o rosto. O que faz ele crescer é o assunto certo, não a câmera.

## O que é

Muita gente quer ter um canal sobre IA, mas não quer aparecer. No nosso radar do YouTube, o que mais puxou as views foi o assunto, não quem aparece. O **canal sem rosto com radar** é um método em 5 etapas e um kit grátis: ele lê o radar do que está bombando, separa os assuntos em que canais pequenos e médios furaram a bolha e sugere pautas com os números e um formato sem rosto para cada uma. Você precisa de um computador com Python e do radar [youtube-bombando](https://inematds.github.io/youtube-bombando/guia/) (também grátis). Não há promessa de dinheiro nem de views: o radar mostra uma chance.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/canal-sem-rosto/guia/**

**Sem promessa de dinheiro ou views.** O radar aponta uma chance. Não prova que o assunto causou o resultado, nem garante que ele se repita.

## Instalação

Tenha Git e Python 3.10 ou mais recente. Só usamos a biblioteca padrão: nada de pip, chaves ou chamadas de API. O kit lê um arquivo local.

```bash
git clone https://github.com/inematds/canal-sem-rosto
cd canal-sem-rosto
python3 --version
```

## Uso em 3 comandos

Depois de entrar na pasta:

```bash
python3 pautas.py exemplos/dados-sintetico.json
python3 checa_sem_fonte.py exemplos/dados-sintetico.json saida/pautas.md saida/pautas.json
python3 -m unittest discover -s tests
```

O exemplo é inteiramente inventado. Abra `saida/pautas.md` para ler; `saida/pautas.json` traz os mesmos dados estruturados. Os números no JSON são numéricos; no texto usam vírgula decimal e ponto de milhar.

Para usar seu radar:

```bash
python3 pautas.py
# Ou indique onde salvou o arquivo:
python3 pautas.py /caminho/dados.json --saida saida --n 10 --piso-views 1000 --fator 3 --amostra 5
```

O radar grava o arquivo em `painel/dados.json`, dentro da pasta dele. Sem caminho, o kit procura na pasta ao lado (`../youtube-bombando/painel/dados.json`), em `~/projetos/youtube-bombando/painel/dados.json` e em `~/youtube-bombando/painel/dados.json`. Se não achar, diz onde procurou e termina com código 2. Gere ou baixe os dados pelo [guia do radar](https://inematds.github.io/youtube-bombando/guia/). Mantenha dados reais fora do repositório.

## Como o filtro funciona

- Categoria: Conteúdo ou Conteúdo + quem fala.
- Porte: pequeno ou médio. Porte ausente e canal grande não entram.
- Fator do canal de pelo menos 3×, pelo menos 1.000 views e amostra de pelo menos 5 vídeos.
- Pauta: o mesmo nicho e tema precisa aparecer em pelo menos 2 canais distintos.

O fator compara um vídeo com a mediana dos vídeos recentes do próprio canal. A mediana é o valor do meio da lista ordenada. Assim, um canal grande não ganha apenas por já ter público.

O título só serve para encontrar um tema em `temas.json`. Edite os rótulos e as palavras com cuidado: use assuntos, nunca nomes de fontes. A comparação ignora acentos e maiúsculas e respeita palavras inteiras. Se vários temas casarem, o primeiro vence; temas com `evitar_sem_rosto` têm prioridade e ficam fora do método. Sem casamento, o tema é “geral do nicho”. Um vídeo em dois nichos conta nos dois; não some as pautas como se fossem vídeos únicos.

Ordenação: mais canais, maior fator mediano e mais views somadas. Empates usam o assunto em ordem alfabética. O limite `--n` não é preenchido com sinais fracos. Um único canal fica em `sinais_fracos`; sem identidade de canal também não se forma uma pauta. O identificador do canal tem prioridade; o nome serve de alternativa. Quando há um único ID conhecido para esse nome, os registros são reunidos. Cada registro de vídeo da entrada conta uma vez em cada nicho: use uma exportação sem vídeos duplicados.

Duração: curto abaixo de 8 minutos; médio de 8 até 20; longo acima de 20 até 60; maratona acima de 60. Ausência de duração é mostrada como “sem duração”. Empates na faixa mais comum usam essa ordem, com a faixa desconhecida por último. O peso do conteúdo usa o percentual fornecido pelo radar, sem recalcular nem inferir uma causa.

## As 5 etapas

1. [Escolher o assunto](metodo/1-escolher-assunto.md).
2. [Escrever um roteiro com gancho](metodo/2-roteiro-com-gancho.md).
3. [Produzir sem rosto com autoria](metodo/3-producao-sem-rosto.md).
4. [Publicar](metodo/4-publicar.md).
5. [Medir de novo](metodo/5-medir-no-radar.md).

Veja o [método completo](metodo/README.md) e as [regras do YouTube conferidas em 13/11/2026](metodo/regras-youtube.md).

## O processo, do início ao fim

1. 🧠 **Você:** escolha um assunto amplo e gere/baixe `dados.json` na ferramenta do [radar](https://inematds.github.io/youtube-bombando/guia/).
2. ⚙️ **Script:** execute `python3 pautas.py /caminho/dados.json`. Leia os números em `saida/pautas.md`.
3. 🧠 **Você:** escolha uma pauta com pelo menos dois canais. Escreva uma dor, uma promessa e um teste próprio no seu editor de texto. Siga [o roteiro](metodo/2-roteiro-com-gancho.md).
4. 🧠 **Você:** grave a tela ou desenhe um diagrama, faça o teste e explique com sua narração ou escrita. Use seu gravador de tela e editor de vídeo.
5. ⚙️ **Script:** antes de compartilhar os textos, rode `python3 checa_sem_fonte.py /caminho/dados.json saida/pautas.md saida/pautas.json /caminho/roteiro.txt`.
6. 🧠 **Você:** revise título e miniatura no YouTube Studio e publique numa frequência sustentável.
7. 🧠 **Você:** sete dias depois, inclua seu canal/assunto no radar e gere outra exportação.
8. ⚙️ **Script:** rode `python3 pautas.py /caminho/dados-novos.json --saida saida/rodada-2`. 🧠 **Você:** compare o vídeo com o normal do seu canal e decida o próximo assunto.

## Fontes ficam privadas

Os relatórios públicos não trazem títulos, canais, pessoas, descrições, IDs nem links de vídeos. O terminal traz apenas um resumo e os filtros. O arquivo de entrada permanece no seu computador.

```bash
python3 pautas.py /caminho/dados.json --detalhes
```

Só essa opção grava títulos e canais em `saida/detalhes-PRIVADO.md`, com permissão de leitura/escrita apenas para o dono. **Não publique este arquivo.** Ele serve ao seu estudo. Inclui os grupos que passaram no filtro de vídeo, inclusive sinais fracos e temas excluídos. Uma execução posterior sem a opção não apaga o arquivo privado anterior; o terminal avisa se ele ainda existe.

O verificador procura strings inteiras, ignorando maiúsculas, em `.md`, `.json`, `.html`, `.txt`, `.py`, `.yaml` e `.srt`. Pastas são percorridas recursivamente; `.git`, links simbólicos e arquivos chamados `detalhes-PRIVADO.md` são ignorados. Termos com menos de 5 caracteres e palavras comuns do dicionário/stopwords são ignorados. Ele não reconhece paráfrases nem substitui sua revisão. Código 0: limpo; 1: encontrou fonte, com texto mascarado; 2: erro de leitura. Ao checar o repositório inteiro, a própria entrada sintética será apontada: ela contém as fontes inventadas de propósito. Confira os arquivos que pretende publicar.

## Exemplo e manutenção

[Veja o relatório sintético](exemplos/pautas-exemplo.md). Para regenerá-lo:

```bash
python3 pautas.py exemplos/dados-sintetico.json --saida saida/exemplo
cp saida/exemplo/pautas.md exemplos/pautas-exemplo.md
python3 checa_sem_fonte.py exemplos/dados-sintetico.json exemplos/pautas-exemplo.md
python3 -m unittest discover -s tests
```

## Licença

[MIT](LICENSE), inematds, 2026. Versão [1.0.0](VERSION).

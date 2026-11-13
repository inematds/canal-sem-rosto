# Faceless channel with a radar

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![Your faceless channel](guia/assets/banner-en.jpg)](https://inematds.github.io/canal-sem-rosto/guia/en/)

> You can have a channel without showing your face. What makes it grow is the right topic, not the camera.

## What it is

Many people want to have a channel about AI but don’t want to appear on camera. In our YouTube radar, the topic drove the most views, not who appeared. The **faceless channel with a radar** is a 5-step method and a free kit: it reads the radar of what’s trending, identifies topics where small and medium-sized channels broke through, and suggests ideas with the numbers and a faceless format for each one. You need a computer with Python and the [youtube-bombando](https://inematds.github.io/youtube-bombando/guia/) radar (also free). There’s no promise of money or views: the radar shows an opportunity.

## 📖 User guide

Complete guide (landing page + step-by-step instructions): **https://inematds.github.io/canal-sem-rosto/guia/en/**

**No promise of money or views.** The radar points to an opportunity. It doesn’t prove that the topic caused the result, or guarantee that it will happen again.

## Installation

Have Git and Python 3.10 or later. We use only the standard library: no pip, keys, or API calls. The kit reads a local file.

```bash
git clone https://github.com/inematds/canal-sem-rosto
cd canal-sem-rosto
python3 --version
```

## Use in 3 commands

After entering the folder:

```bash
python3 pautas.py exemplos/dados-sintetico.json
python3 checa_sem_fonte.py exemplos/dados-sintetico.json saida/pautas.md saida/pautas.json
python3 -m unittest discover -s tests
```

The example is entirely made up. Open `saida/pautas.md` to read it; `saida/pautas.json` contains the same data in structured form. The numbers in the JSON are numeric; in the text, decimals use commas and thousands use periods.

To use your radar:

```bash
python3 pautas.py
# Or specify where you saved the file:
python3 pautas.py /caminho/dados.json --saida saida --n 10 --piso-views 1000 --fator 3 --amostra 5
```

The radar saves the file in `painel/dados.json`, inside its folder. Without a path, the kit looks in the neighboring folder (`../youtube-bombando/painel/dados.json`), in `~/projetos/youtube-bombando/painel/dados.json`, and in `~/youtube-bombando/painel/dados.json`. If it can’t find it, it tells you where it looked and exits with code 2. Generate or download the data using the [radar guide](https://inematds.github.io/youtube-bombando/guia/). Keep real data outside the repository.

## How the filter works

- Category: Content or Content + speaker.
- Size: small or medium. Channels with no size specified and large channels are excluded.
- Channel factor of at least 3×, at least 1,000 views, and a sample of at least 5 videos.
- Topic: the same niche and topic must appear in at least 2 distinct channels.

The factor compares a video with the median of the channel’s recent videos. The median is the middle value in a sorted list. This way, a large channel doesn’t win simply because it already has an audience.

The title is used only to find a topic in `temas.json`. Edit labels and words carefully: use topics, never source names. Matching ignores accents and capitalization and respects whole words. If multiple topics match, the first one wins; topics with `evitar_sem_rosto` have priority and are excluded from the method. If nothing matches, the topic is “general niche.” A video in two niches counts in both; don’t add up topics as if they were unique videos.

Sort order: more channels, higher median factor, and more total views. Ties are broken by topic in alphabetical order. The `--n` limit isn’t filled with weak signals. A single channel goes in `sinais_fracos`; without a channel identity, no topic is formed either. The channel ID takes priority; the name is used as a fallback. When there is a single known ID for that name, the records are grouped together. Each video record in the input counts once in each niche: use an export without duplicate videos.

Duration: short is under 8 minutes; medium is from 8 to 20; long is over 20 to 60; marathon is over 60. Missing duration is shown as “no duration.” Ties for the most common range use this order, with the unknown range last. Content weight uses the percentage provided by the radar, without recalculating it or inferring a cause.

## The 5 steps

1. [Choose the topic](metodo/1-escolher-assunto.md).
2. [Write a script with a hook](metodo/2-roteiro-com-gancho.md).
3. [Produce faceless content with original work](metodo/3-producao-sem-rosto.md).
4. [Publish](metodo/4-publicar.md).
5. [Measure again](metodo/5-medir-no-radar.md).

See the [complete method](metodo/README.md) and the [YouTube rules checked on 13/11/2026](metodo/regras-youtube.md).

## The process, from start to finish

1. 🧠 **You:** choose a broad topic and generate/download `dados.json` in the [radar](https://inematds.github.io/youtube-bombando/guia/) tool.
2. ⚙️ **Script:** run `python3 pautas.py /caminho/dados.json`. Read the numbers in `saida/pautas.md`.
3. 🧠 **You:** choose a topic with at least two channels. Write a problem, a promise, and your own test in your text editor. Follow [the script guide](metodo/2-roteiro-com-gancho.md).
4. 🧠 **You:** record your screen or draw a diagram, run the test, and explain it with your narration or writing. Use your screen recorder and video editor.
5. ⚙️ **Script:** before sharing the text, run `python3 checa_sem_fonte.py /caminho/dados.json saida/pautas.md saida/pautas.json /caminho/roteiro.txt`.
6. 🧠 **You:** review the title and thumbnail in YouTube Studio and publish at a sustainable pace.
7. 🧠 **You:** seven days later, add your channel/topic to the radar and generate another export.
8. ⚙️ **Script:** run `python3 pautas.py /caminho/dados-novos.json --saida saida/rodada-2`. 🧠 **You:** compare the video with your channel’s usual performance and decide on the next topic.

## Keep sources private

Public reports don’t include titles, channels, people, descriptions, IDs, or video links. The terminal shows only a summary and the filters. The input file stays on your computer.

```bash
python3 pautas.py /caminho/dados.json --detalhes
```

Only this option saves titles and channels to `saida/detalhes-PRIVADO.md`, with read/write permissions for the owner only. **Don’t publish this file.** It’s for your own study. It includes groups that passed the video filter, including weak signals and excluded topics. A later run without the option doesn’t delete the previous private file; the terminal will tell you if it still exists.

The checker searches for whole strings, ignoring capitalization, in `.md`, `.json`, `.html`, `.txt`, `.py`, `.yaml`, and `.srt` files. It searches folders recursively; `.git`, symbolic links, and files named `detalhes-PRIVADO.md` are ignored. Terms shorter than 5 characters and common dictionary words/stop words are ignored. It doesn’t recognize paraphrases or replace your review. Code 0: clean; 1: source found, with text masked; 2: read error. When checking the entire repository, the synthetic input itself will be flagged: it intentionally contains made-up sources. Check the files you plan to publish.

## Example and maintenance

[See the synthetic report](exemplos/pautas-exemplo.md). To regenerate it:

```bash
python3 pautas.py exemplos/dados-sintetico.json --saida saida/exemplo
cp saida/exemplo/pautas.md exemplos/pautas-exemplo.md
python3 checa_sem_fonte.py exemplos/dados-sintetico.json exemplos/pautas-exemplo.md
python3 -m unittest discover -s tests
```

## License

[MIT](LICENSE), inematds, 2026. Version [1.0.0](VERSION).

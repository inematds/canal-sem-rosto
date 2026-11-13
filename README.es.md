# Canal sin rostro con radar

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

[![Tu canal sin rostro](guia/assets/banner-es.jpg)](https://inematds.github.io/canal-sem-rosto/guia/es/)

> Puedes tener un canal sin mostrar tu rostro. Lo que lo hace crecer es el tema adecuado, no la cámara.

## Qué es

Mucha gente quiere tener un canal sobre IA, pero no quiere aparecer. En nuestro radar de YouTube, lo que más impulsó las vistas fue el tema, no quién aparece. El **canal sin rostro con radar** es un método de 5 etapas y un kit gratis: lee el radar de lo que está en auge, separa los temas en los que canales pequeños y medianos rompieron la burbuja y sugiere ideas con los números y un formato sin rostro para cada una. Necesitas una computadora con Python y el radar [youtube-bombando](https://inematds.github.io/youtube-bombando/guia/) (también gratis). No hay promesa de dinero ni de vistas: el radar muestra una oportunidad.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/canal-sem-rosto/guia/es/**

🎬 Video (en portugués): https://www.youtube.com/watch?v=HqBKgxhUHak · Short: https://youtube.com/shorts/LQY5YGVvTHE

**Sin promesa de dinero ni de vistas.** El radar señala una oportunidad. No prueba que el tema haya causado el resultado ni garantiza que se repita.

## Instalación

Ten Git y Python 3.10 o una versión más reciente. Solo usamos la biblioteca estándar: nada de pip, claves ni llamadas a API. El kit lee un archivo local.

```bash
git clone https://github.com/inematds/canal-sem-rosto
cd canal-sem-rosto
python3 --version
```

## Uso en 3 comandos

Después de entrar en la carpeta:

```bash
python3 pautas.py exemplos/dados-sintetico.json
python3 checa_sem_fonte.py exemplos/dados-sintetico.json saida/pautas.md saida/pautas.json
python3 -m unittest discover -s tests
```

El ejemplo es completamente inventado. Abre `saida/pautas.md` para leerlo; `saida/pautas.json` contiene los mismos datos estructurados. Los números del JSON son numéricos; en el texto usan coma decimal y punto de miles.

Para usar tu radar:

```bash
python3 pautas.py
# O indica dónde guardaste el archivo:
python3 pautas.py /caminho/dados.json --saida saida --n 10 --piso-views 1000 --fator 3 --amostra 5
```

El radar guarda el archivo en `painel/dados.json`, dentro de su carpeta. Si no indicas una ruta, el kit busca en la carpeta contigua (`../youtube-bombando/painel/dados.json`), en `~/projetos/youtube-bombando/painel/dados.json` y en `~/youtube-bombando/painel/dados.json`. Si no lo encuentra, indica dónde buscó y termina con el código 2. Genera o descarga los datos siguiendo la [guía del radar](https://inematds.github.io/youtube-bombando/guia/). Mantén los datos reales fuera del repositorio.

## Cómo funciona el filtro

- Categoría: Contenido o Contenido + quién habla.
- Tamaño: pequeño o mediano. Si falta el tamaño o el canal es grande, no se incluye.
- Factor del canal de al menos 3×, al menos 1.000 vistas y una muestra de al menos 5 videos.
- Tema: el mismo nicho y tema deben aparecer en al menos 2 canales distintos.

El factor compara un video con la mediana de los videos recientes del propio canal. La mediana es el valor central de la lista ordenada. Así, un canal grande no gana solo por tener ya una audiencia.

El título solo sirve para encontrar un tema en `temas.json`. Edita las etiquetas y las palabras con cuidado: usa temas, nunca nombres de fuentes. La comparación ignora tildes y mayúsculas y respeta las palabras completas. Si coinciden varios temas, gana el primero; los temas con `evitar_sem_rosto` tienen prioridad y quedan fuera del método. Si no hay coincidencias, el tema será «general del nicho». Un video en dos nichos cuenta en ambos; no sumes los temas como si fueran videos únicos.

Orden: más canales, mayor factor mediano y más vistas sumadas. En caso de empate, los temas se ordenan alfabéticamente. El límite `--n` no se completa con señales débiles. Un solo canal queda en `sinais_fracos`; sin identidad de canal tampoco se forma un tema. El identificador del canal tiene prioridad; el nombre sirve como alternativa. Cuando hay un único ID conocido para ese nombre, los registros se agrupan. Cada registro de video de la entrada cuenta una vez en cada nicho: usa una exportación sin videos duplicados.

Duración: corto, menos de 8 minutos; mediano, de 8 a 20; largo, más de 20 hasta 60; maratón, más de 60. Si falta la duración, se muestra como «sin duración». En caso de empate en el rango más común, se usa este orden, con el rango desconocido al final. El peso del contenido usa el porcentaje proporcionado por el radar, sin recalcularlo ni inferir una causa.

## Las 5 etapas

1. [Elegir el tema](metodo/1-escolher-assunto.md).
2. [Escribir un guion con gancho](metodo/2-roteiro-com-gancho.md).
3. [Producir sin mostrar el rostro y con autoría](metodo/3-producao-sem-rosto.md).
4. [Publicar](metodo/4-publicar.md).
5. [Volver a medir](metodo/5-medir-no-radar.md).

Consulta el [método completo](metodo/README.md) y las [reglas de YouTube verificadas el 13/11/2026](metodo/regras-youtube.md).

## El proceso, de principio a fin

1. 🧠 **Tú:** elige un tema amplio y genera/descarga `dados.json` en la herramienta del [radar](https://inematds.github.io/youtube-bombando/guia/).
2. ⚙️ **Script:** ejecuta `python3 pautas.py /caminho/dados.json`. Lee los números en `saida/pautas.md`.
3. 🧠 **Tú:** elige un tema con al menos dos canales. Escribe un problema, una promesa y una prueba propia en tu editor de texto. Sigue [el guion](metodo/2-roteiro-com-gancho.md).
4. 🧠 **Tú:** graba la pantalla o dibuja un diagrama, haz la prueba y explícalo con tu narración o escritura. Usa tu grabador de pantalla y editor de video.
5. ⚙️ **Script:** antes de compartir los textos, ejecuta `python3 checa_sem_fonte.py /caminho/dados.json saida/pautas.md saida/pautas.json /caminho/roteiro.txt`.
6. 🧠 **Tú:** revisa el título y la miniatura en YouTube Studio y publica con una frecuencia sostenible.
7. 🧠 **Tú:** siete días después, incluye tu canal/tema en el radar y genera otra exportación.
8. ⚙️ **Script:** ejecuta `python3 pautas.py /caminho/dados-novos.json --saida saida/rodada-2`. 🧠 **Tú:** compara el video con lo habitual en tu canal y decide el siguiente tema.

## Las fuentes son privadas

Los informes públicos no incluyen títulos, canales, personas, descripciones, ID ni enlaces a videos. La terminal solo muestra un resumen y los filtros. El archivo de entrada permanece en tu computadora.

```bash
python3 pautas.py /caminho/dados.json --detalhes
```

Solo esta opción guarda títulos y canales en `saida/detalhes-PRIVADO.md`, con permisos de lectura y escritura únicamente para el dueño. **No publiques este archivo.** Sirve para tu estudio. Incluye los grupos que pasaron el filtro de video, incluso las señales débiles y los temas excluidos. Una ejecución posterior sin la opción no borra el archivo privado anterior; la terminal avisa si aún existe.

El verificador busca cadenas completas, ignorando mayúsculas, en `.md`, `.json`, `.html`, `.txt`, `.py`, `.yaml` y `.srt`. Recorre las carpetas de forma recursiva; ignora `.git`, los enlaces simbólicos y los archivos llamados `detalhes-PRIVADO.md`. Ignora los términos de menos de 5 caracteres y las palabras comunes del diccionario/listas de palabras vacías. No reconoce paráfrasis ni sustituye tu revisión. Código 0: limpio; 1: encontró una fuente, con el texto oculto; 2: error de lectura. Al revisar todo el repositorio, se señalará la propia entrada sintética: contiene fuentes inventadas a propósito. Revisa los archivos que pretendes publicar.

## Ejemplo y mantenimiento

[Consulta el informe sintético](exemplos/pautas-exemplo.md). Para volver a generarlo:

```bash
python3 pautas.py exemplos/dados-sintetico.json --saida saida/exemplo
cp saida/exemplo/pautas.md exemplos/pautas-exemplo.md
python3 checa_sem_fonte.py exemplos/dados-sintetico.json exemplos/pautas-exemplo.md
python3 -m unittest discover -s tests
```

## Licencia

[MIT](LICENSE), inematds, 2026. Versión [1.0.0](VERSION).

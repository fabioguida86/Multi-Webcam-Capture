# Multi Webcam Capture

Multi Webcam Capture è un'applicazione desktop per Windows che scatta foto in automatico da più webcam contemporaneamente.

Per ogni webcam si sceglie ogni quanti secondi scattare, per quanti minuti, in quale cartella salvare le immagini e con quale nome. Il programma imposta da solo la risoluzione più alta supportata da ogni webcam e mostra un'anteprima dal vivo di tutte le inquadrature.

È utile per time-lapse, monitoraggio di esperimenti o cantieri e per raccogliere immagini da più punti di vista.

## Download

Se non usi Python, scarica il file `MVC_1.0.exe` dalla sezione **Releases** di questo repository e avvialo: non serve installazione.

## Avvio da codice sorgente

Requisiti: Python 3.9 o successivo.

```bash
pip install -r requirements.txt
python MVC_1.0.py
```

## Come si usa

1. Inserisci il numero di webcam da usare e premi **Configura webcam**.
2. Per ogni webcam compila i campi:
   - **Indice webcam**: il numero della webcam nel sistema (`0` per la prima, `1` per la seconda, e così via).
   - **Intervallo (sec)**: i secondi tra uno scatto e il successivo.
   - **Durata (min)**: per quanti minuti continuare a scattare.
   - **Cartella**: dove salvare le foto (viene creata se non esiste).
   - **Nome immagini**: il nome base dei file. Le foto vengono salvate come `nome_1.jpg`, `nome_2.jpg`, …
3. Con **Attiva anteprima** controlli le inquadrature. Premi **Stop anteprima** prima di avviare l'acquisizione.
4. Premi **Avvia tutte** per iniziare. L'acquisizione si ferma da sola alla fine della durata impostata, oppure con **Stop tutte**.

## Creare l'eseguibile

```bash
pip install pyinstaller
pyinstaller MVC_1.0.spec
```

L'eseguibile viene creato nella cartella `dist/`.

## Tecnologie

Python, OpenCV, Tkinter, Pillow.

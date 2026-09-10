# Vishnu Purana source record

## Reading text

- **Edition:** *The Vishnu Purana*, translated by Manmatha Nath Dutt, Elysium Press, Calcutta, 1896.
- **Transcription:** [Project Gutenberg eBook #66208](https://www.gutenberg.org/ebooks/66208).
- **Rights status:** Public domain. Dutt died in 1912; Project Gutenberg distributes this edition as a public-domain eBook in the United States.
- **Local raw-file SHA-256:** `924d8c109ddf87a26fab4025556be7b74dbf0c21534e253bfb4561f711956bb5`.

The generated `vishnu-purana.json` contains every one of the edition's 6 parts and 126 sections. Body paragraphs and all 259 referenced translator's notes are retained. Line wrapping is removed; the prose is not summarized or modernized.

The story titles and synopses come from the same edition's printed table of contents. They are displayed as a **source reading guide**, never as canonical text. Section numbers are assigned from body order because the printed contents contains two obvious numbering defects in Part V.

## Sanskrit witness

- **Edition:** Jīvānanda Vidyāsāgara/Bhattacharya Sanskrit edition with Śrīdhara's commentary, 1882.
- **Scan:** [Digital Library of India / Internet Archive](https://archive.org/details/in.ernet.dli.2015.486983).
- **Catalogued rights status:** `Public Domain`.
- **Local OCR-file SHA-256:** `46022d9f069b4503b2fb8e8a2b3431f9561cb0df0726b96d464c66f23c9cfa15`.

The archive's machine OCR is too corrupt for responsible scripture display. Gyan Sutra therefore links the page images as the Sanskrit witness and withholds the OCR transcription until it can be checked page by page. No generated Sanskrit is substituted.

## Rebuilding and indexing

Raw downloads live under the git-ignored `data/raw/vishnu-purana/` directory. With `dutt-1894.txt` present:

```sh
node scripts/prepare_vishnu_purana.js
npm run ingest:vishnu
```

The first command deterministically rebuilds the reading dataset. The second creates stable section records plus passage-sized vector records for Sarathi's cited retrieval.

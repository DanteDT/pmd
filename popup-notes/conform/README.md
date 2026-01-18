## Conformant syntax for popup footnotes

The (X)HTML syntax *conforms* to a known standard like [EPUB 3.3](https://www.w3.org/TR/epub-33/).

If you are interested in epub files that *work* using *non-conformant* syntax, see [work](../work)

### Conventions

The filename indicates the `EPUB-SPEC` prefix.

`OEBPS/content.opf` metadata confirms the OS and Software that work, using `<dc:subject>OS v, Software v</dc:subject>`

For example, [EPUB33+Popup+Footnotes+-+Power+Lit.epub](./EPUB33+Popup+Footnotes+-+Power+Lit.epub) pops up notes correctly using conformant syntax:
* EPUB 3.3 conformant syntax
  * `EPUB33` filename prefix
  *  `<dc:subject>EPUB 3.3 Popup footnotes using noteref / footnote epub types</dc:subject>`
* Windows 11, using Calibre 8
  * `<dc:subject>Windows 11, Calibre 8</dc:subject>` in the content.opf
* Android 17, using Lithium 0.24
  *  `<dc:subject>Android 17, Lithium 0.24</dc:subject>`

[EpubCheck](https://pypi.org/project/epubcheck/) confirm validity of the file, as reported in [EPUB33+Popup+Footnotes.xls](./EPUB33+Popup+Footnotes.xls)

It may not work for some OS-Software combinations like
* Android-Readera
* Kobo Libra Colour

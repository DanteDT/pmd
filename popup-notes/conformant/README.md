## *Conformant* popup notes work on these files

The (X)HTML syntax *works* and *is conform* to a known standard like [EPUB 3.3](https://www.w3.org/TR/epub-33/).

If you are interested in *working* but *non-conformant* files, see [working](../working)

### Naming convention

The filename indicates
* `EPUB-SPEC` prefix
* `OS-Software <, OS-Software>*` that pops up footnotes correctly, for a great reading experience.

`OEBPS/content.opf` metadata confirms the same in entries like `<dc:subject>OS v, Software v</dc:subject>`

#### OS abbreviations
* WIN, Windows
* AND, Android
* IOS, iOS

For example, [Working-popup-note+-+WIN-Calibre+AND-Lithium.epub](./Working-popup-note+-+WIN-Calibre+AND-Lithium.epub) pops up notes correctly with conformant syntax:
* EPUB 3.3 conformant syntax
  * `EPUB33` filename prefix
  *  `<dc:subject>EPUB 3.3 noteref / footnote conformant popup notes</dc:subject>`
* Windows 11, using Calibre 8
  * `WIN-Calibre` in the filename
  * `<dc:subject>Windows 11, Calibre 8</dc:subject>` in the content.opf
* Android 17, using Lithium 0.24
  *  `AND-Lithium`
  *  `<dc:subject>Android 17, Lithium 0.24</dc:subject>`

It does not work for some OS-Software combinations like
* Android-Readera
* Kobo Libra Colour

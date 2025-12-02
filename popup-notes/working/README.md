## Popup notes work on these files

The (X)HTML syntax *works* but may *not conform* to any known standard like [EPUB 3.3](https://www.w3.org/TR/epub-33/).

If it works *and* conforms to a published spec, the file belongs in [conformant](../conformant)

### Naming convention

The filename indicates `OS-Software <, OS-Software>*` that pops up footnotes correctly, for a great reading experience.

`OEBPS/content.opf` metadata confirms the same in entries like `<dc:subject>OS v, Software v</dc:subject>`

#### OS abbreviations
* WIN, Windows
* AND, Android
* IOS, iOS

For example, [Working-popup-note+-+WIN-Calibre+AND-Lithium.epub](./Working-popup-note+-+WIN-Calibre+AND-Lithium.epub) pops up notes correctly on
* Windows 11, using Calibre 8
  * `WIN-Calibre` in the filename
  * `<dc:subject>Windows 11, Calibre 8</dc:subject>` in the content.opf
* Android 17, using Lithium 0.24
  *  `AND-Lithium`
  *  `<dc:subject>Android 17, Lithium 0.24</dc:subject>`

It does not work for some OS-Software combinations like
* Android-Readera
* Kobo Libra Colour

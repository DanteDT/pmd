## Power lit

Moby-Dick annotated epub, based on the great efforts of [Power Moby-Dick, The Online Annotation](http://www.powermobydick.com/).
* Highly recommended extras to be found there
  * [Glossary](http://www.powermobydick.com/Moby138.html)
  * [Resources](http://www.powermobydick.com/Moby141.html) including diagrams of whaleships and the surprising background of [How Moby-Dick got his name](http://www.powermobydick.com/Moby147.html)

With front/back material from a [scanned, signed first-edition from the Internet Archive](https://archive.org/details/mobydickorwhale01melv/page/n7/mode/2up).

### Very brief overview
1. Scrape PMD TOC and Chapters
2. Basic HTML clean up, then some deep cleaning and patching to improve the e-reader experience
3. Prep the EPUB content, XHTML chapters
4. Build the EPUB - an edition that uses epub footnotes, and an edition that uses hyperlinks. See below.

I test on epub readers that I have used for a long time, without trying harder for more common devices or apps :
* Windows 11, [Calibre epub reader, validator and builder](https://calibre-ebook.com/) ❤️
* Android tablet, with the reliable [Lithium epub reader](https://play.google.com/store/apps/details?id=com.faultexception.reader&hl=en-US) ❤️
* iPhone, with the spectacular [Readdle Documents](https://readdle.com/documents), although links - not popups. See below.
* *Kobo Libra Color [claims to support popup footnotes](https://github.com/kobolabs/epub-spec?tab=readme-ov-file#footnotesendnotes-are-fully-supported-across-kobo-platforms). In fact, Kobo have [struggled for years](https://github.com/kobolabs/epub-spec/issues?q=is%3Aissue%20state%3Aopen%20popup%20OR%20pop-up) to get this right, and still haven't. See below.*

### Why two .epub files? What's the difference?

Unfortunately, e-pub devices and apps support TOC Navigation, and Footnotes in different ways (or not).

To keep this overview minimal, I address technical topics in:
* [TOC navigation](navigation.md), and
* [Footnotes](footnotes.md)

Due to unreliable support for these two essential e-book features by device manufacturers and app developers, your e-reader may work better with
* the **footnote** release (popup footnotes 😃), or
* the **hyperlink** release (functional yet disruptive links back-and-forth between main text and footnotes 😒)

Why is it so hard for device manufacturers and app developers to get this right? I don't know. People get [hard stuff right](https://home.cern/news/news/accelerators/hie-isolde-10-years-10-highlights) all the time.

### Use and Contribute
Suggestions are welcome to improve the annotated Moby-Dick reading experience. Something not work on your e-reader? Please report it.

If you can demonstrate WORKING, or WORKING/CONFORMANT Popup Footnotes or TOC Navigation for a particular scenario, please consider submitting that. See examples that:
* [conform](popup-notes/conform) ... popups work, and syntax **conforms** to a recognized standard, and
* [work](popup-notes/work) ... popups work, although syntax may not conform to any spec.
* *no copyrighted content, please. just simple examples of working syntax, like the ones in those folders.*

To customize your own edition, consider the [config.yaml](config.yaml) setting `debugging: True` to focus a debugging session. The setting `epub_ref: "foot"` produces the Footnote editions; `epub_ref: "link"` produces the hyperlink edition.

### Recognition and attribution

With respect and gratitude for Herman and Margaret. ❤️
* Moby-Dick by Herman Melville is in the public domain.
* All notes in Power Moby-Dick: The Online Annotation copyright 2008 by Margaret Guroff.
* Rendered and released here to common e-book formats with permission.

This is what I can offer.

-- DDT

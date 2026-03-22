## Power lit

Moby-Dick annotated ebook, based on the great efforts of [Power Moby-Dick, The Online Annotation](http://www.powermobydick.com/).
* Highly recommended extras to be found there
  * [Glossary](http://www.powermobydick.com/Moby138.html)
  * [Resources](http://www.powermobydick.com/Moby141.html) including diagrams of whaleships and the surprising background of [How Moby-Dick got his name](http://www.powermobydick.com/Moby147.html)

With front/back material from a [scanned, signed first-edition from the Internet Archive](https://archive.org/details/mobydickorwhale01melv/page/n7/mode/2up).

## Notes about this ebook

- The copyrighted notes in this ebook are used by permission of their author.
- The page images in this ebook from Harper &amp; Brothers' 1851 edition are in the public domain.
- The Rockwell Kent illustrations in this ebook from Lakeside Press' 1930 edition are in the public domain.
- The fonts included in this ebook, [Dante MT](https://en.wikipedia.org/wiki/Dante_(typeface)) and [Charis_SIL](https://en.wikipedia.org/wiki/Charis_SIL), are in the public domain.

## Very brief overview
1. Scrape PMD TOC and Chapters
2. Basic HTML clean up, then some deep cleaning and patching to improve the e-reader experience
3. Prep the EPUB content, XHTML chapters
4. Build the EPUB - an edition that uses epub footnotes, and an edition that uses hyperlinks. See below.

I test on epub readers that I have used for a long time, without trying harder for more common devices or apps :
* Windows 11, [Calibre epub reader, validator and builder](https://calibre-ebook.com/) ❤️
* Android tablet, with the reliable [Lithium epub reader](https://play.google.com/store/apps/details?id=com.faultexception.reader&hl=en-US) ❤️
* iPhone, with the spectacular [Readdle Documents](https://readdle.com/documents), although links - not popups. See below.
* *Kobo Libra Color [claims to support popup footnotes](https://github.com/kobolabs/epub-spec?tab=readme-ov-file#footnotesendnotes-are-fully-supported-across-kobo-platforms). In fact, Kobo have [struggled for years](https://github.com/kobolabs/epub-spec/issues?q=is%3Aissue%20state%3Aopen%20popup%20OR%20pop-up) to get this right, and still haven't. See below.*

## Why two ebook variations? What's the difference?

Unfortunately, ebook readers (devices and apps) support TOC Navigation and Footnotes/Endnotes in different ways (or, often, not).

To keep this overview minimal, I address these technical topics in:
* [TOC navigation](navigation.md), and
* [Footnotes](footnotes.md), and [Endnotes](endnotes.md)

Due to unreliable support for these two essential ebook features by device manufacturers and app developers, your ebook reader may work better with
* the **footnote** release (popup footnotes and endnotes 😃), or
* the **hyperlink** release (functional yet disruptive links back-and-forth between main text and insightful notes 😒)

Why is it so hard for device manufacturers and app developers to get this right? I don't know. People get [hard stuff right](https://home.cern/news/news/accelerators/hie-isolde-10-years-10-highlights) all the time, when they want to.

## Use and Contribute
Suggestions are welcome to improve the annotated Moby-Dick reading experience. Something not work on your e-reader? Please report it.

If you can demonstrate WORKING, or WORKING/CONFORMANT Popup Footnotes or TOC Navigation for a particular scenario, please consider submitting that. See examples that:
* [conform](popup-notes/conform) ... popups work, and syntax **conforms** to a recognized standard, and
* [work](popup-notes/work) ... popups work, although syntax may not conform to any spec.
* *no copyrighted content, please. just simple examples of working syntax, like the ones in those folders.*

 customize your own edition, consider the [config.yaml](config.yaml) setting `debugging: True` to focus a debugging session. The setting `epub_ref: "foot"` produces the Footnote editions; `epub_ref: "link"` produces the hyperlink edition.

## Recognize, attribute, and appreciate

With respect and gratitude for Herman and Margaret. ❤️
* Moby-Dick by Herman Melville is in the public domain.
* All notes in Power Moby-Dick: The Online Annotation copyright 2008 by Margaret Guroff.
  * The copyrighted notes in this ebook are used by permission of their author.

[Standard Ebooks](https://standardebooks.org/about/standard-ebooks-and-the-public-domain) share a beautiful, inspiring sentiment: 
> "The public domain is a priceless resource for all of us, and for the generations after us. It’s a free repository of our culture going back centuries—a way for us to see where we came from and to chart where we’re going. It represents our collective cultural heritage."

This ebook rendering is what I can offer.

-- DDT

## Power lit

Moby-Dick annotated epub, based on the great efforts of [Power Moby-Dick, The Online Annotation](http://www.powermobydick.com/).
* Highly recommended extras to be found there
  * [Glossary](http://www.powermobydick.com/Moby138.html)
  * [Resources](http://www.powermobydick.com/Moby141.html) including the fascinating background on [How Moby-Dick got his name](http://www.powermobydick.com/Moby147.html)

With front/back material from a [scanned, signed first-edition from the Internet Archive](https://archive.org/details/mobydickorwhale01melv/page/n7/mode/2up).

### Very brief overview
1. Scrape PMD TOC and Chapters
2. Basic HTML clean up, then some deep cleaning and patching to improve the e-reader experience
3. Prep the EPUB content, XHTML chapters
4. Build the EPUB

I test on epub readers that I have used for a long time, without trying harder for more common devices or apps :
* Windows 11, [Calibre epub reader, validator and builder](https://calibre-ebook.com/) ❤️
* Android tablet, with the reliable [Lithium epub reader](https://play.google.com/store/apps/details?id=com.faultexception.reader&hl=en-US) ❤️
* iPhone, with the spectacular [Readdle Documents](https://readdle.com/documents), although links - not popups. See below.
* *Kobo Libra Color [claims to support popup footnotes](https://github.com/kobolabs/epub-spec?tab=readme-ov-file#footnotesendnotes-are-fully-supported-across-kobo-platforms). In fact, Kobo have [struggled for years](https://github.com/kobolabs/epub-spec/issues?q=is%3Aissue%20state%3Aopen%20popup%20OR%20pop-up) to get this right, and still haven't. See below.*

### Why two .epub files? What's the difference?

Unfortunately, e-pub devices and readers support notes in different ways (or not):
* as popup [footnotes](https://www.w3.org/TR/epub-ssv-11/#notes), which is a great reading experience, or 
* as **hyperlinks** to non-linear content.
  * Links force the reader to jump around the content - a disruptive, sub-optimal reading experience.
  * Some publishers use hyperlinks; some e-readers treat footnotes as hyperlinks.
  * Both choose to deliver a disruptive, sub-optimal reading experience.

Apparently, few e-readers support popup footnotes. My preferred Windows and Android readers, above, do. If your e-reader does not support popups, you may have better luck with the "hyperlink" EPUB. You won't get popups like:

  * <img src="web/noteref-popup.jpg" height="125px">

If you can demonstrate WORKING, or WORKING/CONFORMANT popup notes for a particular scenario, please consider contributing submitting that. See templates in:
* [working](popup-notes/working) ... popups work, although syntax may not conform to spec, and
* [conformant](popup-notes/conformant) ... popups work, and syntax **conforms** to a recognized standard.
* *no copyrighted content, please. just simple examples of working syntax.*

### Key points from EPUB standards
A few key points from [EPUB 3.3](https://www.w3.org/TR/epub-ssv-11/)
* [skippability and escapability matter](https://www.w3.org/TR/epub-33/#sec-behaviors-skip-escape) and may confuse since, distinct from skippable, escapable items are those "that users might wish to skip" ... 
  * Wait, whaaa... ?!
* Nonetheless, footnotes are skippable. And popups are the best experience to ensure readers don't want to skip them.
* So footnotes matter and are detailed in [EPUB 3 Structural Semantics Vocabulary 1.1, footnotes](https://www.w3.org/TR/epub-ssv-11/#notes) and [noterefs](https://www.w3.org/TR/epub-ssv-11/#links)
  * epub:type="noteref" belongs in HTML `<a>` tags "in the main body of text."
  * epub:type="footnote" belongs in HTML `<aside>` tags to provide the reader "ancillary information ... that provides additional context" to that main text.

The simplest case for popup text notes seems pretty simple:
```
<div id="text">
    <a id="txt01" epub:type="noteref" href="#fn01">
        Main body of text
    </a>
    without the interesting, skippable bits.
</div>
...
<div id="footnotes">
    <aside epub:type="footnote" id="fn01">
        <a href="#txt01">back ↩</a>
        See external info 
        <a href="http://wikipedia.com">on Wikipedia</a>
    </aside>
</div>
```

Why is this hard to get right for devices and apps? I don't know. People get [hard stuff right](https://home.cern/news/news/accelerators/hie-isolde-10-years-10-highlights) all the time.

### Contribute
Suggestions welcome to improve the annotated Moby-Dick epub experience. Something not work on your reader? Please report it.

To customize your own edition, consider the [config.yaml](config.yaml) setting `debugging: True` to focus a debugging session.

With respect and gratitude for Herman and Margaret. ❤️

This is what I can offer.

-- DDT

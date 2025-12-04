## Footnotes 😃 vs. Hyperlinks 😒

Popup [footnotes](https://www.w3.org/TR/epub-ssv-11/#notes) ensure a great, seamless reading experience.

Unfortunately, e-reader devices and apps don't reliaby deliver these.

**Hyperlinks** is a lesser alternative, for readers to access non-linear content that is separate from the main text -- like footnotes and endnotes.

* Links force the reader to jump around the content - a disruptive, sub-optimal reading experience.
* Some e-book publishers use hyperlinks; some e-readers treat well-formed footnotes as hyperlinks.
* Both choose to deliver a disruptive, sub-optimal reading experience.

### Spotty popup support by device manufacturers and app developers

Few e-readers support popup footnotes reliably. My preferred Windows and Android readers, mentioned in the [README](./README.md), do.

If your e-reader does not support popups, you may have better luck with the "hyperlink" epub edition. You won't get popups like:

  * <img src="web/noteref-popup.jpg" height="125px">

### Key points from EPUB standards
A few key points from [EPUB 3.3](https://www.w3.org/TR/epub-ssv-11/)
* [skippability and escapability matter](https://www.w3.org/TR/epub-33/#sec-behaviors-skip-escape) and may confuse since, distinct from skippable, escapable items are those "that users might wish to skip" ... 
  * Wait, whaaa... ?!
* Nonetheless, footnotes are skippable. And popups are the best experience to ensure readers don't want to skip them.
* So footnotes matter and are detailed in [EPUB 3 Structural Semantics Vocabulary 1.1, footnotes](https://www.w3.org/TR/epub-ssv-11/#notes) and [noterefs](https://www.w3.org/TR/epub-ssv-11/#links)
  * epub:type="noteref" belongs in HTML `<a>` tags "in the main body of text."
  * epub:type="footnote" belongs in HTML `<aside>` tags to provide the reader "ancillary information ... that provides additional context" to that main text.

The simplest case for popup notes seems pretty simple:
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
        Skippable details and
        <a href="http://wikipedia.com">more on Wikipedia</a>
    </aside>
</div>
```


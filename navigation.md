## TOC Navigation

EPUB 3.3 specs include [7.3 The nav element: restrictions](https://www.w3.org/TR/epub-33/#sec-nav-def-model).

[Kobo Labs](https://github.com/kobolabs/epub-spec?tab=readme-ov-file#epub3-tocs) share a basic example that their own devices often mishandle:
```
<nav epub:type="toc">
    <h2>Contents</h2>
    <ol>
        <li><a href="title-page.xhtml">Title Page</a></li>
		<li><a href="copyright.xhtml">Copyright</a></li>
		<li><a href="chapter-1.xhtml">Chapter 1</a></li>
		<li><a href="chapter-2.xhtml">Chapter 2</a></li>
		<li><a href="chapter-3.xhtml">Chapter 3</a></li>
    </ol>
</nav>
```

### Spotty support by device manufacturers and app developers
Kobo Libra Colour 4.44.23552 software ver fails to load or fall back to any navigation TOC for multiple epubs from a variety of sources.

Kobo fails to load this PMD epub nav.xhtml structure:

```
<nav epub:type="toc" id="nav">
<h1>Table of Contents</h1>
<ol class="nav-toc">
<li><a href="title.xhtml">Title page</a></li>
<li><a href="ch001.xhtml">Chapter 1</a></li>
<li><a href="ch002.xhtml#sub001">Chapter 2</a><ol class="nav-toc">
    <li><a href="ch002.xhtml#sub002">Subtitle 1</a></li>
    <li><a href="ch002.xhtml#sub003">Subtitle 2</a></li>
</ol></li>
...
</nav>
```

Multiple other devices and apps load and display these TOCs without issue, and they are fully functional for navigation.

If you are in this or a similar scenario, and you can offer a working syntax for your device/app ... or point out my mistake in the PMD epub ... please do so.
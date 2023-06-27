# pdf-stickers

**Should:** Combine pdf stickers to fit them efficiently on regular size page

**Does:** All individual pages from all provided files resize and place on A4 page

- Doesn't ask you preferable size of sticker
- Doesn't ask you preferable paper size
- Doesn't save proportions of the input page
- Works only with A4
- Resizes all pages to size that can fit on A4 page 6 times (Because it's what we need at work)

For now. Of course.

**How:** 
- Use it as a module: `python3 -m app list.pdf of.pdf pdf.pdf files.pdf` or `python3 -m app -f file_path_to_save.pdf -d
/dir/from/which/all/pdfs/will/be/used`

    - options -f and -d are optional
    - if -f is ommited, standard name is used
    - if -d is specified, all pdf files from provided directory is used only

- Import function `compose_stickers`, give it list of file names and file name to save.
- Use carefully designed UI from ui module:
    - run it as module: `python3 -m ui`
    - use run.sh (why not) `chmod u+x run.sh`(x1) and then `./run.sh`(as needed)
    - or even create your .desktop file, as I supposed to, but got lazy.
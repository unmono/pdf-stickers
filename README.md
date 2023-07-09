# pdf-stickers

**Should:** combine .pdf files, so they can be printed on a chosen page size

---

**Does:** resize each page from the input files and arrange them on a page according to the chosen layout.

After you:
- specify how many stickers should be placed across(horizontaly on) the page
- specify how many stickers should be placed down(vertically on) the page
- specify the size of a page
- specify the margins around each sticker if needed. Can be negative.
- allow or disallow it to rotate a page when its original ratio is violated in the chosen layout
- pick files individually or import all .pdf files from selected directories

---

**How:**
- Use it as a module:

    `python3 -m app [OPTIONS] list.pdf of.pdf files.pdf to.pdf combine.pdf`
    
    `Options can be:`

    `-f [FILE] - specify the path and name of file that will be created. Default is ./stickers.pdf.`

    `-d [DIRECTORY] - specify the directory from which all .pdf files will be used as input along with individual files
    if provided.`

    `-w [INTEGER] - specify how many stickers to place in the width of a page. Default is 2.`

    `-h [INTEGER] - specify how many stickers to place in the height of a page. Default is 3.`
    
    `-s [PAGE SIZE] - specify the page size. Like A4, A3 etc. Default is A4.`

    `-m [INTEGER] - specify the margins around each sticker in mm. Default is 0. Can be negative.`

    `-r [BOOLEAN] - type 'false' if you don't want program to rotate the page if its ratio is violated. Default 
    is 'true'.`


- Import function `compose_stickers`, and give it what it wants.


- Use beautiful UI:
    - run it as module: `python3 -m ui`
    - use run.sh (why not) `chmod u+x run.sh`(x1) and then `./run.sh`(as needed)
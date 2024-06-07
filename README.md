# pdf-stickers

**TL/DR:** combines .pdf files according to chosen layout on chosen page size.

---

**What actually happens:**

Let's call each individual page from input files - a **sticker**.

You specify:
- How many stickers should be placed across the page.
- How many stickers should be placed down the page.
- The format of a page (A3, A4, A5, etc.).
- The margins around each sticker if needed. Can be negative.
- Fill available space or resize sticker to fit into it.
- Whether to rotate a page when its original ratio is violated in chosen layout.
- Files individually or directories from which all .pdf files will be imported.

Program does:
- Resizes each page from input files to fit in specified layout filling all space or just fitting in
- Rotates stickers if needed
- Saves resulted .pdf file

Example:
You can choose files consisted together of 12 pages, select layout 2 x 3 and result will be .pdf file consisted of 2 
pages with 6 stickers on each.
Or you can specify 1 x 1 layout and result will be all pages from all input files combined in one.

---

**How to use:**

- install:
    
    `chmod u+x run.sh install.sh`
    
    `. install.sh`
    
    or

    setup venv and install dependencies by yourself


- Use UI:
    
  *Tkinter must be installed* 

    `. run.sh`, 
    enjoy


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

    `-l [BOOLEAN] - type 'true' to resize each sticker to all available space instead of fit in it.`


- In your code import function `compose_stickers`, and give it what it wants.
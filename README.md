# Renegade Immortal EPUB Splitter

When I downloaded the EPUB file for Renegade Immortal from Wuxia World, I noticed that all 13 books were crammed into a single file.  This caused Amazon's "Send to Kindle" feature to hang for over an hour and ultimately fail.  To fix this, I wrote a small python script that will split the combined EPUB back into its 13 original books and write individual EPUB files for each book.  This script will generate correct "Table of Contents" for each book as well.

## Usage

First grab dependencies:

```sh
$ pip install -r requirements.txt
```

Next, you need to decompress the combined EPUB file from Wuxia World.  The good news is that EPUB files are just zip files in disguise, so you can use your favorite ZIP tool to decompress everything.  Place the files in `./source`.

Finally, just run `split-books.py` using Python:

```sh
$ python split-books.py
```

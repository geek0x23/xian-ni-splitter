# Renegade Immortal EPUB Splitter

When I downloaded the EPUB file for Renegade Immortal from Wuxia World, I noticed that all 13 books were crammed into a single file.  This caused Amazon's "Send to Kindle" feature to hang for over an hour and ultimately fail.  To fix this, I wrote a small python script that will split the combined EPUB back into its 13 original books and write individual EPUB files for each book.  This script will generate correct "Table of Contents" for each book as well.

## Usage

First grab dependencies:

```sh
$ pip install -r requirements.txt
```

Next, just run `split-books.py` using Python:

```sh
$ python split-books.py path/to/renegade-immortal.epub
```

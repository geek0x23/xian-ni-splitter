from books import books
from pybars import Compiler
from pathlib import Path

import click
import shutil
import os
import zipfile

@click.command()
@click.argument("source", type=click.Path(exists=True))
def run(source):
    """Converts the massive single-book EPUB for Renegade Immortal into individual EPUBS (one per book)"""
    compiler = Compiler()

    content_opf_template = compiler.compile(Path("templates/content.opf.hbs").read_text(encoding="utf-8"));
    contents_xhtml_template = compiler.compile(Path("templates/contents.xhtml.hbs").read_text(encoding="utf-8"));
    title_page_xhtml_template = compiler.compile(Path("templates/title-page.xhtml.hbs").read_text(encoding="utf-8"));
    toc_ncx_template = compiler.compile(Path("templates/toc.ncx.hbs").read_text(encoding="utf-8"));

    print("Cleaning up from previous runs.")
    staging_path = Path.cwd().joinpath("staging")
    out_path = Path.cwd().joinpath("out")
    source_path = Path.cwd().joinpath("source")
    shutil.rmtree(staging_path, ignore_errors=True)
    shutil.rmtree(out_path, ignore_errors=True)
    shutil.rmtree(source_path, ignore_errors=True)
    os.makedirs(staging_path, 0o755)
    os.makedirs(out_path, 0o755)
    os.makedirs(source_path, 0o755)

    print("Decompressing source EPUB.")
    with zipfile.ZipFile(source, "r") as zipf:
        zipf.extractall(source_path)

    for book in books:
        print("Working on book {0}: {1}".format(book.number, book.title))

        book_path = staging_path.joinpath("book{0}".format(book.number))
        meta_inf_path = book_path.joinpath("META-INF")
        oebps_path = book_path.joinpath("OEBPS")
        css_path = oebps_path.joinpath("css")
        images_path = oebps_path.joinpath("images")

        os.makedirs(book_path, 0o755)
        os.makedirs(meta_inf_path, 0o755)
        os.makedirs(oebps_path, 0o755)
        os.makedirs(css_path, 0o755)
        os.makedirs(images_path, 0o755)

        print(" - Copying static contents.")
        shutil.copy2(source_path.joinpath("META-INF", "com.apple.ibooks.display-options.xml"), meta_inf_path)
        shutil.copy2(source_path.joinpath("META-INF", "container.xml"), meta_inf_path)
        shutil.copy2(source_path.joinpath("OEBPS", "copyright.xhtml"), oebps_path)
        shutil.copy2(source_path.joinpath("OEBPS", "cover.xhtml"), oebps_path)
        shutil.copy2(source_path.joinpath("OEBPS", "css", "media.css"), css_path)
        shutil.copy2(source_path.joinpath("OEBPS", "css", "style.css"), css_path)
        shutil.copy2(source_path.joinpath("OEBPS", "images", "vellum-created.png"), images_path)
        shutil.copy2(source_path.joinpath("OEBPS", "images", "xn.jpg"), images_path)
        shutil.copy2(source_path.joinpath("mimetype"), book_path)

        print(" - Generating manifests and ToC.")
        content_opf_output = content_opf_template(book)
        contents_xhtml_output = contents_xhtml_template(book)
        title_page_xhtml_output = title_page_xhtml_template(book)
        toc_ncx_output = toc_ncx_template(book)

        content_opf_path = oebps_path.joinpath("content.opf")
        contents_xhtml_path = oebps_path.joinpath("contents.xhtml")
        title_page_xhtml_path = oebps_path.joinpath("title-page.xhtml")
        toc_ncx_path = oebps_path.joinpath("toc.ncx")

        content_opf_path.write_text(content_opf_output, encoding="utf-8")
        contents_xhtml_path.write_text(contents_xhtml_output, encoding="utf-8")
        title_page_xhtml_path.write_text(title_page_xhtml_output, encoding="utf-8")
        toc_ncx_path.write_text(toc_ncx_output, encoding="utf-8")

        print(" - Copying chapters.")
        for chapter in book.chapters:
            source_chapter_path = source_path.joinpath("OEBPS", chapter.file_name)
            dest_chapter_path = oebps_path.joinpath(chapter.file_name)
            shutil.copy2(source_chapter_path, dest_chapter_path)

        print(" - Generating EPUB file.")
        out_epub_path = out_path.joinpath("Renegade Immortal - Book {0} - {1}.epub".format(book.number, book.title))
        with zipfile.ZipFile(out_epub_path, "w", compresslevel=9) as zipf:
            for root, subdirs, files in os.walk(book_path):
                for file in files:
                    full_file_name = os.path.join(root, file)
                    method = zipfile.ZIP_DEFLATED
                    file_size = os.path.getsize(full_file_name)
                    if file_size < 23: # Minimum compressed size is 22 bytes, so we don't bother compressing.
                        method = zipfile.ZIP_STORED

                    zipf.write(full_file_name, os.path.relpath(full_file_name, book_path), compress_type=method)

        print(" - Book complete!\n")

    print("All done, check the \"out\" folder!")

if __name__ == "__main__":
    run()

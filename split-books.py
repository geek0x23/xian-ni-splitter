from books import books
from pybars import Compiler
from pathlib import Path

import click
import shutil
import os
import zipfile

@click.command()
@click.argument('source', type=click.Path(exists=True))
def run(source: str):
    '''Converts the massive single-book EPUB for Renegade Immortal into individual EPUBS (one per book)'''
    hb = Compiler()
    cwd = Path(__file__).parent

    templates_path = cwd.joinpath('templates')
    covers_path = cwd.joinpath('covers')
    content_opf_template = hb.compile(templates_path.joinpath('content.opf.hbs').read_text(encoding='utf-8'))
    contents_xhtml_template = hb.compile(templates_path.joinpath('contents.xhtml.hbs').read_text(encoding='utf-8'))
    title_page_xhtml_template = hb.compile(templates_path.joinpath('title-page.xhtml.hbs').read_text(encoding='utf-8'))
    toc_ncx_template = hb.compile(templates_path.joinpath('toc.ncx.hbs').read_text(encoding='utf-8'))

    print('Cleaning up from previous runs.')
    staging_path = cwd.joinpath('staging')
    out_path = cwd.joinpath('out')
    source_path = cwd.joinpath('source')
    shutil.rmtree(staging_path, ignore_errors=True)
    shutil.rmtree(out_path, ignore_errors=True)
    shutil.rmtree(source_path, ignore_errors=True)
    staging_path.mkdir(0o755, True, True)
    out_path.mkdir(0o755, True, True)
    source_path.mkdir(0o755, True, True)

    print('Decompressing source EPUB.')
    with zipfile.ZipFile(source, 'r') as zipf:
        zipf.extractall(source_path)

    for book in books:
        print(f'Working on Book {book.number}: {book.title}')

        book_path = staging_path.joinpath(f'book{book.number}')
        meta_inf_path = book_path.joinpath('META-INF')
        oebps_path = book_path.joinpath('OEBPS')
        css_path = oebps_path.joinpath('css')
        images_path = oebps_path.joinpath('images')

        book_path.mkdir(0o755, True, True)
        meta_inf_path.mkdir(0o755, True, True)
        oebps_path.mkdir(0o755, True, True)
        css_path.mkdir(0o755, True, True)
        images_path.mkdir(0o755, True, True)

        print(' - Copying static contents.')
        shutil.copy2(source_path.joinpath('META-INF', 'com.apple.ibooks.display-options.xml'), meta_inf_path)
        shutil.copy2(source_path.joinpath('META-INF', 'container.xml'), meta_inf_path)
        shutil.copy2(source_path.joinpath('OEBPS', 'copyright.xhtml'), oebps_path)
        shutil.copy2(source_path.joinpath('OEBPS', 'cover.xhtml'), oebps_path)
        shutil.copy2(source_path.joinpath('OEBPS', 'css', 'media.css'), css_path)
        shutil.copy2(source_path.joinpath('OEBPS', 'css', 'style.css'), css_path)
        shutil.copy2(source_path.joinpath('OEBPS', 'images', 'vellum-created.png'), images_path)
        shutil.copy2(covers_path.joinpath(f'xn{book.number}.jpg'), images_path.joinpath('xn.jpg'))
        shutil.copy2(source_path.joinpath('mimetype'), book_path)

        print(' - Generating manifests and ToC.')
        content_opf_output = content_opf_template(book)
        contents_xhtml_output = contents_xhtml_template(book)
        title_page_xhtml_output = title_page_xhtml_template(book)
        toc_ncx_output = toc_ncx_template(book)

        content_opf_path = oebps_path.joinpath('content.opf')
        contents_xhtml_path = oebps_path.joinpath('contents.xhtml')
        title_page_xhtml_path = oebps_path.joinpath('title-page.xhtml')
        toc_ncx_path = oebps_path.joinpath('toc.ncx')

        content_opf_path.write_text(content_opf_output, encoding='utf-8')
        contents_xhtml_path.write_text(contents_xhtml_output, encoding='utf-8')
        title_page_xhtml_path.write_text(title_page_xhtml_output, encoding='utf-8')
        toc_ncx_path.write_text(toc_ncx_output, encoding='utf-8')

        print(' - Copying chapters.')
        for chapter in book.chapters:
            source_chapter_path = source_path.joinpath('OEBPS', chapter.file_name)
            dest_chapter_path = oebps_path.joinpath(chapter.file_name)
            shutil.copy2(source_chapter_path, dest_chapter_path)

        print(' - Generating EPUB file.')
        out_epub_path = out_path.joinpath(f'Renegade Immortal - Book {book.number} - {book.title}.epub')
        with zipfile.ZipFile(out_epub_path, 'w', compresslevel=9) as zipf:
            for root, subdirs, files in os.walk(book_path): # Path.walk() needs Python 3.12, but Alma only ships 3.9
                for file in files:
                    file_path = Path(root, file)
                    method = zipfile.ZIP_DEFLATED
                    file_size = file_path.stat().st_size
                    if file_size < 23: # Minimum compressed size is 22 bytes, so we don't bother compressing.
                        method = zipfile.ZIP_STORED

                    zipf.write(file_path, file_path.relative_to(book_path), compress_type=method)

        print(' - Book complete!\n')

    print('All done, check the "out" folder!')

if __name__ == '__main__':
    run()

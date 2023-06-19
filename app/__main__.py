import os
import sys
import pathlib

from pypdf import (
    PdfReader,
    PageObject,
    PdfWriter,
    Transformation,
    PaperSize,
)


class UnporcessableFilesError(Exception):
    def __init__(self, unprocessable_files: list[tuple[pathlib.Path, str]]):
        self.unprocessable_files = unprocessable_files

    def __str__(self):
        files_repr = '\n'.join([
            f'{name}: {why}' for name, why in self.unprocessable_files
        ])
        return f'This files cannot be processed:\n{files_repr}'


def sticker_list(files_list: list[PdfReader]) -> list[PageObject]:
    """
    Make list of individual PageObject objects representing each sticker

    :param files_list: List of PdfReader objects representing each file
    :return: List of PageObject objects
    """
    stickers = []
    for f in files_list:
        stickers += f.pages
    return stickers


def sticker_stacker(stickers: list[PageObject]) -> PdfWriter:
    """
    Creates a PdfWriter object with all stickers placed on A4 pages.

    :param stickers: list of PageObject representing each sticker
    :return: PdfWriter object ready to write in file
    """

    # Initial goal is to fit 6(2x3 grid) stickers on A4 page
    #
    # Need to think how to bind this numbers together when the grid will be
    # a subject to chage
    sticker_widht = PaperSize.A4.width / 2
    sticker_height = PaperSize.A4.height / 3

    writer = PdfWriter()

    destpage: PageObject | None = None
    for i, s in enumerate(stickers):
        # Need to think how to bind this numbers together when the grid will be
        # a subject to chage
        if i % 6 == 0:
            destpage = writer.add_blank_page(
                width=PaperSize.A4.width,
                height=PaperSize.A4.height,
            )
        s.scale_to(width=sticker_widht, height=sticker_height)

        # Need to think how to bind this numbers together when the grid will be
        # a subject to chage
        x = i % 2
        y = (i % 6) // 2
        destpage.merge_transformed_page(
            s,
            Transformation().translate(
                x * sticker_widht,
                PaperSize.A4.height - (y + 1) * sticker_height,  # origin is left bottom corner
            ),
        )
    return writer


def process_paths(files_list: list[str | os.PathLike]) -> list[PdfReader]:
    """
    Checks whether all files are available and processable.
    Files can be repeated and their content will also be repeated in the result

    :param files_list: list of absolute paths to pdf files
    :return: list of PdfReader objects
    :raise UnporcessableFilesError: if file is missing, has non-pdf extension
    or unreadable, with the list of the unprocessable files
    """
    if len(files_list) < 1:
        raise ValueError('The files\' list is empty')

    unprocessable_paths = []
    for f in files_list:
        p = pathlib.Path(f)

        file_error = None
        if not p.exists():
            file_error = (p, 'File doesn\'t exist')
        elif not p.suffix == '.pdf':
            file_error = (p, 'File has non-pdf extension')
        elif not os.access(p, os.R_OK):
            file_error = (p, 'File cannot be read')

        if file_error:
            unprocessable_paths.append(file_error)

    if unprocessable_paths:
        raise UnporcessableFilesError(unprocessable_paths)

    return [PdfReader(f) for f in files_list]


def compose_stickers(files_list: list[str | os.PathLike], file_to_write: str = 'stickers.pdf') -> None:
    """
    Make .pdf file with all pages from listed files as stickers placed on A4 page.

    :param files_list: List of paths to pdf files. Can be strings or PathLike objects
    :param file_to_write: Name for the final file
    """
    stickers = process_paths(files_list)
    writer = sticker_stacker(sticker_list(stickers))

    with open(file_to_write, 'wb') as fp:
        writer.write(fp)


def parse_arguments() -> dict[str, str]:
    """
    Parse command line arguments.

    -f, --file-name - optional. Name of the final file to save.

    :return: Dict of kwargs to main function
    """

    result_file_name = 'stickers.pdf'
    file_names_start_from = 1
    if sys.argv[1] in ('-f', '--file-name'):
        result_file_name = sys.argv[2]
        file_names_start_from = 3

    return {
        'files_list': sys.argv[file_names_start_from:],
        'file_to_write': result_file_name
    }


if __name__ == '__main__':
    compose_stickers(**parse_arguments())


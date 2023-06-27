import os
import sys
import pathlib
from typing import Iterable

from pypdf import (
    PdfReader,
    PageObject,
    PdfWriter,
    Transformation,
    PaperSize,
)


class UnporcessableArgumentsError(Exception):
    def __init__(self, unprocessable_arguments: list[tuple[pathlib.Path | str, str]]):
        self.unprocessable_arguments = unprocessable_arguments

    def __str__(self):
        args_repr = '\n'.join([
            f'{name}: {why}' for name, why in self.unprocessable_arguments
        ])
        return f'These arguments cannot be processed:\n{args_repr}'


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
    # a subject to change
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
        elif p.suffix not in ('.pdf', '.PDF'):
            file_error = (p, 'File has non-pdf extension')
        elif not os.access(p, os.R_OK):
            file_error = (p, 'File cannot be read')

        if file_error:
            unprocessable_paths.append(file_error)

    if unprocessable_paths:
        raise UnporcessableArgumentsError(unprocessable_paths)

    return [PdfReader(f) for f in files_list]


def compose_stickers(
    files_list: list[str | os.PathLike],
    file_to_write: str | os.PathLike = 'stickers.pdf'
) -> None:
    """
    Make .pdf file with all pages from listed files as stickers placed on A4 page.

    :param files_list: List of paths to pdf files. Can be strings or PathLike objects
    :param file_to_write: Name for the final file
    """
    stickers = process_paths(files_list)
    writer = sticker_stacker(sticker_list(stickers))

    with open(file_to_write, 'wb') as fp:
        writer.write(fp)


def parse_options(
        arguments: list[str],
        implemented_options: Iterable
) -> tuple[list[tuple[str, str]], list[str]]:
    """
    Separate options, if provided, from file names.

    :param arguments: List of all provided arguments
    :param implemented_options: Iterable of implemented options to parse
    :return: Tuple of list of options with values and list of files
    """

    options = []
    while len(arguments) > 1:
        if arguments[0] in implemented_options:
            options.append((arguments.pop(0), arguments.pop(0)))
        else:
            break

    return options, arguments


def file_name(value: str, result_dict: dict) -> dict:
    """
    -f option. User defined name of final file.

    :param value: User provided name
    :param result_dict: Dict of arguments to modify
    :return: Modified dict of arguments
    """
    result_dict['file_to_write'] = value
    return result_dict


def directory(value: str, result_dict: dict) -> dict:
    """
    -d option. User defined directory from which all pdf files will be used as files list.

    :param value: Name of the directory
    :param result_dict: Dict of arguments to modify
    :return: Modified dict of arguments
    """
    try:
        result_dict['files_list'] = [value / pathlib.Path(f) for f in os.listdir(value) if f.endswith(('.pdf', '.PDF'))]
    except FileNotFoundError:
        raise UnporcessableArgumentsError([(value, 'No such directory'), ])

    return result_dict


def parse_arguments() -> dict[str, str]:
    """
    Parse command line arguments.

    -f - optional. Name of the final file to save
    -d - optional. Directory from which all pdf files will be used as input files

    :return: Dict of kwargs to main function
    """

    # Flags with corresponding functions that modify result dict accordingly
    implemented_options = {
        '-f': file_name,
        '-d': directory,
    }

    # Get list of options with their values and list of files to use
    options, files = parse_options(sys.argv[1:], implemented_options)

    # Default input to main function
    result = {
        'files_list': files,
        'file_to_write': 'stickers.pdf'
    }

    # For all parsed options call corresponding function with its value and result dict to modify
    for option, value in options:
        implemented_options[option](value, result)

    return result


if __name__ == '__main__':
    # print(parse_arguments())
    compose_stickers(**parse_arguments())

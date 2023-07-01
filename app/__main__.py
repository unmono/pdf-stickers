import os
import sys
import pathlib
from typing import Iterable
from functools import partial

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


def validate_grid_value(*args) -> list[tuple[str, str]]:
    errors = []
    for value in args:
        if value < 1 or value > 40:
            errors.append((value, 'Should be an integer from 1 to 40.'))

    return errors


def sticker_stacker(
        stickers: list[PageObject],
        paper_format: str = 'A4',
        # Initial goal is to fit 6(2x3 grid) stickers on A4 page, so the default values are 2 and 3
        stickers_in_width: int = 2,
        stickers_in_height: int = 3,
) -> PdfWriter:
    """
    Creates a PdfWriter object with all stickers placed on A4 pages.

    :param paper_format: paper format to use (e.g. A4, A3 etc.)
    :param stickers_in_width: how many stickers do you want to place in a single row on a page(stickers in width)
    :param stickers_in_height: how many rows of stickers should be on a page(stickers in height)
    :param stickers: list of PageObject representing each sticker
    :return: PdfWriter object ready to write in file
    """

    errors = []
    try:
        page_size = getattr(PaperSize, paper_format.upper())
    except AttributeError:
        valid_formats = [f for f in dir(PaperSize) if not f.startswith('__')]
        errors.append((paper_format, f'It is not a valid paper format. Please chose from: {", ".join(valid_formats)}'))

    errors += validate_grid_value(stickers_in_width, stickers_in_height)
    if errors:
        raise UnporcessableArgumentsError(errors)

    stickers_on_page = stickers_in_width * stickers_in_height
    sticker_widht = page_size.width / stickers_in_width
    sticker_height = page_size.height / stickers_in_height

    writer = PdfWriter()

    destpage: PageObject | None = None
    for i, s in enumerate(stickers):
        if i % stickers_on_page == 0:
            destpage = writer.add_blank_page(
                width=page_size.width,
                height=page_size.height,
            )
        s.scale_to(width=sticker_widht, height=sticker_height)

        x = i % stickers_in_width
        y = (i % stickers_on_page) // stickers_in_width
        destpage.merge_transformed_page(
            s,
            Transformation().translate(
                x * sticker_widht,
                page_size.height - (y + 1) * sticker_height,  # origin is left bottom corner
            ),
        )
    return writer


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
    file_to_write: str | os.PathLike = 'stickers.pdf',
    **kwargs
) -> None:
    """
    Make .pdf file with all pages from listed files as stickers placed on A4 page.

    :param files_list: List of paths to pdf files. Can be strings or PathLike objects
    :param file_to_write: Name for the final file
    """
    stickers = process_paths(files_list)
    writer = sticker_stacker(sticker_list(stickers), **kwargs)

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


def grid_parameters(attr_key: str, value: str, result_dict: dict) -> dict:
    try:
        result_dict[attr_key] = int(value)
    except ValueError:
        raise UnporcessableArgumentsError([(value, 'Should be an integer'), ])

    return result_dict


set_stickers_in_width = partial(grid_parameters, attr_key='stickers_in_width')
set_stickers_in_height = partial(grid_parameters, attr_key='stickers_in_height')


def set_paper_format(value: str, result_dict: dict) -> dict:
    result_dict['paper_format'] = value
    return result_dict


def parse_arguments() -> dict[str, str]:
    """
    Parse command line arguments.

    -f - optional. Name of the final file to save
    -d - optional. Directory from which all pdf files will be used as input files
    -w - optional. How many stickers should be placed across the page
    -h - optional. How many stickers should be placed down the page
    -s - optional. Paper format to use (e.g. A4, A3 etc.)

    :return: Dict of kwargs to main function
    """

    # Flags with corresponding functions that modify result dict accordingly
    implemented_options = {
        '-f': file_name,
        '-d': directory,
        '-w': set_stickers_in_width,
        '-h': set_stickers_in_height,
        '-s': set_paper_format,
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
        implemented_options[option](value=value, result_dict=result)

    return result


if __name__ == '__main__':
    # print(parse_arguments())
    try:
        compose_stickers(**parse_arguments())
    except UnporcessableArgumentsError as uae:
        print(uae)
        sys.exit(1)

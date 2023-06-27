from .StickersUI import StickersUI, browse_files, browse_directory

if __name__ == '__main__':
    stickers = StickersUI([
        browse_directory,
        browse_files,
    ])

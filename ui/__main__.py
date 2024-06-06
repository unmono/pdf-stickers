from .StickersUI import StickersUI
from .JSONAttributeKeeper import JSONAttributeKeeper

if __name__ == '__main__':
    stickers = StickersUI(keeper=JSONAttributeKeeper)
    stickers.run()

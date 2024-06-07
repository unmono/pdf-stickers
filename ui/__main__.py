from .JSONAttributeKeeper import JSONAttributeKeeper
from .StickersUI import StickersUI

if __name__ == '__main__':
    stickers = StickersUI(keeper=JSONAttributeKeeper)
    stickers.run()

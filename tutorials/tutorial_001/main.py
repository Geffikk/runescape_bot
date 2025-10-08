import cv2 as cv
import numpy as np

haystack_img = cv.imread('runescape_dungeon.png', cv.IMREAD_REDUCED_COLOR_2)
needle_img = cv.imread('catablepon.png', cv.IMREAD_REDUCED_COLOR_2)

result = cv.matchTemplate(haystack_img, needle_img, cv.TM_CCOEFF_NORMED)

#cv.imshow('Result', result)
#cv.waitKey()

# Get the best match position
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

print(f'Best match top-left position: {max_loc}, with confidence: {max_val}')

threshold = 0.8
if max_val >= threshold:
    print(f'Catablepon found at position: {max_loc}')

    top_left = max_loc
    bottom_right = (top_left[0] + needle_img.shape[1], top_left[1] + needle_img.shape[0])

    cv.rectangle(haystack_img, top_left, bottom_right, (0, 255, 0), 2, lineType=cv.LINE_4)
    #cv.imshow('Result', haystack_img)
    #cv.waitKey()
    cv.imwrite('result.png', haystack_img)
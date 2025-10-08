import cv2 as cv
import numpy as np
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#np.set_printoptions(threshold=sys.maxsize)

haystack_img = cv.imread('runescape_dungeon.png', cv.IMREAD_REDUCED_COLOR_2)
needle_img = cv.imread('catablepon.png', cv.IMREAD_REDUCED_COLOR_2)

result = cv.matchTemplate(haystack_img, needle_img, cv.TM_SQDIFF_NORMED)
#print(result)

threshold = 0.2
locations = np.where(result <= threshold)
locations = list(zip(*locations[::-1]))
print(locations)

if locations:
    print(f'Catablepon found')

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]
    line_color = (0, 255, 0)
    line_type = cv.LINE_4

    # need to loop over all locations and draw them
    for loc in locations:
        top_left = loc
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
        cv.rectangle(haystack_img, top_left, bottom_right, line_color, 2, lineType=line_type)

    cv.imshow('Matches', haystack_img)
    cv.waitKey()
    #cv.imwrite('result.png', haystack_img)
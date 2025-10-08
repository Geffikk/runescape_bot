import cv2 as cv
import numpy as np
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#np.set_printoptions(threshold=sys.maxsize)

def findClickPositions(needle_img_path, haystack_img_path, threshold=0.5, debug_mode=None):

    haystack_img = cv.imread('runescape_dungeon.png', cv.IMREAD_REDUCED_COLOR_2)
    needle_img = cv.imread('catablepon.png', cv.IMREAD_REDUCED_COLOR_2)

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack_img, needle_img, method)


    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        rectangles.append(rect)

    rectangles, _ = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.2)

    if len(rectangles):
        print(f'Catablepon found')

        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_DIAMOND

        points = []
        # need to loop over all locations and draw them
        for (x, y, w, h) in rectangles:
            # Determining the center of the rectangle
            center_x = x + w / 2
            center_y = y + h / 2
            points.append((int(center_x), int(center_y)))

            if debug_mode == 'rectangles':
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                cv.rectangle(haystack_img, top_left, bottom_right, line_color, 2, lineType=line_type)
            elif debug_mode == 'points':
                cv.drawMarker(haystack_img, (int(center_x), int(center_y)), marker_color, marker_type, 10, 1)

        if debug_mode:
            cv.imshow('Matches', haystack_img)
            cv.waitKey()

        return points

points = findClickPositions('catablepon.png', 'runescape_dungeon.png', debug_mode='points')
print(points)
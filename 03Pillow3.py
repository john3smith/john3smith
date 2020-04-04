#실패작.
#cv2로 이미지를 읽어도 PIL라이브러리에 적용할 수 없음.

from PIL import Image
from PIL import ImageDraw
from PIL import ImageChops
from PIL import ImageStat
import sys
import cv2
import numpy as np


def Search(cx, cy):
    compare = source.crop((cx, cy, cx + tx, cy + ty)) # 소스에서 타겟으로 판단되는 위치의 이미지를 타겟 사이즈 만큼 잘라낸다.
    # Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    print("Compare size: ", compare.size)
 
    diff = ImageChops.difference(compare, target) # 타겟과 타겟으로 판단되는 부분의 픽셀값 비교.
    stat = ImageStat.Stat(diff)

    if stat.sum == [0, 0, 0, 0]:
        print("Target found(checksum): ", stat.sum)
        return True
    else:
        return False

print("[시작]")

#타겟(비올레타) 찾기
source = cv2.imread("imgDir/scr (11)4.png")  #화면. 너무 크면(QHD) 처음부터 끝까지 찾지 못한다.
#sx, sy = source.shape
sx = source.shape[1]
sy = source.shape[0]
target = cv2.imread("imgDir/bio3.png")   #찾을 이미지
#tx, ty = target.shape
tx = target.shape[1]
ty = target.shape[0]

print(source.shape)

result_search=False #이미지 서치 성공여부 
draw = ImageDraw.Draw(source)    # Creates an object that can be used to draw in the given image.

for y in range(sy - ty):        # 소스의 처음부터 타겟 사이즈를 뺀 위치 까지 검색을 시작 한다.
    for x in range(sx - tx):    # 처음 (2 X 2)개 픽셀의 값이 같다면 Search()로 타겟 사이즈 전체를 다시 확인한다.
        if source.getpixel((x, y)) == target.getpixel((0, 0)) and source.getpixel((x + 1, y)) == target.getpixel((1, 0)) \
            and source.getpixel((x, y + 1)) == target.getpixel((0, 1)) and source.getpixel((x + 1, y + 1)) == target.getpixel((1, 1)):
            print("\tSearch 시도중")
            if Search(x, y) == True:
                print("Top left point: (%d, %d)" %(x, y))
                print("Center of targe point: (%d, %d)" %(x + target.width / 2, y + target.height / 2))
                draw.rectangle((x, y, x + target.width, y + target.height), outline = (255, 0, 0))
                # Draws a rectangle. 소스 이미지의 타겟 부분에 빨간 사각형을 그린다.
                result_search=True
                source.show()
                break
    if result_search==True:
        break
if result_search==False:
    print("Image search failed.")

print("[끝]")
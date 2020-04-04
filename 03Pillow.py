from PIL import Image
from PIL import ImageDraw
from PIL import ImageChops
from PIL import ImageStat
import sys


def Search(cx, cy):
    compare = source.crop((cx, cy, cx + tx, cy + ty)) # 소스에서 타겟으로 판단되는 위치의 이미지를 타겟 사이즈 만큼 잘라낸다.
    # Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    print("Compare size: ", compare.size)
 
    diff = ImageChops.difference(compare, target) # 타겟과 타겟으로 판단되는 부분의 픽셀값 비교.
    stat = ImageStat.Stat(diff)
    global trial

    if stat.sum == [0, 0, 0, 0]:
        print("Target found(checksum): ", stat.sum)
        return True
    else:
        trial += 1
        return False

source = Image.open("imgDir/scr (12)2.png")  #화면. 너무 크면(QHD) 처음부터 끝까지 찾지 못한다.
sx, sy = source.size
target = Image.open("imgDir/bio3.png")   #찾을 이미지
tx, ty = target.size

print("Source size: ", source.size)
print("Target size: ", target.size)
trial = 0 # Image search 시도 횟수.
result_search=False #이미지 서치 성공여부 

draw = ImageDraw.Draw(source)    # Creates an object that can be used to draw in the given image.

print("[시작]")
for y in range(sy - ty):        # 소스의 처음부터 타겟 사이즈를 뺀 위치 까지 검색을 시작 한다.
    for x in range(sx - tx):    # 처음 (2 X 2)개 픽셀의 값이 같다면 Search()로 타겟 사이즈 전체를 다시 확인한다.
        if source.getpixel((x, y)) == target.getpixel((0, 0)) and source.getpixel((x + 1, y)) == target.getpixel((1, 0)) \
            and source.getpixel((x, y + 1)) == target.getpixel((0, 1)) and source.getpixel((x + 1, y + 1)) == target.getpixel((1, 1)):
            print("\tSearch 시도중")
            if Search(x, y) == True:
                print("Top left point: (%d, %d)" %(x, y))
                print("Center of targe point: (%d, %d)" %(x + target.width / 2, y + target.height / 2))
                print("Number of total wrong detection: ", trial)
                draw.rectangle((x, y, x + target.width, y + target.height), outline = (255, 0, 0))
                # Draws a rectangle. 소스 이미지의 타겟 부분에 빨간 사각형을 그린다.
                result_search=True
                source.show()
                break
            else:
                print("At (%d, %d): Target not found" %(x, y))
                print("Wrong detection count: ", trial)
if result_search==False:
    print("Image search failed.")
    
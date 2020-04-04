#성공.
#QHD라서가 아니라 이미지포맷이 각각 "RGB", "RGBA"라서 비교가 안됬던거임.
#출처 : https://s-engineer.tistory.com/10
###

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

    if stat.sum == [0, 0, 0]:
        print("Target found(checksum): ", stat.sum)
        return True
    else:
        return False

print("[시작]")

#게임 타이틀 찾기
source = Image.open("imgDir/scr (11).png")  #화면. 너무 크면(QHD) 처음부터 끝까지 찾지 못한다.
source = source.crop((0,0,2560-1800,1440-900))
sx, sy = source.size
target = Image.open("imgDir/GameTitle.png")   #찾을 이미지
target = target.convert("RGB")
tx, ty = target.size

#source.show()
print("source : ",source.size)
print("target : ",target.size)
print(source.getpixel((59,109)))
print(target.getpixel((0,0)))

result_search=False

for y in range(sy):        # 소스의 처음부터 타겟 사이즈를 뺀 위치 까지 검색을 시작 한다.
    for x in range(sx):    # 처음 (2 X 2)개 픽셀의 값이 같다면 Search()로 타겟 사이즈 전체를 다시 확인한다.
        if source.getpixel((x, y)) == target.getpixel((0, 0)) and source.getpixel((x + 1, y)) == target.getpixel((1, 0)) \
            and source.getpixel((x, y + 1)) == target.getpixel((0, 1)) and source.getpixel((x + 1, y + 1)) == target.getpixel((1, 1)):
            print("\tSearch 시도중")
            if Search(x, y) == True:
                pt_x = x
                pt_y = y
                result_search=True
                print("title 좌표 : ",pt_x," ", pt_y)
                break
    if result_search==True:
        break


#타겟(비올레타) 찾기
if result_search==True:
    source = Image.open("imgDir/scr (12).png")  #화면. 너무 크면(QHD) 처음부터 끝까지 찾지 못한다.
    source = source.crop((pt_x,pt_y,pt_x+1920,pt_y+1080))
    sx, sy = source.size
    target = Image.open("imgDir/bio3.png")   #찾을 이미지
    target = target.convert("RGB")
    tx, ty = target.size


    result_search=False #이미지 서치 성공여부 
    draw = ImageDraw.Draw(source)    # Creates an object that can be used to draw in the given image.

    for y in range(pt_y, sy - ty):        # 소스의 처음부터 타겟 사이즈를 뺀 위치 까지 검색을 시작 한다.
        for x in range(pt_x, sx - tx):    # 처음 (2 X 2)개 픽셀의 값이 같다면 Search()로 타겟 사이즈 전체를 다시 확인한다.
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
else:
    print("Didnt search title;;;")
print("[끝]")
#색상이 근사한 픽셀을 비교하는 프로그램

from PIL import Image
from PIL import ImageDraw
from PIL import ImageChops
from PIL import ImageStat
import sys
import time
 
source = Image.open("imgDir/scr (11).png")
source = source.convert("RGB")
sx, sy = source.size
target = Image.open("imgDir/bio2.png")
target = target.convert("RGB")
tx, ty = target.size
tolerance = 30 # 오차 범위는 30 정도면 적당한거 같다.
step = 2 # 모든 픽셀을 검사하면 너무 오랜 시간이 걸린다. 한 개 건너 한 개 픽셀만 검사.
 
print("Source size: ", source.size)
print("Target size: ", target.size)
 
trial = 0 # Image search 시도 횟수.
 
def Search(cx, cy, tolerance):
    compare = source.crop((cx, cy, cx + tx, cy + ty)) # 소스에서 타겟으로 판단되는 위치의 이미지를 타겟 사이즈 만큼 잘라낸다.
    # Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    print("Compare size: ", compare.size)
 
    diff = ImageChops.difference(compare, target) # 타겟과 타겟으로 판단되는 부분의 픽셀값 비교.
    stat = ImageStat.Stat(diff)
    global trial
    if max(max(stat.extrema[0]), max(stat.extrema[1]), max(stat.extrema[2])) <= tolerance:
        print("Target found(Min, max): ", stat.extrema)
        return True
    else:
        trial += 1
        return False
 
draw = ImageDraw.Draw(source)    # Creates an object that can be used to draw in the given image.
start = time.time()
 
for y in range(sy - ty):                # 소스의 처음부터 타겟 사이즈를 뺀 위치 까지 전체 검색을 시작 한다.
    for x in range(0, sx - tx, step):    # 처음 (10 X 10)개 픽셀의 값이 비슷 하다면 Search()로 타겟 사이즈 전체를 다시 확인한다.
        compare = source.crop((x, y, x + 10, y + 10))
        partial_target = target.crop((0, 0, 10, 10))
        diff = ImageChops.difference(compare, partial_target) # 각 픽셀값 차의 절대값이 반환 된다.
        # Returns the absolute value of the pixel-by-pixel difference between the two images.
        stat = ImageStat.Stat(diff)
 
        if max(max(stat.extrema[0]), max(stat.extrema[1]), max(stat.extrema[2])) < tolerance:
            if Search(x, y, tolerance) == True:
                print("Top left point: (%d, %d)" %(x, y))
                print("Center of targe point: (%d, %d)" %(x + target.width / 2, y + target.height / 2))
                print("Number of total wrong detection: ", trial)
                draw.rectangle((x, y, x + target.width, y + target.height), outline = (255, 0, 0))
                # Draws a rectangle. 소스 이미지의 타겟 부분에 빨간 사각형을 그린다.
                end = time.time()
                print("Seraching time: ", end - start)
                source.show()
                sys.exit()
            else:
                print("At (%d, %d): Target not found" %(x, y))
                print("Wrong detection count: ", trial)
 
end = time.time()
print("Image search failed.")
print("Seraching time: ", end - start)

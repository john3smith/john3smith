#출처 : https://ng1004.tistory.com/89

from skimage.measure import compare_ssim
import argparse
import imutils
import cv2

#ap = argparse.ArgumentParser()
#ap.add_argument("-f", "--first", required = True, help = "first input image")
#ap.add_argument("-s", "--second", required = True, help = "second")

#imgDir/bioleta.png
#imgDir/screenshot.png
#$python tmp.py --first imgDir/bioleta.png --second imgDir/screenshot.png

#args = vars(ap.parse_args())

imageA = cv2.imread("imgDir/screenshot2.png")
imageB = cv2.imread("imgDir/screenshot.png")

grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

(score, diff) = compare_ssim(grayA, grayB, full = True)
diff = (diff * 255).astype("uint8")
print("SSIM: {}".format(score))



thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV |cv2.THRESH_OTSU)[1]
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

#cv2.imshow("Original", imageA)
#cv2.waitKey()
#cv2.destroyAllWindows()
#cv2.imshow("Modified", imageB)
#cv2.waitKey()
#cv2.destroyAllWindows()
# cv2.imshow("grayA", grayA)
# cv2.imshow("grayB", grayB)

cv2.imshow("Diff", diff)
cv2.waitKey()
cv2.destroyAllWindows()
cv2.imshow("Thresh", thresh)
cv2.waitKey()
cv2.destroyAllWindows()
cv2.waitKey()
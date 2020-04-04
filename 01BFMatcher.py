#출처 : https://hongku.tistory.com/333
import cv2
import matplotlib.pyplot as plt
import numpy as np

class compareImg:
    def __init__(self):
        pass
    
    def readImg(self, filepath):
        img = cv2.imread(filepath, 0)
        #cv2.namedWindow("root", cv2.WINDOW_NORMAL)
        #cv2.imshow("root",img)
        #cv2.waitKey()    #5초
        #cv2.destroyAllWindows()
        return img
    
    def run(self):
        filepath1 = "imgDir/bioleta.png"    #비올레타
        filepath2 = "imgDir/screenshot.png" #비교할 스크린샷
        img1 = self.readImg(filepath1)
        img2 = self.readImg(filepath2)

        self.diffImg(img1, img2)    #이미지 비교

    def diffImg(self, img1, img2):
        #initiate SIFT detector(디텍터를 시작한다)
        orb = cv2.ORB_create()

        #key point, descriptors를 찾음
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        #BFMatcher 오브젝트 생성
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        #des를 매칭시킨다
        matches = bf.match(des1, des2)

        matches = sorted(matches, key = lambda x:x.distance)    #매칭결과를 거리로 분류한다.

        #기본설정으로 매칭?시킨다
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        #ratio 적용
        good = []
        for m,n in matches: #matches에서
            if m.distance < 0.65 * n.distance:  #매칭요소의 거리가??
                good.append([m])    #합격리스트에 추가함

        #텍스트 출력
        print(good)

        #이미지 출력
        knn_img = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
        plt.figure(figsize=(10,6))
        plt.axis("off")
        plt.imshow(knn_img)
        plt.tight_layout()
        plt.show()

if __name__=="__main__":    #이 프로그램이 메인 프로그램인경우 실행함
    cImg = compareImg()
    cImg.run()
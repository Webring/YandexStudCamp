import numpy as np
import cv2
import glob

img_names_undistort = [img for img in glob.glob(
    "./img_test/*.jpg")]
new_path = "./undist/"

camera_matrix = np.array([[1.20467414e+03, 0.00000000e+00, 9.07854974e+02],
                          [0.00000000e+00, 1.20123843e+03, 5.52728845e+02],
                          [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist_coefs = np.array([-0.41728863,  0.22615515, -0.00167113,  0.00549296, -0.03307888])

def udis(img):

    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coefs, (w, h), 1, (w, h))

    # undistort
    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

    undst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

    # crop and save the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    return dst

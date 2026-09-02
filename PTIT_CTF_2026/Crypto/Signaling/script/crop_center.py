import cv2

img = cv2.imread('script/all_frames/frame_0000.png')
h, w, _ = img.shape
cx, cy = w // 2, h // 2
r = 450
crop = img[cy-r:cy+r, cx-r:cx+r]
cv2.imwrite('script/center_dial.png', crop)
print("Center dial cropped:", crop.shape)

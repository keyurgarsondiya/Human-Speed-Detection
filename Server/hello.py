import cv2
import numpy as np
import random
from collections import deque
import matplotlib.pyplot as plt
import sys

input_name = sys.argv[1]
y_n = sys.argv[2]

output_name = "processed_video.avi"
count = 0

cap = cv2.VideoCapture(input_name)

face_cascade = cv2.CascadeClassifier('frontalface.xml')
# tracking face using their centroids, maintaining a centroid list of all faces present in a frame
centroids_list = deque([])
face_count = 0

fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
out = cv2.VideoWriter(output_name, fourcc, cv2.CAP_PROP_FPS, (int(cap.get(3)),int(cap.get(4))))

listofspeeds = [];

while True:
	center1 = []
	center2 = []

	rc, image = cap.read()

	if rc!=True:
		break

	gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	faces = face_cascade.detectMultiScale(gray_image, 1.1, 13, 18, (24, 24))

	for (x, y, w, h) in faces:
		xA = x
		xB = x + w
		yA = y
		yB = y + h
		# Enumerate over all the faces in centroids_list
		# each centroid_list element contains: [last_updated_frame, color, position,
		# lock_count, unlock_count, lockstate(unlocked by default), list_of_face_speeds_in_prev_frames, id]
		not_matched = True
		for idx, centroid_data in enumerate(centroids_list):
			if centroid_data[0] == count:
				continue
			if centroids_list[idx][4] == 0:
				centroids_list[idx][5] = "unlocked"
				centroids_list[idx][4] = 5

			# check proximity using manhattan distance
			X = abs(float(centroid_data[2][0] + centroid_data[2][2]) / 2 - float(xA + xB) / 2)
			Y = abs(float(centroid_data[2][1] + centroid_data[2][3]) / 2 - float(yA + yB) / 2)
			# if there is a rectangle in n/2 pixel proximity of a rectangle of previous frame than i am assuming that,
			# the face in the rectangle is same as it was in the previous frame
			# 10 can be changed to any other value based on the movement happening in the frames, if vehicles are moving
			# more than 10 pixels per frame suppose 20 so change the value to 20
			n = 20
			if X < n and Y < n:

				not_matched = False
				centroids_list[idx][4] = 5
				centroids_list[idx][2] = [xA, yA, xB, yB]
				centroids_list[idx][6].append(np.sqrt(X ** 2 + Y ** 2) * 0.5)
				if centroids_list[idx][5] == "unlocked":

					if centroids_list[idx][0] == count - 1:
						centroids_list[idx][3] += 1

					else:
						centroids_list[idx][3] = 0

				if centroids_list[idx][3] == 3:
					centroids_list[idx][5] = "locked"
					centroids_list[idx][3] = 0
				if centroids_list[idx][6][-1] != 0.0:
					cv2.rectangle(image, (xA, yA), (xB, yB), centroid_data[1], 2)
					cv2.putText(image, str(centroids_list[idx][6][-1]),
								(xA, yA), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (np.average(centroid_data[1])/2), 1, cv2.LINE_AA)
				centroids_list[idx][0] = count
				break

		# If rectangle does not match with previous rectangles that means it is a new face so make a new rectangle
		if not_matched:
			color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

			# append new rectangle in previous faces list
			centroids_list.appendleft([count, color, (xA, yA, xB, yB), 1, 5, "unlocked", [0], face_count])
			face_count += 1
			prev_color = color
			prev_coords = [xA, yA, xB, yB]

	# plot all remaining locked rectangles
	for idx, centroid_data in enumerate(centroids_list):

		if centroid_data[5] == "locked" and centroid_data[0] != count:
			centroids_list[idx][4] -= 1
			if centroids_list[idx][6][-1] != 0.0:
				cv2.rectangle(image, (centroid_data[2][0], centroid_data[2][1]), (centroid_data[2][2], centroid_data[2][3]),
							  centroid_data[1], 2)
				# cv2.putText(image, str(centroids_list[idx][6][-1]),
				#			(centroid_data[2][0], centroid_data[2][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, centroid_data[1], 1,
				#			cv2.LINE_AA)
				cv2.putText(image, str(centroids_list[idx][6][-1]),
							(centroid_data[2][0], centroid_data[2][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (np.average(centroid_data[1])/2), 1,
							cv2.LINE_AA)
			if centroids_list[idx][4] == 0:
				centroids_list[idx][5] = "unlocked"
				centroids_list[idx][4] = 5
				centroids_list[idx][3] = 0

		if count - centroid_data[0] == 10:
			if sum(centroid_data[6]) / len(centroid_data[6]) != 0.0:
				listofspeeds.append( (centroid_data[7], centroid_data[6], centroid_data[1]) );

	centroids_list = deque([face_data for face_data in list(centroids_list) if count - face_data[0] < 10])

	if input_name == "0" or y_n == 'n':
		cv2.imshow('video2', image)
	out.write(image)

	# Wait for Esc key to stop
	if cv2.waitKey(33) == 27:
		break

	count += 1

cap.release()
out.release()

encountered = []
speed = []
colors = []
for i in range(1,len(listofspeeds)):
	j = len(listofspeeds) - i;
	if (listofspeeds[j][0] not in encountered) and (len(listofspeeds[j][1])>3):
		encountered.append(listofspeeds[j][0])
		speed.append(listofspeeds[j][1])
		colors.append(listofspeeds[j][2])

plt.figure()
for i in range(1,len(speed)):
	plt.plot(speed[i], label="speed of tracker "+str(encountered[i]), color= (colors[i][0]/255, colors[i][1]/255, colors[i][2]/255))

plt.legend()
print('Hello')
plt.savefig('graph.png')
plt.show()

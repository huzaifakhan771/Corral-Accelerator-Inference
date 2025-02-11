#to run
#python Video_detection.py --model models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite --labels models/coco_labels.txt --video 22.mp4


# import the necessary packages
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
import argparse
import imutils
import time
import cv2


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to TensorFlow Lite object detection model")
ap.add_argument("-l", "--labels", required=True,
	help="path to labels file")
ap.add_argument("-v", "--video", required=True,
	help="path to input video")
ap.add_argument("-c", "--confidence", type=float, default=0.3,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the labels dictionary
print("[INFO] parsing class labels...")
labels = {}
# loop over the class labels file
for row in open(args["labels"]):
	# unpack the row and update the labels dictionary
	(classID, label) = row.strip().split(maxsplit=1)
	labels[int(classID)] = label.strip()

# load the Google Coral object detection model
print("[INFO] loading Coral model...")
model = DetectionEngine(args["model"])

# load the input image
video = cv2.VideoCapture(args["video"])
# image = imutils.resize(image, width=500)
# orig = image.copy()

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 500 pixels
	flag, frame = video.read()
	if flag == False:
                break
	frame = imutils.resize(frame, width=500)
	orig = frame.copy()
	# prepare the frame for object detection by converting (1) it
	# from BGR to RGB channel ordering and then (2) from a NumPy
	# array to PIL image format
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	frame = Image.fromarray(frame)
	# make predictions on the input frame
	# start = time.time()
	timer = cv2.getTickCount()
	results = model.DetectWithImage(frame, threshold=args["confidence"],
		keep_aspect_ratio=True, relative_coord=False)
	# end = time.time()
	fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
	print("fps : ", fps)

	# loop over the results	
	for r in results:
		# extract the bounding box and box and predicted class label
		box = r.bounding_box.flatten().astype("int")
		(startX, startY, endX, endY) = box
		label = labels[r.label_id]
		# draw the bounding box and label on the image
		cv2.rectangle(orig, (startX, startY), (endX, endY),
			(0, 255, 0), 2)
		y = startY - 15 if startY - 15 > 15 else startY + 15
		text = "{}: {:.2f}%".format(label, r.score * 100)
		cv2.putText(orig, text, (startX, y),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
	# show the output frame and wait for a key press
	cv2.imshow("Frame", orig)
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
# do a bit of cleanup
cv2.destroyAllWindows()
video.release()
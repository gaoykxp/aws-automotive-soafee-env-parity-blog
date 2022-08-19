FROM gaoykxp/ubuntu-yolo6-aarch64:0.4

WORKDIR /home/YOLOv6

# Copy the dataset images over and extract them
COPY images/* ./data/images/

# Create directory for prediction result to save to host system
# VOLUME ["/home/YOLOv6/runs"]

CMD python3 ./tools/infer.py --weights ./yolov6s.pt --source ./data/images/test_image_0.png

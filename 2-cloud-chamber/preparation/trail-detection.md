# Information on trail detection using artificial intelligence / machine learning
## Report 2024
### What was tried
Training with
- own recordings with manually labeled data and
- generated images.

Two models:
1. [trail detection](#model-1)
2. [trail distinction](#model-2) (${ \alpha, \beta }$)

Software:
- Roboflow for training, testing and detection
- OpenCV line segment detector (not used)

### What was achieved
- Trail accuracy 93% (${ \alpha }$: 95%, ${ \beta }$: 90%)
- Artificial data was helpful
- Image segmentation
- Machine learning ${ \gg }$ algorithmic detection methods (speed and versatility)

### Issues
Classification issues:
- Scratches, dust etc. misidentified
- Long, curved, faint trails missed / misidentified / split up
- (Misidentified particles in wrong category)

Environmental issues:
- Airflow
- Ethanol drops

(Algorithmic) Line detection has problems with curved and faint trails and is significantly slower than machine learning models.

### Suggested improvements
- More manually labeled training data
- Better artificial data generation for more realistic trails
- Better chamber setup for less distractions

## Workflow
1. Pretrain ML model on existing data ([here](https://universe.roboflow.com/new-workspace-ugpt2/particle2))
2. Train on more data from artificial images with real backgrounds and generated trails in Python (how exactly generated?)
3. Validate with manually labeled data from the experiment (ca. 80 images)
4. Use to find the rest of the trails

### Model 1
Image segmentation:
- Object detection
- Tracing of trails
- Classification

About 80 images classified by hand (only particle vs drop, ${ \alpha }$ vs ${ \beta }$ prone to human error) and augmented in Roboflow (flipping).

Confidence threshold: 1%

[Source](https://universe.roboflow.com/nytron/cloud-chamber-particle-traces)

### Model 2
Object detection:
- Bounding box
- Labelling

Artificially generated data used only here (trails very visible (early stage) and not always generated where they should be).

[Source](https://universe.roboflow.com/testproject-jenwe/cloud-chamber-ethanol)

## Software/Sources
- [Roboflow](https://roboflow.com/)
- [YOLO11](https://github.com/ultralytics/ultralytics), [article](https://handeaygenli.medium.com/particle-identification-system-in-cloud-chamber-using-yolov5-518d58ad9f8f) on [YOLOv5](https://github.com/ultralytics/yolov5)
- [Report](https://iopscience.iop.org/article/10.1088/1361-6404/ad78cb) on real-time detection using OpenCV, Tensorflow, Keras on a modern Laptop: [video](https://www.youtube.com/watch?v=BiFm8-vtYIk) (electric cooling?)
- [Report](https://zacharysussman.com/pdf/cloud-chamber.pdf) on video post-processing using OpenCV3, numpy with very detailed code explanation (8 pages) with good trail-finding, but also bad characterization (12y/o laptop: 7-8fps)
- [Report](https://pubs.aip.org/aip/rsi/article/94/6/063304/2900463/Neuro-explicit-semantic-segmentation-of-the) on two different approaches to classification

# %%
from ultralytics import YOLO

# %%
# Create model from pretrained template
model = YOLO('yolo11n.pt')

# %%
# Train model with our own data
train_results = model.train(
  data='data.yaml',
  epochs=100,
  imgsz=640,
)

# %%
# See validation data
metrics = model.val()

# %%
# Analyse an image
results = model('image-to-analyse.png')
results[0].show()

# %%
# Export model and weights
# path = model.export(format='onnx')

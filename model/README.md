# 🍕 Pizza Detection YOLO Training

Train YOLO models to detect pizzas using the interactive Jupyter notebook with `.env` configuration.

## Table of Contents

- [Training Configuration](#training-configuration)
- [Notebook Workflow](#notebook-workflow)
- [Troubleshooting](#troubleshooting)


## Training Configuration

Edit `.env` file to configure training without modifying notebook code:

```env
# Model Configuration
YOLO_MODEL=yolo11m.pt              # Model size: yolo11n.pt (fast) to yolo11x.pt (accurate)
TRAINING_EPOCHS=50                 # Number of training epochs
TRAINING_BATCH=16                  # Batch size (adjust for GPU memory)
TRAINING_IMGSZ=640                 # Training image size
TRAINING_PATIENCE=5                # Early stopping patience

# Validation & Testing
VALIDATION_SPLIT=test              # Dataset split for validation
INFERENCE_CONF=0.25                # Confidence threshold for predictions

# Display & Export
MAX_DISPLAY_IMAGES=5               # Number of result images to show
EXPORT_FORMAT=onnx                 # Model export format
```

### Model Size Guide

| Model | Speed | Accuracy | GPU Memory | Use Case |
|-------|-------|----------|------------|----------|
| `yolo11n.pt` | Fastest | Good | Low | Quick testing |
| `yolo11s.pt` | Fast | Better | Medium | Balanced |
| `yolo11m.pt` | Medium | Good | Medium | **Recommended** |
| `yolo11l.pt` | Slow | Better | High | High accuracy |
| `yolo11x.pt` | Slowest | Best | Very High | Maximum accuracy |

## Notebook Workflow

The training notebook follows this workflow:

### 1. Environment Setup (Cells 1-4)
- Loads `.env` configuration
- Displays training parameters
- Validates dataset structure

### 2. Package Installation (Cells 5-6)
- Installs required packages
- Validates ultralytics installation

### 3. Dataset Preparation (Cells 7-9)
- Configures dataset paths
- Verifies dataset structure
- Displays dataset information

### 4. Model Training (Cell 10)
- Executes YOLO training with your parameters
- Shows real-time training progress
- Saves best model weights

### 5. Training Analysis (Cells 11-14)
- **Confusion Matrix**: Shows classification accuracy
- **Training Metrics**: Loss, precision, recall, mAP
- **Validation Results**: Performance on validation set

### 6. Model Validation (Cells 16-17)
- Tests model on test dataset
- Evaluates final performance metrics

### 7. Inference Testing (Cells 19-21)
- Runs inference on sample images
- Displays detection results with bounding boxes
- Shows confidence scores

### 8. Model Export (Cell 22)
- Exports model to specified format (ONNX, TorchScript, etc.)
- Provides usage instructions

## Troubleshooting

### Environment Issues
- **`.env` not loading**: Restart notebook kernel after editing `.env`
- **Missing packages**: Re-run installation cells
- **Dataset not found**: Check dataset path in `.env`

### Training Issues
- **GPU memory error**: Reduce `TRAINING_BATCH` size in `.env`
- **Training too slow**: Use smaller model (`yolo11n.pt`) or reduce epochs
- **Poor accuracy**: Increase epochs or use larger model


**Validate Configuration:**
```python
# Add this to a notebook cell to check settings
import os
from dotenv import load_dotenv

load_dotenv()
print(f"Model: {os.getenv('YOLO_MODEL')}")
print(f"Epochs: {os.getenv('TRAINING_EPOCHS')}")
print(f"Batch: {os.getenv('TRAINING_BATCH')}")
```
## Key Metrics to Monitor

- **mAP50**: Mean Average Precision at IoU 0.5 (main metric)
- **mAP50-95**: Mean Average Precision at IoU 0.5-0.95
- **Precision**: Ratio of correct predictions
- **Recall**: Ratio of detected objects
- **Loss**: Training loss (should decrease over time)

## Training Tips

1. **Start Small**: Use `yolo11n.pt` for initial testing
2. **Monitor GPU**: Watch for memory errors during training
3. **Check Results**: Review confusion matrix and sample predictions
4. **Adjust Parameters**: Modify `.env` based on results
5. **Export Models**: Save trained models in multiple formats

---

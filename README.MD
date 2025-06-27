# Pizza Counter System

An advanced computer vision system for counting pizzas in video streams using YOLO object detection and centroid tracking algorithms.The current iteration of the system is highly dependent on its environmental setting, which requires an unobstructed camera view of the pizza preparation station and cooking area.

## Overview

This repository contains two main components:

- **`counter_app/`** - Production-ready pizza counting application
- **`model/`** - YOLO model training pipeline for pizza detection

## Quick Start

### For Pizza Counting (Production)

```bash
cd counter_app
```
```bash
run.bat setup     # Setup directories
```
```bash
run.bat build     # Build docker app
```
```bash
run.bat process   # Process videos in input/ folder
```

### For Model Training

```bash
cd model
# Open pizza_yolo_training.ipynb in Jupyter
# Configure training parameters in .env file
```

## Project Structure

```
pizza_counter/
├── counter_app/          # Pizza counting application
│   ├── app.py           # Main application entry point
│   ├── centroid_tracker.py  # Object tracking implementation
│   ├── config.yaml      # Configuration settings
│   ├── zone_setup.py    # Interactive zone configuration
│   ├── input/           # Input videos directory
│   ├── output/          # Processed results and videos
│   └── model_data/      # YOLO model weights
└── model/               # Model training pipeline
    ├── pizza_yolo_training.ipynb  # Training notebook
    ├── runs/            # Training results and metrics
    └── soho_pizza.v2*/  # Training dataset
```

## Features

### Counter App
- **Accurate Detection** - YOLO-based pizza detection with customizable confidence thresholds
- **Object Tracking** - Centroid tracking to prevent duplicate counting
- **Zone Management** - Interactive zone setup for targeted counting areas
- **Video Processing** - Batch processing with annotated output videos
- **Docker Support** - Containerized deployment ready
- **Results Export** - JSON format results with timestamps and counts

### Model Training
- **YOLO Integration** - Support for YOLO11 model variants (n/s/m/l/x)
- **Interactive Training** - Jupyter notebook with step-by-step workflow
- **Configurable Parameters** - Environment-based configuration (.env)
- **Performance Metrics** - Training/validation loss tracking
- **Model Export** - Multiple format support (ONNX, TensorRT, etc.)

## Requirements

- Python 3.8+
- OpenCV
- Ultralytics YOLO
- Docker (optional)
- Jupyter Notebook (for training)

## Documentation

For detailed usage instructions, see the README files in each component:

- [Counter App Documentation](counter_app/README.md)
- [Model Training Documentation](model/README.md)


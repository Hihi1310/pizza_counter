"""
Pizza Counter Application
Processes video footage to count pizzas using YOLO object detection and tracking.
"""

import cv2
import numpy as np
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Set, Tuple
from ultralytics import YOLO
from centroid_tracker import CentroidTracker
from config import get_config
from datetime import timezone, timedelta
import helper

# Configure logging with GMT+7 timezone
class GMT7Formatter(logging.Formatter):
    def converter(self, timestamp):
        gmt7 = timezone(timedelta(hours=7))
        return datetime.fromtimestamp(timestamp, tz=gmt7)
    
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

# Setup logging
formatter = GMT7Formatter('%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, handlers=[])
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('pizza_counter.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class PizzaCounter:
    def __init__(self, model_path: str, confidence_threshold: float = None, config_path: str = None):
        """Initialize the Pizza Counter with YOLO model and Centroid tracker."""
        self.config = get_config(config_path)
        
        self.model_path = model_path
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
        else:
            self.confidence_threshold = self.config.get('MODEL_CONFIG', 'confidence_threshold', 0.5)
        
        self.counted_ids: Set[int] = set()
        self.total_count = 0
        self.track_positions: Dict[int, List[Tuple[int, int]]] = {}
        self.min_track_length = self.config.get('COUNTING_CONFIG', 'min_track_length', 5)
        
        logger.info(f"Loading YOLO model from {model_path}")
        self.model = YOLO(model_path)
        
        max_disappeared = self.config.get('TRACKING_CONFIG', 'max_disappeared', 30)
        max_distance = self.config.get('TRACKING_CONFIG', 'max_distance', 50)
        logger.info(f"Centroid tracker parameters: max_disappeared={max_disappeared}, max_distance={max_distance}")
        
        try:
            self.tracker = CentroidTracker(
                max_disappeared=max_disappeared,
                max_distance=max_distance
            )
            logger.info("Centroid tracker initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Centroid tracker: {e}")
            raise
        
        self.counting_region = None
        self.counting_line = None
        
        zone_coords = self.config.load_zones_from_config()
        if zone_coords:
            self.counting_region = helper.set_counting_region(*zone_coords)
        else:
            self.counting_region = helper.set_counting_region(0, 0, 1, 1)
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, int]:
        """Process a single frame for pizza detection and counting."""
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        detections = helper.extract_detections(results)
        
        # Handle tracker update with potential reinitialization
        tracker_result = helper.safe_tracker_update(self.tracker, detections, self.config)
        if isinstance(tracker_result, tuple):
            tracked_objects, self.tracker = tracker_result
        else:
            tracked_objects = tracker_result
        
        annotated_frame = frame.copy()
        annotated_frame, active_track_ids, self.total_count = helper.process_tracks(
            tracked_objects, annotated_frame, self.track_positions, self.counted_ids,
            self.min_track_length, self.counting_region, self.counting_line, self.total_count
        )
        annotated_frame = helper.draw_overlay(annotated_frame, self.counting_region, self.counting_line, self.total_count)
        
        helper.cleanup_old_tracks(self.track_positions, active_track_ids)
        return annotated_frame, self.total_count
    
    def process_video(self, video_path: str, output_path: str = None, save_video: bool = False) -> Dict:
        """Process entire video file and return counting results."""
        logger.info(f"Processing video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
        
        writer = helper.setup_video_writer(output_path, save_video, fps, width, height)
        frame_count = 0
        start_time = datetime.now()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                annotated_frame, current_count = self.process_frame(frame)
                
                if writer:
                    writer.write(annotated_frame)
                
                if frame_count % (fps * 10) == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% - Current count: {current_count}")
        
        except KeyboardInterrupt:
            logger.info("Processing interrupted by user")
        finally:
            cap.release()
            if writer:
                writer.release()
                logger.info(f"Video saved to: {output_path}" if writer else "No video writer to release")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Processing complete! Total pizzas: {self.total_count} in {processing_time:.2f}s")
        
        return {
            'video_path': video_path,
            'total_pizzas_counted': self.total_count,
            'frames_processed': frame_count,
            'processing_time_seconds': processing_time,
            'fps_processed': frame_count / processing_time if processing_time > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'model_used': self.model_path,
            'confidence_threshold': self.confidence_threshold
        }


def main():
    parser = argparse.ArgumentParser(description='Pizza Counter Application')
    parser.add_argument('--video', '-v', required=True, help='Path to input video file')
    parser.add_argument('--model', '-m', default='model_data/weights/best.pt', 
                       help='Path to YOLO model file')
    parser.add_argument('--config', help='Path to YAML configuration file')
    parser.add_argument('--save-video', action='store_true', 
                       help='Save annotated video')
    parser.add_argument('--confidence', '-c', type=float, default=None,
                       help='Confidence threshold for detections (overrides config)')
    
    args = parser.parse_args()
    
    counter = PizzaCounter(args.model, confidence_threshold=args.confidence, config_path=args.config)
    
    if args.confidence is not None:
        logger.info(f"Using command-line confidence threshold: {counter.confidence_threshold}")
    else:
        logger.info(f"Using config confidence threshold: {counter.confidence_threshold}")
    
    output_path = None
    if args.save_video:
        video_name = Path(args.video).stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"/app/output/{video_name}_processed_{timestamp}.mp4"
        logger.info(f"Auto-generated output path: {output_path}")
    
    try:
        results = counter.process_video(
            args.video, 
            output_path, 
            args.save_video
        )
        
        results_path = f"/app/output/pizza_count_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {results_path}")
        print(f"\n🍕 FINAL RESULTS 🍕")
        print(f"Total Pizzas Counted: {results['total_pizzas_counted']}")
        print(f"Processing Time: {results['processing_time_seconds']:.2f} seconds")
        print(f"Results saved to: {results_path}")
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

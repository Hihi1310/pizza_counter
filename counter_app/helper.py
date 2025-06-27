"""
Helper functions for Pizza Counter
Contains counting region, line crossing detection logic, and processing helpers.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Set
from centroid_tracker import CentroidTracker

logger = logging.getLogger(__name__)

def set_counting_region(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int, int, int]:
    """Set rectangular counting region."""
    counting_region = (x1, y1, x2, y2)
    logger.info(f"Counting region set to: {counting_region}")
    return counting_region

def is_in_counting_region(bbox: Tuple[int, int, int, int], counting_region: Optional[Tuple[int, int, int, int]]) -> bool:
    """Check if bounding box center is in counting region."""
    if counting_region is None:
        return True
        
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    region_x1, region_y1, region_x2, region_y2 = counting_region
    return (region_x1 <= center_x <= region_x2 and 
            region_y1 <= center_y <= region_y2)

def crosses_counting_line(bbox: Tuple[int, int, int, int], track_id: int, 
                         counting_line: Optional[Tuple[int, int, int, int]], 
                         track_positions: Dict[int, List[Tuple[int, int]]]) -> bool:
    """Check if object crosses counting line."""
    if counting_line is None:
        return False
        
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    if track_id not in track_positions:
        track_positions[track_id] = []
    
    track_positions[track_id].append((center_x, center_y))
    
    if len(track_positions[track_id]) > 5:
        track_positions[track_id] = track_positions[track_id][-5:]
    
    if len(track_positions[track_id]) < 2:
        return False
    
    line_x1, line_y1, line_x2, line_y2 = counting_line
    prev_x, prev_y = track_positions[track_id][-2]
    curr_x, curr_y = track_positions[track_id][-1]
    
    if abs(line_x2 - line_x1) < abs(line_y2 - line_y1):
        line_x = (line_x1 + line_x2) // 2
        return (prev_x < line_x < curr_x) or (curr_x < line_x < prev_x)
    else:
        line_y = (line_y1 + line_y2) // 2
        return (prev_y < line_y < curr_y) or (curr_y < line_y < prev_y)

def cleanup_old_tracks(track_positions: Dict[int, List[Tuple[int, int]]], active_track_ids: set) -> None:
    """Clean up position history for tracks that are no longer active."""
    inactive_tracks = set(track_positions.keys()) - active_track_ids
    for track_id in inactive_tracks:
        del track_positions[track_id]

def extract_detections(results) -> List[List[float]]:
    """Extract valid detections from YOLO results."""
    detections = []
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                try:
                    coords = box.xyxy[0].cpu().numpy()
                    if len(coords) != 4:
                        continue
                    
                    x1, y1, x2, y2 = map(float, coords)
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if class_id == 0 and all(0 <= v < 10000 for v in [x1, y1, x2, y2]) and 0.0 <= confidence <= 1.0:
                        detections.append([x1, y1, x2, y2])
                except Exception as e:
                    logger.error(f"Error processing detection: {e}")
    return detections

def safe_tracker_update(tracker, detections, config) -> Dict:
    """Safely update tracker with fallback reinitialization."""
    try:
        return tracker.update(detections)
    except Exception as e:
        logger.error(f"Tracker error: {e}")
        try:
            logger.info("Reinitializing tracker...")
            max_disappeared = config.get('TRACKING_CONFIG', 'max_disappeared', 30)
            max_distance = config.get('TRACKING_CONFIG', 'max_distance', 50)
            new_tracker = CentroidTracker(max_disappeared=max_disappeared, max_distance=max_distance)
            return new_tracker.update(detections), new_tracker
        except Exception as e2:
            logger.error(f"Failed to reinitialize tracker: {e2}")
            return {}, tracker

def process_tracks(tracked_objects, annotated_frame, track_positions, counted_ids, 
                  min_track_length, counting_region, counting_line, total_count) -> Tuple[np.ndarray, Set, int]:
    """Process tracked objects and draw annotations."""
    active_track_ids = set()
    current_count = total_count
    
    for track_id, track_data in tracked_objects.items():
        try:
            active_track_ids.add(track_id)
            centroid_x, centroid_y, x1, y1, x2, y2 = track_data
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            if track_id not in track_positions:
                track_positions[track_id] = []
            
            track_length = len(track_positions.get(track_id, []))
            should_count = (track_length >= min_track_length and 
                          should_count_object((x1, y1, x2, y2), track_id, counting_region, counting_line, track_positions))
            
            if should_count and track_id not in counted_ids:
                counted_ids.add(track_id)
                current_count += 1
                logger.info(f"Pizza #{current_count} counted (Track ID: {track_id})")
            
            color = (0, 255, 0) if track_id in counted_ids else (0, 0, 255)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, f"Pizza ID: {track_id}", 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        except Exception as e:
            logger.warning(f"Error processing track {track_id}: {e}")
    
    return annotated_frame, active_track_ids, current_count

def should_count_object(bbox, track_id, counting_region, counting_line, track_positions) -> bool:
    """Determine if object should be counted based on region/line rules."""
    if counting_region:
        return is_in_counting_region(bbox, counting_region)
    elif counting_line:
        return crosses_counting_line(bbox, track_id, counting_line, track_positions)
    return True

def draw_overlay(frame, counting_region, counting_line, total_count) -> np.ndarray:
    """Draw counting regions/lines and total count overlay."""
    if counting_region:
        x1, y1, x2, y2 = counting_region
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, "Counting Region", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    if counting_line:
        x1, y1, x2, y2 = counting_line
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.putText(frame, "Counting Line", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    cv2.putText(frame, f"Total Pizzas: {total_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    return frame

def setup_video_writer(output_path, save_video, fps, width, height):
    """Setup video writer if needed."""
    if not save_video or not output_path:
        return None
    
    logger.info(f"Initializing video writer for: {output_path}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not writer.isOpened():
        logger.error(f"Failed to initialize video writer")
        return None
    
    logger.info("Video writer initialized successfully")
    return writer

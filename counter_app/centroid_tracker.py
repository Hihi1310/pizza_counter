#!/usr/bin/env python3
"""
Simple Centroid Tracker for Pizza Counter
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Set
from scipy.spatial import distance as dist
from collections import OrderedDict

class CentroidTracker:
    def __init__(self, max_disappeared: int = 30, max_distance: int = 50) -> None:
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid: Tuple[int, int]) -> None:
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id: int) -> None:
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections: List[List[float]]) -> Dict[int, Tuple[int, int, float, float, float, float]]:
        """Update tracker with new detections. Returns dict of {object_id: (cx, cy, x1, y1, x2, y2)}"""
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return {}

        input_centroids = []
        for detection in detections:
            x1, y1, x2, y2 = detection
            cx = int((x1 + x2) / 2.0)
            cy = int((y1 + y2) / 2.0)
            input_centroids.append((cx, cy))

        if len(self.objects) == 0:
            for i, centroid in enumerate(input_centroids):
                self.register(centroid)
        else:
            object_centroids = list(self.objects.values())
            object_ids = list(self.objects.keys())

            D = dist.cdist(np.array(object_centroids), input_centroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_row_indices = set()
            used_col_indices = set()

            for (row, col) in zip(rows, cols):
                if row in used_row_indices or col in used_col_indices:
                    continue

                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_row_indices.add(row)
                used_col_indices.add(col)

            unused_row_indices = set(range(0, D.shape[0])).difference(used_row_indices)
            unused_col_indices = set(range(0, D.shape[1])).difference(used_col_indices)

            if D.shape[0] >= D.shape[1]:
                for row in unused_row_indices:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_col_indices:
                    self.register(input_centroids[col])

        result = {}
        for object_id, centroid in self.objects.items():
            for i, detection in enumerate(detections):
                x1, y1, x2, y2 = detection
                det_cx = int((x1 + x2) / 2.0)
                det_cy = int((y1 + y2) / 2.0)
                if abs(det_cx - centroid[0]) < 5 and abs(det_cy - centroid[1]) < 5:
                    result[object_id] = (centroid[0], centroid[1], x1, y1, x2, y2)
                    break

        return result

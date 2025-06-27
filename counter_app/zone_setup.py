"""
Simple tool to define counting zones for pizza detection.
Run this to easily set up your counting region.
"""

import cv2
import json
import numpy as np
from pathlib import Path

class ZoneSelector:
    def __init__(self):
        self.points = []
        self.drawing = False
        self.zones = []
        
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for drawing zones."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.points = [(x, y)]
            
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            # Show preview rectangle
            img_copy = param['img'].copy()
            cv2.rectangle(img_copy, self.points[0], (x, y), (0, 255, 0), 2)
            cv2.imshow('Zone Setup', img_copy)
            
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.points.append((x, y))
            
            # Add zone
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            zone = {
                'type': 'rectangle',
                'coordinates': [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)],
                'name': f'zone_{len(self.zones) + 1}'
            }
            self.zones.append(zone)
            
            print(f"✅ Added zone: {zone['coordinates']}")
            
    def setup_zones_from_video(self, video_path):
        """Interactive zone setup from video frame."""
        cap = cv2.VideoCapture(video_path)
        
        # Get first frame
        ret, frame = cap.read()
        if not ret:
            print("❌ Could not read video")
            return None
            
        cap.release()
        
        print("🍕 Pizza Zone Setup")
        print("Instructions:")
        print("- Click and drag to draw rectangles")
        print("- Press 's' to save zones")
        print("- Press 'c' to clear all zones")
        print("- Press 'q' to quit")
        
        # Create larger, resizable window
        cv2.namedWindow('Zone Setup', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Zone Setup', self.mouse_callback, {'img': frame})
        
        while True:
            # Draw current zones
            display_frame = frame.copy()
            for i, zone in enumerate(self.zones):
                x1, y1, x2, y2 = zone['coordinates']
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display_frame, f"Zone {i+1}", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add instructions overlay
            cv2.putText(display_frame, "Press: S=Save, C=Clear, Q=Quit", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Zones: {len(self.zones)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.imshow('Zone Setup', display_frame)
            
            key = cv2.waitKey(30) & 0xFF
            
            if key == ord('q') or key == ord('Q') or key == 27:  # Q or ESC
                break
            elif key == ord('s') or key == ord('S'):
                if self.zones:
                    self.save_zones()
                    print(f"Saved {len(self.zones)} zones")
            elif key == ord('c') or key == ord('C'):
                if self.zones:
                    self.zones = []
                    print("Zones cleared")
        
        cv2.destroyAllWindows()
        return self.zones
    
    def save_zones(self):
        """Save zones to config file."""
        config = {
            'zones': self.zones
        }
        
        with open('zones_config.json', 'w') as f:
            json.dump(config, f, indent=2)

def create_simple_zones():
    """Create zones programmatically for common pizza kitchen layouts."""
    
    # Based on typical pizza counter dimensions
    zones = {
        'prep_area': {
            'type': 'rectangle', 
            'coordinates': [100, 200, 400, 500],  # x1, y1, x2, y2
            'name': 'Preparation Area'
        },
        'baking_counter': {
            'type': 'rectangle',
            'coordinates': [500, 150, 800, 450],
            'name': 'Baking Counter'
        },
        'packaging_zone': {
            'type': 'rectangle', 
            'coordinates': [200, 50, 600, 200],
            'name': 'Packaging Zone'
        }
    }
    
    return zones

def draw_zones_on_frame(frame, zones):
    """Draw zones on a frame for visualization."""
    overlay = frame.copy()
    
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
    
    for i, (zone_name, zone) in enumerate(zones.items()):
        if zone['type'] == 'rectangle':
            x1, y1, x2, y2 = zone['coordinates']
            color = colors[i % len(colors)]
            
            # Draw rectangle
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            
            # Add semi-transparent fill
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            
            # Add label
            cv2.putText(overlay, zone['name'], (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Blend with original frame
    alpha = 0.3
    frame_with_zones = cv2.addWeighted(frame, 1-alpha, overlay, alpha, 0)
    
    return frame_with_zones

def main():
    """Main function to set up zones."""
    print("🍕 Pizza Zone Setup Tool")
    print("Choose an option:")
    print("1. Interactive setup from video")
    print("2. Use predefined zones")
    print("3. Manual coordinate entry")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == '1':
        video_path = input("Enter video file path: ")
        if Path(video_path).exists():
            selector = ZoneSelector()
            zones = selector.setup_zones_from_video(video_path)
        else:
            print("❌ Video file not found")
            return
            
    elif choice == '2':
        zones = create_simple_zones()
        print("✅ Using predefined zones")
        
    elif choice == '3':
        print("Manual zone entry:")
        print("Enter coordinates as: x1,y1,x2,y2")
        coords = input("Baking zone coordinates: ")
        try:
            x1, y1, x2, y2 = map(int, coords.split(','))
            zones = {
                'baking_zone': {
                    'type': 'rectangle',
                    'coordinates': [x1, y1, x2, y2],
                    'name': 'Baking Zone'
                }
            }
            print("✅ Zone created")
        except:
            print("❌ Invalid coordinates format")
            return
    
    else:
        print("❌ Invalid choice")
        return
    
    # Save zones
    with open('zones_config.json', 'w') as f:
        json.dump({'zones': zones}, f, indent=2)
    
    print(f"💾 Saved {len(zones)} zones to zones_config.json")
    
    # Show zone info
    if isinstance(zones, dict):
        for name, zone in zones.items():
            print(f"Zone '{name}': {zone['coordinates']}")
    elif isinstance(zones, list):
        for i, zone in enumerate(zones):
            print(f"Zone {i+1}: {zone.get('coordinates', 'No coordinates')}")
    else:
        print("Zones saved successfully")

if __name__ == "__main__":
    main()

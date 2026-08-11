import math
from typing import Dict, List, Tuple

try:
    from scipy.optimize import linear_sum_assignment  # type: ignore[import-untyped]
except ImportError:
    linear_sum_assignment = None


def compute_iou(box1: List[float], box2: List[float]) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    area2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0.0


class CentroidTracker:
    """
    Hungarian IoU & Centroid Multi-Object Tracker (Version 3.0).
    Uses Hungarian algorithm matching + IoU metrics to eliminate identity swaps when occupants cross paths.
    """

    def __init__(self, max_disappeared: int = 15, max_distance: float = 100.0) -> None:
        self.next_object_id: int = 1
        self.objects: Dict[int, Tuple[int, int]] = {}  # id -> (cx, cy)
        self.boxes: Dict[int, List[float]] = {}       # id -> [x1, y1, x2, y2]
        self.disappeared: Dict[int, int] = {}          # id -> count
        self.max_disappeared: int = max_disappeared
        self.max_distance: float = max_distance

    def register(self, centroid: Tuple[int, int], box: List[float]) -> int:
        object_id = self.next_object_id
        self.objects[object_id] = centroid
        self.boxes[object_id] = box
        self.disappeared[object_id] = 0
        self.next_object_id += 1
        return object_id

    def deregister(self, object_id: int) -> None:
        del self.objects[object_id]
        del self.boxes[object_id]
        del self.disappeared[object_id]

    def update(self, rects: List[List[float]]) -> Dict[int, List[float]]:
        """
        Update tracker with new bounding boxes [x1, y1, x2, y2].
        Returns mapping of persistent object_id -> [x1, y1, x2, y2, cx, cy].
        """
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self._get_tracked_dict()

        input_centroids = []
        for box in rects:
            cx = int((box[0] + box[2]) / 2.0)
            cy = int((box[1] + box[3]) / 2.0)
            input_centroids.append((cx, cy))

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i], rects[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            object_boxes = list(self.boxes.values())

            # Combined cost matrix (Distance penalty minus IoU bonus)
            cost_matrix = []
            for r in range(len(object_ids)):
                row = []
                for c in range(len(rects)):
                    dist = math.hypot(object_centroids[r][0] - input_centroids[c][0], object_centroids[r][1] - input_centroids[c][1])
                    iou = compute_iou(object_boxes[r], rects[c])
                    # Higher IoU reduces overall cost
                    cost = dist * (1.0 - 0.5 * iou)
                    row.append(cost)
                cost_matrix.append(row)

            used_rows = set()
            used_cols = set()

            if linear_sum_assignment is not None:
                row_ind, col_ind = linear_sum_assignment(cost_matrix)
                for r, c in zip(row_ind, col_ind):
                    if cost_matrix[r][c] > self.max_distance:
                        continue
                    object_id = object_ids[r]
                    self.objects[object_id] = input_centroids[c]
                    self.boxes[object_id] = rects[c]
                    self.disappeared[object_id] = 0
                    used_rows.add(r)
                    used_cols.add(c)
            else:
                # Greedy fallback
                pairs = []
                for r in range(len(object_ids)):
                    for c in range(len(input_centroids)):
                        pairs.append((cost_matrix[r][c], r, c))
                pairs.sort(key=lambda x: x[0])

                for cost, r, c in pairs:
                    if r in used_rows or c in used_cols:
                        continue
                    if cost > self.max_distance:
                        continue

                    object_id = object_ids[r]
                    self.objects[object_id] = input_centroids[c]
                    self.boxes[object_id] = rects[c]
                    self.disappeared[object_id] = 0
                    used_rows.add(r)
                    used_cols.add(c)

            unused_rows = set(range(len(object_ids))) - used_rows
            unused_cols = set(range(len(input_centroids))) - used_cols

            for r in unused_rows:
                object_id = object_ids[r]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            for c in unused_cols:
                self.register(input_centroids[c], rects[c])

        return self._get_tracked_dict()

    def _get_tracked_dict(self) -> Dict[int, List[float]]:
        result = {}
        for obj_id, box in self.boxes.items():
            cx, cy = self.objects[obj_id]
            result[obj_id] = list(box[:4]) + [float(cx), float(cy)]
        return result


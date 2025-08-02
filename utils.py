def eye_aspect_ratio(eye):
    from scipy.spatial import distance
    v1 = distance.euclidean(eye[1], eye[5])
    v2 = distance.euclidean(eye[2], eye[4])
    h = distance.euclidean(eye[0], eye[3])
    ear = (v1 + v2) / (2.0 * h)
    return ear

def log_distraction(event):  # Unused in current code, kept for compatibility
    print(f"[DEBUG] Distraction: {event}")
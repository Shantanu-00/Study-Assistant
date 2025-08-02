import mediapipe as mp
print("Mediapipe imported successfully!")
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
print("FaceMesh initialized!")
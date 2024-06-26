import sys
import cv2
import face_recognition
from PIL import Image
import numpy as np
import hashlib
import cryptidy.asymmetric_encryption

# Documentation Reference: https://medium.com/@charlietapsell1989/python-pixelation-6fc490307a05

def shuffle_pixels(face, key):
    # Convert the key to a seed for the random number generator
    seed = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % 10**8
    rng = np.random.default_rng(seed)

    # Flatten the face array and shuffle it
    shuffled_face = face.flatten()
    rng.shuffle(shuffled_face)

    # Reshape the shuffled array back to the original shape
    shuffled_face = shuffled_face.reshape(face.shape)

    return shuffled_face


def unshuffle_pixels(shuffled_face, key):
    # Convert the key to a seed for the random number generator
    seed = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % 10**8
    rng = np.random.default_rng(seed)

    # Generate a permutation that can unshuffle the pixels
    permutation = rng.permutation(len(shuffled_face.flatten()))

    # Flatten the shuffled face array and unshuffle it
    unshuffled_face = shuffled_face.flatten()[permutation.argsort()]

    # Reshape the unshuffled array back to the original shape
    unshuffled_face = unshuffled_face.reshape(shuffled_face.shape)

    return unshuffled_face

# Get the video file path from command line argument
video_file = sys.argv[1]

# Open the input video file
cap = cv2.VideoCapture(video_file)

# Get the video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (frame_width, frame_height))

# Initialize face_locations list
face_locations = []

while True:
    # Grab a single frame of video
    ret, frame = cap.read()
    
    if not ret:
        break

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces in the current frame of video
    face_locations = face_recognition.face_locations(rgb_frame)

    # Pixelate each face
    for top, right, bottom, left in face_locations:
        face = rgb_frame[top:bottom, left:right]
        private_key, public_key = cryptidy.asymmetric_encryption.generate_keys(2048)
        shuffled_face = shuffle_pixels(face, private_key)
        # Append private keys to a file
        with open('private_keys.txt', 'a') as file:
            file.write(private_key)
            file.write('\n\n')
        # Append the shuffled faces (type: numpy.ndarray) to a file
        with open('shuffled_faces.txt', 'a') as file:
            file.write(str(shuffled_face))
            file.write('\n\n')
        frame[top:bottom, left:right] = shuffled_face[:, :, ::-1]
      
    out.write(frame)
    cv2.imshow('Video', frame)
    # Wait for Enter key to stop
    if cv2.waitKey(25) == 13:
        break

# Release input and output video objects
cap.release()
out.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
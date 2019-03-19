import threading
import time
import face_recognition
import psycopg2
import feedparser
import urllib.request
import random
import cv2
import numpy as np
import os
import logging

#  Reference to Image folder
# IMAGES_PATH = 'C:\\Programming\\Python\\Facial Recognition\\Facial Rec-DatSciLab\\images\\'
# try:
#     conn = psycopg2.connect(host="localhost", database="thesis", user="postgres", password="root")
# except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
# finally:
#     if conn is not None:
#         conn.close()
try:
    conn = psycopg2.connect(host="localhost", database="thesis", user="postgres", password="root")
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
SUM =''
IMAGES_PATH = "C:\\Users\\Dre\\Desktop\\Thesis\\web\\thesis\\facial_recognition\\Image"
CAMERA_DEVICE_ID = 0
MAX_DISTANCE = 0.4


def get_face_embeddings_from_image(image, convert_to_rgb=False):
    """
    Take raw image and run both face dectection and ebmedding model on it
    """

    # Convert from BGR to RGB if needed (OpenCV reads in BGR, face_recognition reads in RGB)
    if convert_to_rgb:
        image = image[:, :, ::-1]

    # run detection model to determine facial locations
    face_locations = face_recognition.face_locations(image)

    # Run embedding model to get embeddings for the supplied locations
    face_encodings = face_recognition.face_encodings(image, face_locations)

    return face_locations, face_encodings


def setup_database():
    """
    Load reference images and create a database of their faec encodings
    """
    database = {}

    # for filename in glob.glob(os.path.join(IMAGES_PATH, '')):
    for root, dirs, files in os.walk(IMAGES_PATH):
        for file in files:
            filename = os.path.join(IMAGES_PATH, file)
            # Load image
            image_rgb = face_recognition.load_image_file(filename)

            # Use name in filename as the identity key
            identity = os.path.splitext(os.path.basename(filename))[0]

            # Get face encoding and link it to the identity
            locations, encodings = get_face_embeddings_from_image(image_rgb)
            database[identity] = encodings[0]

    return database


def paint_detected_face_on_image(frame, location, name=None):
    """
    Paint a rectangle around the face and write the name
    """

    # Unpack the coordinates from the location tuple
    top, right, bottom, left = location

    if name is None:
        name = 'unknown'
        color = (0, 0, 255)  # Red for unrecognized face
    else:
        color = (0, 128, 0)  # Dark green for recognized face

    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

    # Draw a label with the name around the face
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)


def arx(search_query):
    base_url = 'http://export.arxiv.org/api/query?';
    # Search parameters
    # search for electron in all fields
    num = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    start = random.choice(num)
    # retreive the first 5 results
    max_results = 1
    # global author, title, author
    query = 'search_query=%s&start=%i&max_results=%i' % (search_query, start, max_results)

    # Opensearch metadata such as totalResults, startIndex,
    # and itemsPerPage live in the opensearch namespase.
    # Some entry metadata lives in the arXiv namespace.
    # This is a hack to expose both of these namespaces in
    # feedparser v4.1
    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

    # perform a GET request using the base_url and query
    response = urllib.request.urlopen(base_url + query).read()
    if response:
        # parse the response using feedparser
        feed = feedparser.parse(response)
    else:
        print('Could not connect')
        # Run through each entry, and print out information
    for entry in feed.entries:
        author = entry.author
        title = entry.title
        summary = entry.summary
    return summary, title, author

def run_face_recognition(database):
    """
    Start Facial recognition via the webcam
    """
    # Open connection to the camera
    dre = ''
    video_capture = cv2.VideoCapture(CAMERA_DEVICE_ID)

    # The face recognition library uses keys and values of your database separately
    known_face_encodings = list(database.values())
    known_face_names = list(database.keys())

    # Read from cammera in a loop, frame by frame
    while video_capture.isOpened():
        # Grab a single frame of video

        ok, frame = video_capture.read()

        if not ok:
            logging.error("Could not read frame from camera. Stopping video capture.")
            break;

        # Run detection and embedd models
        face_locations, face_encodings = get_face_embeddings_from_image(frame, convert_to_rgb=True)

        # Loop through each face inthe frame of the video and see if there is a  match
        for location, face_encoding in zip(face_locations, face_encodings):

            # Get the distances from this encoding to those of all reference images
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            # Select the closest match (smallest distance) if it's below the threshold value
            if np.any(distances <= MAX_DISTANCE):
                best_match_idx = np.argmin(distances)
                name = known_face_names[best_match_idx]
                sql = "SELECT name, interest FROM thesis_user WHERE name = %s"
                cur = conn.cursor()
                cur.execute(sql, (name,))
                result = cur.fetchall()
                for x in result:
                    interest = x[1]
                    h = random.choice(interest)
                    v = str(h).replace(' ', '%20')
                # summary_f, title, author = arx(v)
                # first_filter = str(summary_f).replace('\\n', ' ')
                # second_filter = first_filter.replace('(\'', '\'')
                # summary = second_filter.replace('\')', '\'')
                cur.close()
                return name, v

            else:
                name = None
        #      # Show recognition info on the image
        #     paint_detected_face_on_image(frame, location, name)
        #
        # # Display the image
        # cv2.imshow('Testing', frame)
        # # Hit 'q' on the keyboard to stop the loop
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        nobody = 'none'
        return nobody, 'yhyh'
    video_capture.release()
    # Close the window

    cv2.destroyAllWindows()
    # Release handle to webcam








database = setup_database()
# thread_facial_recognition = threading.Thread(target=run_face_recognition, args=(database,))
# thread_facial_recognition.start()

import face_recognition
import cv2
import psycopg2
import feedparser
import urllib.request
import random
import time
import os
import logging

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
try:
    conn = psycopg2.connect(host="localhost", database="thesis", user="postgres", password="root")
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


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


def main(student, interest):
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    obama_image = face_recognition.load_image_file("C:\\Users\\Dre\\Desktop\\Thesis\\web\\thesis\\facial_recognition\\Image\\" + student + ".jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        obama_face_encoding,
    ]
    known_face_names = [
        "" + student + "",
    ]

    # Initialize some variables
    face_locations = []
    face_names = []
    process_this_frame = True
    x = time.time()
    while True and (time.time() - x) < 10:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    # sql = "SELECT name, interest FROM thesis_user WHERE name = %s"
                    # cur = conn.cursor()
                    # cur.execute(sql, (name,))
                    # result = cur.fetchall()
                    # for x in result:
                    #     interest = x[1]
                    #     h = random.choice(interest)
                    v = str(interest).replace(' ', '%20')
                    summary_f, title, author = arx(v)
                    first_filter = str(summary_f).replace('\\n', ' ')
                    second_filter = first_filter.replace('(\'', '\'')
                    summary = second_filter.replace('\')', '\'')
                    # cur.close()
                    if name is student:
                        return summary, title, author
                face_names.append(name)
        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    dre = 'nothing'
    return dre, 'uhu', 'ihui'
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

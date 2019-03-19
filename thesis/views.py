from django.shortcuts import render
from django.http import Http404
from .models import User
from.facial_recognition import facial_recognition, face_recognition
from django.shortcuts import redirect


# Create your views here.
def index(request):
    student, interest = facial_recognition.run_face_recognition(facial_recognition.database)

    if student is 'none':
        return render(request, 'thesis/home.html')
    else:
        context ={
            'interests': interest,
            'students': student,
        }
        return render(request, 'thesis/main.html', context)


def main(request, student, interest):
    summary, title, author = face_recognition.main(student, interest)
    if summary is 'nothing':
        return redirect('/')
    else:
        context ={
            'summarys': summary,
            'titles': title,
            'authors': author,
            'interests': interest,
            'students': student,
        }
        return render(request, 'thesis/index.html', context)

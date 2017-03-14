from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render_to_response
from django.template import RequestContext
 
def index(request):
    if request.method == 'POST' and request.FILES['nba.jpg']:
        myfile = request.FILES['nba.jpg']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'home/index.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'home/index.html')
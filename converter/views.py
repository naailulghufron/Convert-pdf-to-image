from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from pdf2image import convert_from_bytes
from pdf2image import convert_from_path
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

class ConvertPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        # print(file)
        # return file
        if not file:
            return Response({"error": "No file provided"}, status=400)

        temp_path = default_storage.save(f"uploads/{file.name}", ContentFile(file.read()))
        temp_full_path = default_storage.path(temp_path)
# return (temp_full_path)
        try:
            # images = convert_from_bytes(file.read())
            # images = convert_from_bytes('sample.pdf',500, poppler_path=r'C:\poppler\Library\bin')
            images = convert_from_path(temp_full_path,500, poppler_path=r'C:\poppler\Library\bin')
            # images = convert_from_path('sample.pdf',500, poppler_path=r'C:\poppler\Library\bin')
            image_urls = []
            for i, image in enumerate(images):
                # return (image)
                image_path = f"output/{file.name}_page_{i+1}.png"
                image.save(default_storage.path(image_path), "PNG")
                image_urls.append(default_storage.url(image_path))
                # return Response({"image_urls": image_urls})
                # return (image)

            return Response({"message": "Conversion successful", "images": image_urls})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


from django.http import FileResponse, JsonResponse
from rest_framework.views import APIView
from pdf2image import convert_from_path
import os
import zipfile
import uuid

# POPPLER_PATH = "/usr/bin"  # Untuk Linux
POPPLER_PATH = r"C:\poppler\Library\bin"  # untuk Windows
MEDIA_DIR = "media/"  # Folder untuk menyimpan hasil konversi

class ConvertPDFView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)

        pdf_file = request.FILES['file']
        original_name = os.path.splitext(pdf_file.name)[0]  # Ambil nama asli tanpa ekstensi
        unique_id = str(uuid.uuid4())[:8]  # Gunakan 8 karakter pertama UUID
        pdf_name = f"{original_name}_{unique_id}"  # Format nama unik
        pdf_path = os.path.join(MEDIA_DIR, f"{pdf_name}.pdf")

        # Simpan PDF yang diunggah
        with open(pdf_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        try:
            # Konversi PDF ke gambar (semua halaman)
            images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
            image_paths = []
            zip_filename = os.path.join(MEDIA_DIR, f"{pdf_name}.zip")  # Nama ZIP sesuai PDF

            # Simpan setiap halaman sebagai gambar
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for i, img in enumerate(images):
                    image_path = os.path.join(MEDIA_DIR, f"{pdf_name}_page_{i+1}.png")
                    img.save(image_path, "PNG")
                    zipf.write(image_path, os.path.basename(image_path))
                    image_paths.append(image_path)

            # Kembalikan ZIP sebagai respons
            return FileResponse(open(zip_filename, 'rb'), content_type="application/zip", as_attachment=True, filename=f"{pdf_name}.zip")
            # with open(zip_filename, 'rb') as zip_file:
            #     response = FileResponse(zip_file, content_type="application/zip", as_attachment=True, filename=f"{pdf_name}.zip")

            # return response


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        finally:
            # Hapus file sementara setelah selesai
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            for img_path in image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
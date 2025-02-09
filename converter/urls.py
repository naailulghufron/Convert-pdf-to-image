from django.urls import path
from .views import ConvertPDFView

urlpatterns = [
    path("convert/", ConvertPDFView.as_view(), name="convert_pdf"),
]

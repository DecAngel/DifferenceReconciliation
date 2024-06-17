from django.urls import path

from . import views

urlpatterns = [
    path("documents/", views.DocumentView.as_view(), name="documents"),
    path("entries/<int:document_id>/", views.DEView.as_view(), name="entries"),
    path("difference/<int:document_id>/", views.DDView.as_view(), name="difference"),
    path("", views.ResultView.as_view(), name="result"),
]

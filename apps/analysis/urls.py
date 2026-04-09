from django.urls import path

from .views import AnalysisListView, AnalysisView

urlpatterns = [
    path("analysis/create/", AnalysisView.as_view(), name="analysis_create"),
    path("analysis/<int:pk>/", AnalysisView.as_view(), name="analysis_detail"),
    path("analysis/list/", AnalysisListView.as_view(), name="analysis_list"),
]

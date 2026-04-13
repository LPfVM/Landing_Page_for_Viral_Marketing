from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Analysis
from .serializers import AnalysisResponseSerializer, AnalysisSerializer
from .services import AnalysisService


@extend_schema(tags=["Analysis"])
class AnalysisSwaggerView(APIView):
    pass


@extend_schema(tags=["Analysis"])
class AnalysisListSwaggerView(generics.ListAPIView):
    pass


class AnalysisView(AnalysisSwaggerView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(request=AnalysisSerializer)
    def post(self, request):
        serializer = AnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        analysis = AnalysisService(
            user=request.user,
            about=data["about"],
            type_of_time=data["period_type"],
            period_start=data["period_start"],
            period_end=data["period_end"],
        ).run()

        if analysis is None:
            return Response(
                {"detail": "해당 기간에 거래 내역이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            AnalysisResponseSerializer(analysis).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses=AnalysisResponseSerializer)
    def get(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
        return Response(AnalysisResponseSerializer(analysis).data)


class AnalysisListView(AnalysisListSwaggerView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AnalysisResponseSerializer

    def get_queryset(self):
        queryset = Analysis.objects.filter(user=self.request.user)
        period_type = self.request.query_params.get("period_type")
        if period_type:
            queryset = queryset.filter(type=period_type)
        return queryset

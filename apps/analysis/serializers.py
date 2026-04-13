from rest_framework import serializers

from .models import Analysis


class AnalysisSerializer(serializers.Serializer):
    about = serializers.ChoiceField(choices=Analysis.AboutChoices.choices)
    period_type = serializers.ChoiceField(choices=Analysis.TypeOfTimeChoices.choices)
    period_start = serializers.DateField()
    period_end = serializers.DateField()

    def validate(self, data):
        if data["period_start"] > data["period_end"]:
            raise serializers.ValidationError("시작일이 종료일 보다 클 수 없습니다.")
        return data


class AnalysisResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = (
            "about",
            "period_start",
            "period_end",
            "type",
            "description",
            "result_image",
        )

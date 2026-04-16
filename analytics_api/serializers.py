from rest_framework import serializers
from .models import DimCompany, FactMlScores, FactProfitLoss

class MlScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactMlScores
        fields = '__all__'

class ProfitLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactProfitLoss
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    # Include latest score nested
    latest_score = serializers.SerializerMethodField()
    
    class Meta:
        model = DimCompany
        fields = '__all__'

    def get_latest_score(self, obj):
        score = FactMlScores.objects.filter(symbol=obj.id).order_by('-computed_at').first()
        if score:
            return MlScoresSerializer(score).data
        return None

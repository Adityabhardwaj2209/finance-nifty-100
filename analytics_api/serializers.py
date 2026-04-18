from rest_framework import serializers
from .models import (
    DimCompany, FactMlScores, FactProfitLoss, 
    FactBalanceSheet, FactCashFlow, FactProsAndCons
)

class MlScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactMlScores
        fields = '__all__'

class ProfitLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactProfitLoss
        fields = '__all__'

class BalanceSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactBalanceSheet
        fields = '__all__'

class CashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactCashFlow
        fields = '__all__'

class ProsAndConsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactProsAndCons
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    latest_score = serializers.SerializerMethodField()
    financial_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = DimCompany
        fields = '__all__'

    def get_latest_score(self, obj):
        score = FactMlScores.objects.filter(symbol=obj.id).order_by('-computed_at').first()
        if score:
            return MlScoresSerializer(score).data
        return None

    def get_financial_summary(self, obj):
        # Latest P&L to show simple growth or sales
        latest_pl = FactProfitLoss.objects.filter(company_id=obj.id).order_by('-fiscal_year').first()
        if latest_pl:
            return {
                'sales': latest_pl.sales,
                'net_profit': latest_pl.net_profit,
                'year': latest_pl.year_label
            }
        return None

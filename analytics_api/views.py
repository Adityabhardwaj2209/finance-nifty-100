from rest_framework import viewsets
from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    DimCompany, FactMlScores, FactProfitLoss,
    FactBalanceSheet, FactCashFlow, FactProsAndCons
)
from .serializers import (
    CompanySerializer, MlScoresSerializer, ProfitLossSerializer,
    BalanceSheetSerializer, CashFlowSerializer, ProsAndConsSerializer
)

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows companies to be viewed.
    """
    queryset = DimCompany.objects.all().order_by('id')
    serializer_class = CompanySerializer

    @action(detail=True, methods=['get'])
    def full_profile(self, request, pk=None):
        """
        Get all data for a company: P&L, BS, CF, Scores, Pros/Cons.
        """
        company = self.get_object()
        pl = FactProfitLoss.objects.filter(company_id=pk).order_by('fiscal_year')
        bs = FactBalanceSheet.objects.filter(company_id=pk).order_by('fiscal_year')
        cf = FactCashFlow.objects.filter(company_id=pk).order_by('fiscal_year')
        scores = FactMlScores.objects.filter(symbol=pk).order_by('-computed_at')
        pc = FactProsAndCons.objects.filter(company_id=pk).first()

        scores_data = MlScoresSerializer(scores, many=True).data
        latest_score = scores_data[0] if scores_data else None

        hold_prediction = None
        if latest_score:
            health = latest_score.get('health_label', 'Unknown')
            growth = latest_score.get('growth_score', 0)
            prof = latest_score.get('profitability_score', 0)
            
            if health in ["Excellent", "Stable"] and growth > 7.0:
                duration = "Long Term (3 - 5+ Years)"
                rationale = "High structural growth and stable health indicators make this an excellent compounder to hold for multi-year horizons."
            elif health in ["Stable", "Average"] and prof > 5.0:
                duration = "Medium Term (1 - 3 Years)"
                rationale = "Moderate growth but stable profitability. Good for medium-term capital appreciation."
            else:
                duration = "Short Term / Watchful (< 1 Year)"
                rationale = "Elevated risk profile or stagnating metrics suggest limiting exposure to shorter trades or avoiding deep holds."
                
            hold_prediction = {
                'duration': duration,
                'rationale': rationale
            }

        return Response({
            'company': CompanySerializer(company).data,
            'profit_loss': ProfitLossSerializer(pl, many=True).data,
            'balance_sheet': BalanceSheetSerializer(bs, many=True).data,
            'cash_flow': CashFlowSerializer(cf, many=True).data,
            'scores': scores_data,
            'pros_cons': ProsAndConsSerializer(pc).data if pc else None,
            'hold_prediction': hold_prediction
        })

class ScoresViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FactMlScores.objects.all().order_by('-computed_at')
    serializer_class = MlScoresSerializer

class SectorViewSet(viewsets.ViewSet):
    def list(self, request):
        from django.db import connection
        with connection.cursor() as cursor:
            query = """
                SELECT c.sector, AVG(s.overall_score) as avg_score, COUNT(c.id) as company_count
                FROM dim_company c
                JOIN fact_ml_scores s ON c.id = s.symbol
                JOIN (
                    SELECT symbol, MAX(computed_at) as max_date
                    FROM fact_ml_scores
                    GROUP BY symbol
                ) latest ON s.symbol = latest.symbol AND s.computed_at = latest.max_date
                WHERE c.sector IS NOT NULL
                GROUP BY c.sector
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
        data = [
            {'sector': row[0], 'avg_score': round(row[1], 2), 'company_count': row[2]}
            for row in rows
        ]
        return Response(data)

class FinancialsViewSet(viewsets.ViewSet):
    """
    Helper ViewSet for getting specific financial statements by symbol.
    """
    def list(self, request):
        return Response({"message": "Use /api/companies/<symbol>/full_profile/ for complete data"})

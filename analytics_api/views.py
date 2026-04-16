from rest_framework import viewsets
from django.db.models import Avg, Count
from rest_framework.response import Response
from .models import DimCompany, FactMlScores
from .serializers import CompanySerializer, MlScoresSerializer

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows companies to be viewed.
    """
    queryset = DimCompany.objects.all().order_by('id')
    serializer_class = CompanySerializer

class ScoresViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows health scores to be viewed.
    """
    queryset = FactMlScores.objects.all().order_by('-computed_at')
    serializer_class = MlScoresSerializer

class SectorViewSet(viewsets.ViewSet):
    """
    API endpoint for sector-wise performance aggregation.
    """
    def list(self, request):
        # Calculate avg scores per sector
        # Optimize by fetching the latest score for each company in a single batch
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Compatible alternative for older SQLite versions
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

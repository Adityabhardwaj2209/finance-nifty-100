from django.db import models

class DimCompany(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    company_name = models.CharField(max_length=255)
    company_logo = models.URLField(null=True, blank=True)
    about_company = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    nse_profile = models.URLField(null=True, blank=True)
    bse_profile = models.URLField(null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    sub_sector = models.CharField(max_length=100, null=True, blank=True)
    face_value = models.FloatField(null=True, blank=True)
    book_value = models.FloatField(null=True, blank=True)
    roce_percentage = models.FloatField(null=True, blank=True)
    roe_percentage = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'dim_company'

class FactProfitLoss(models.Model):
    id = models.AutoField(primary_key=True)
    company_id = models.CharField(max_length=20)
    fiscal_year = models.IntegerField()
    year_label = models.CharField(max_length=20)
    sales = models.FloatField(null=True)
    expenses = models.FloatField(null=True)
    operating_profit = models.FloatField(null=True)
    opm_percentage = models.FloatField(null=True)
    net_profit = models.FloatField(null=True)
    net_profit_margin_pct = models.FloatField(null=True)
    eps = models.FloatField(null=True)
    
    class Meta:
        managed = False
        db_table = 'fact_profit_loss'

class FactBalanceSheet(models.Model):
    id = models.AutoField(primary_key=True)
    company_id = models.CharField(max_length=20)
    fiscal_year = models.IntegerField()
    year_label = models.CharField(max_length=20)
    equity_capital = models.FloatField(null=True)
    reserves = models.FloatField(null=True)
    borrowings = models.FloatField(null=True)
    total_assets = models.FloatField(null=True)
    debt_to_equity = models.FloatField(null=True)

    class Meta:
        managed = False
        db_table = 'fact_balance_sheet'

class FactCashFlow(models.Model):
    id = models.AutoField(primary_key=True)
    company_id = models.CharField(max_length=20)
    fiscal_year = models.IntegerField()
    year_label = models.CharField(max_length=20)
    operating_activity = models.FloatField(null=True)
    investing_activity = models.FloatField(null=True)
    financing_activity = models.FloatField(null=True)
    net_cash_flow = models.FloatField(null=True)

    class Meta:
        managed = False
        db_table = 'fact_cash_flow'

class FactProsAndCons(models.Model):
    id = models.AutoField(primary_key=True)
    company_id = models.CharField(max_length=20)
    pros = models.TextField(null=True)
    cons = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = 'fact_prosandcons'

class FactMlScores(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=20)
    overall_score = models.FloatField()
    profitability_score = models.FloatField()
    growth_score = models.FloatField()
    leverage_score = models.FloatField()
    cashflow_score = models.FloatField()
    health_label = models.CharField(max_length=20)
    computed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'fact_ml_scores'

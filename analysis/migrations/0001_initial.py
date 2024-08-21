# Generated by Django 5.1 on 2024-08-21 10:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('asset_id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('currency_code', models.CharField(choices=[('USD', 'US Dollar'), ('NZD', 'New Zealand Dollar'), ('AUD', 'Australian Dollar'), ('JPY', 'Japanese Yen'), ('CNY', 'Chinese Yuan'), ('GBP', 'British Pound'), ('EUR', 'Euro'), ('CAD', 'Canadian Dollar'), ('SGD', 'Singapore Dollar')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioAsset',
            fields=[
                ('portfolio_asset_id', models.AutoField(primary_key=True, serialize=False)),
                ('position', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost_basis', models.DecimalField(decimal_places=2, max_digits=15)),
                ('targeted_ratio', models.DecimalField(decimal_places=2, max_digits=5)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.asset')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.portfolio')),
            ],
        ),
    ]
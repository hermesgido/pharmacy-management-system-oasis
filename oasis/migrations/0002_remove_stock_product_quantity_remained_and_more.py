# Generated by Django 4.1.3 on 2022-11-10 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oasis', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock_product',
            name='quantity_remained',
        ),
        migrations.AddField(
            model_name='stock_product',
            name='quantity_sold',
            field=models.IntegerField(default=0, verbose_name='Quantity Sold'),
        ),
        migrations.AlterField(
            model_name='user',
            name='key',
            field=models.CharField(blank=True, default='2Q6ESD7AXLG2HJXAFEIOYZ2GX3NBRCBR', max_length=200, null=True),
        ),
    ]

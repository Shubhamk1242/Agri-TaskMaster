# Generated by Django 4.2 on 2023-05-19 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='farmer',
            table='tblFarmer',
        ),
        migrations.AlterModelTable(
            name='labour',
            table='tblLabour',
        ),
        migrations.AlterModelTable(
            name='ratings',
            table='tblRatings',
        ),
        migrations.AlterModelTable(
            name='task',
            table='tblTask',
        ),
        migrations.AlterModelTable(
            name='workstatus',
            table='tblWorkStatus',
        ),
    ]

# Generated by Django 4.2.2 on 2024-06-12 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting_difference', '0002_accountingentry_direction_alter_accountingproof_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.BooleanField(default=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='PrimaryDifference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('prefix', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='PrimarySubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('prefix', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SecondaryDifference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=10)),
                ('primary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.primarydifference')),
            ],
        ),
        migrations.CreateModel(
            name='SecondarySDRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.secondarydifference')),
            ],
        ),
        migrations.CreateModel(
            name='SecondarySubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=10)),
                ('primary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.primarysubject')),
            ],
        ),
        migrations.RenameModel(
            old_name='AccountingProof',
            new_name='Proof',
        ),
        migrations.DeleteModel(
            name='AccountingEntry',
        ),
        migrations.AddField(
            model_name='secondarysdrelationship',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.secondarysubject'),
        ),
        migrations.AddField(
            model_name='entry',
            name='proof',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.proof'),
        ),
        migrations.AddField(
            model_name='entry',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.secondarysubject'),
        ),
    ]

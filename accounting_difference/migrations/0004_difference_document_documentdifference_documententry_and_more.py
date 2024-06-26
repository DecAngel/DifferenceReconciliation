# Generated by Django 4.2.2 on 2024-06-16 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting_difference', '0003_entry_primarydifference_primarysubject_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Difference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('primary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.difference')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=100)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='DocumentDifference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('difference_sec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.difference')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.document')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.BooleanField(default=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.document')),
            ],
        ),
        migrations.CreateModel(
            name='SDRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difference_sec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.difference')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('primary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.subject')),
            ],
        ),
        migrations.RemoveField(
            model_name='secondarydifference',
            name='primary',
        ),
        migrations.RemoveField(
            model_name='secondarysdrelationship',
            name='difference',
        ),
        migrations.RemoveField(
            model_name='secondarysdrelationship',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='secondarysubject',
            name='primary',
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
        migrations.DeleteModel(
            name='PrimaryDifference',
        ),
        migrations.DeleteModel(
            name='PrimarySubject',
        ),
        migrations.DeleteModel(
            name='Proof',
        ),
        migrations.DeleteModel(
            name='SecondaryDifference',
        ),
        migrations.DeleteModel(
            name='SecondarySDRelationship',
        ),
        migrations.DeleteModel(
            name='SecondarySubject',
        ),
        migrations.AddField(
            model_name='sdrelationship',
            name='subject_sec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.subject'),
        ),
        migrations.AddField(
            model_name='documententry',
            name='subject_sec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_difference.subject'),
        ),
    ]

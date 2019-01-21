# Generated by Django 2.1.5 on 2019-01-20 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0023_auto_20190120_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_account', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Bank account',
                'verbose_name_plural': 'Bank accounts',
            },
        ),
        migrations.AddField(
            model_name='donorpaymentchannel',
            name='bank_account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='bankaccounts', to='aklub.BankAccount'),
        ),
        migrations.AlterUniqueTogether(
            name='donorpaymentchannel',
            unique_together={('VS', 'bank_account')},
        ),
    ]
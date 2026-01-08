"""
Initial migration for Dynamic wallet authentication.
Creates the WalletAddress model.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=42)),
                ('chain', models.CharField(
                    choices=[
                        ('eip155:1', 'Ethereum'),
                        ('eip155:137', 'Polygon'),
                        ('eip155:56', 'BSC'),
                        ('eip155:42161', 'Arbitrum')
                    ],
                    default='eip155:1',
                    max_length=32
                )),
                ('is_primary', models.BooleanField(default=False)),
                ('dynamic_user_id', models.CharField(
                    blank=True,
                    db_index=True,
                    max_length=128,
                    null=True
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='wallet_addresses',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Wallet Address',
                'verbose_name_plural': 'Wallet Addresses',
                'unique_together': {('address', 'chain')},
            },
        ),
    ]

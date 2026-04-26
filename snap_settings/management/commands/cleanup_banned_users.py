from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from snap_settings.models import BannedUser

class Command(BaseCommand):
    help = 'Deletes users who have been banned/deactivated for more than 14 days.'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=14)
        
        # Find ban records older than 14 days
        expired_bans = BannedUser.objects.filter(banned_at__lt=cutoff_date)
        
        count = expired_bans.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired bans found. Clean up skipped.'))
            return
            
        for ban_record in expired_bans:
            user = ban_record.user
            username = user.username
            user.delete() # This cascades and deletes the BannedUser record as well
            self.stdout.write(self.style.SUCCESS(f'Deleted user {username} after 14-day ban period.'))
            
        self.stdout.write(self.style.SUCCESS(f'Cleanup complete. Total users deleted: {count}'))

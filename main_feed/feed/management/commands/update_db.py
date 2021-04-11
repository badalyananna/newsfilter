from django.core.management.base import BaseCommand, CommandError
from feed.models import NewsPiece, Topic
from feed.views import scrape, contains_words, is_alert_news, filter_news
from datetime import datetime, timezone
import threading
from urllib.error import URLError
import pytz
from accounts.models import User

class Command(BaseCommand):
    help = "Update the database every one hour"

    def handle(self, *args, **options):
        def update():
            try:
                for user in User.objects.all():
                    user.last_upd = datetime.now(timezone.utc)
                    scrape(user)
                    user.save()
                    filter_news(user)
                
                print(f'The database was updated at {datetime.now(pytz.timezone("Asia/Tashkent"))}')              
            except URLError:
                print(f'{datetime.now(pytz.timezone("Asia/Tashkent"))} URLError occured, restarting in 10 minutes.')
                threading.Timer(600, update).start()
        update()
        return

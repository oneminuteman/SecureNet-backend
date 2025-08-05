from django.core.management.base import BaseCommand
from securanet.models import KnownSite
from securanet.utils.compare import get_html_signature

class Command(BaseCommand):
    help = 'Fetch and cache HTML signatures for all known sites'

    def handle(self, *args, **kwargs):
        count = 0
        for site in KnownSite.objects.all():
            if not site.html_signature:
                self.stdout.write(f"⏳ Caching HTML for {site.domain}...")
                html = get_html_signature(site.url)
                if html:
                    site.html_signature = html
                    site.save()
                    self.stdout.write(self.style.SUCCESS(f"✅ Cached for {site.domain}"))
                    count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Failed for {site.domain}"))

        if count == 0:
            self.stdout.write(self.style.WARNING("No uncached signatures were found."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. Cached {count} signatures."))
from django.core.management.base import BaseCommand

from pages.models import SiteSettings
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Delete all Products, Categories, and SiteSettings (does not touch users or orders)'

    def handle(self, *args, **options):
        prod_count = Product.objects.count()
        cat_count = Category.objects.count()
        ss_count = SiteSettings.objects.count()

        self.stdout.write(
            f'This will delete {prod_count} product(s), {cat_count} category/ies, '
            f'and {ss_count} SiteSettings record(s).'
        )
        confirm = input('Type YES to confirm: ').strip()
        if confirm != 'YES':
            self.stdout.write(self.style.WARNING('Aborted.'))
            return

        Product.objects.all().delete()
        Category.objects.all().delete()
        SiteSettings.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {prod_count} product(s), {cat_count} category/ies, '
                f'{ss_count} SiteSettings record(s).'
            )
        )

import csv

from django.core.management.base import BaseCommand

from operaQuizbot.helpers import facebook_get_json
from operaQuizbot.models import FacebookPage, OperaCategory


class Command(BaseCommand):
    help = "Adds the operas from a CSV file."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with open('operaQuizbot/management/commands/fbpages.csv', 'r') as f:
            # Open the opera categories CSV
            dr = csv.DictReader(f, dialect='excel')
            dr = [x for x in dr]
            for x in dr:
                print(x)

        for row in dr:
            if row['name']:
                res = facebook_get_json('search', params={"type": "page",
                                                          "q": row['name']})
                print(res)

                page, _ = FacebookPage.objects.get_or_create(facebook_id=res["data"][0]["id"], name=res["data"][0]["name"])

                categories = row['categories'].split("/")
                categories = [OperaCategory.objects.get_or_create(name=x)[0] for x in categories]
                for x in categories:
                    x.save()
                    page.categories.add(x)

        self.stdout.write(self.style.SUCCESS("Imported the Facebook Pages!"))

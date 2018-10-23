import csv
from operaQuizbot.models import Opera, OperaCategory

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Adds the operas from a CSV file."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with open('operaQuizbot/management/commands/operas.csv','r') as f:
            # Open the opera categories CSV
            dr = csv.DictReader(f, dialect='excel')
            dr = [x for x in dr]
            for x in dr:
                print(x)

        # Delete all the existing operas and categories
        Opera.objects.all().delete()
        OperaCategory.objects.all().delete()

        for row in dr:
            opera, _ = Opera.objects.get_or_create(name=row['OPERA'], url=row['URL'], description=row['Description'])

            categories = (row['FILM GENRE TAG'].split("/") +
                          row['MUSIC TAG'].split("/") +
                          [row['length']])
            categories = [OperaCategory.objects.get_or_create(name=x)[0] for x in categories if x!='']
            for x in categories:
                x.save()
                opera.categories.add(x)

        self.stdout.write(self.style.SUCCESS("Imported the operas!"))
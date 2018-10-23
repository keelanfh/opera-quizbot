import csv

from django.core.management.base import BaseCommand

from operaQuizbot.models import FinancialCategory, OperaGoerCategory, ApproachCultureCategory


class Command(BaseCommand):
    help = "Adds the questions from a CSV file."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        for x in [FinancialCategory, OperaGoerCategory, ApproachCultureCategory]:
            x.objects.all().delete()

        with open('operaQuizbot/management/commands/profilecategories.csv', 'r') as f:
            # Open the opera categories CSV
            dr = csv.DictReader(f, dialect='excel')
            dr = [x for x in dr]
            financials = [x["financial"] for x in dr if not x["financial"].strip() == '']
            opera_goers = [x["opera_goers"] for x in dr if not x["opera_goers"].strip() == '']
            culture_approaches = [x["culture_approach"] for x in dr if not x["culture_approach"].strip() == '']

            models = [FinancialCategory, OperaGoerCategory, ApproachCultureCategory]

            for n, listy in enumerate([financials, opera_goers, culture_approaches]):
                model = models[n]
                for x, name in enumerate(listy):
                    model.objects.create(id=x + 1, name=name)

        self.stdout.write(self.style.SUCCESS("Imported the Profiling Categories!"))
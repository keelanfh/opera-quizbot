import csv

from django.core.management.base import BaseCommand

from operaQuizbot.models import DidYouKnowQuestion, FinancialCategory, OperaGoerCategory, ApproachCultureCategory


class Command(BaseCommand):
    help = "Adds the did you knows from a CSV file."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        DidYouKnowQuestion.objects.all().delete()

        with open('operaQuizbot/management/commands/didyouknow.csv', 'r') as f:
            # Open the opera categories CSV
            dr = csv.DictReader(f, dialect='excel')

            for x in dr:
                print(x)
                if x['link']:
                    link = x['link']
                else:
                    link = ''

                if x['picture']:
                    image = x['picture']
                else:
                    image = ''
                dyk = DidYouKnowQuestion(text=x['text'], link_url=link, image_url=image)
                dyk.save()
                if not x['financial'] == 'x':
                    financial_ids = x['financial'].split(',')
                else:
                    financial_ids = [1,2,3,4]
                fins = FinancialCategory.objects.filter(pk__in=financial_ids)

                for fin in fins:
                    dyk.financial.add(fin)

                if not x['opera_goer'] == 'x':
                    opera_goer_ids = x['opera_goer'].split(',')
                else:
                    opera_goer_ids = [1,2,3,4,5]
                ops = OperaGoerCategory.objects.filter(pk__in=opera_goer_ids)

                for op in ops:
                    dyk.opera_goer.add(op)

                if not x['culture_event'] == 'x':
                    culture_event_ids = x['culture_event'].split(',')
                else:
                    culture_event_ids = [1,2,3,4,5]
                accs = ApproachCultureCategory.objects.filter(pk__in=culture_event_ids)

                for acc in accs:
                    dyk.approach_culture.add(acc)


                dyk.save()
        self.stdout.write(self.style.SUCCESS("Imported the 'Did you Know' statements!"))
import csv

from django.core.management.base import BaseCommand

from operaQuizbot.models import Question, OperaCategory, Answer, AnswerCategoryWeighting


class Command(BaseCommand):
    help = "Adds the questions from a CSV file."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with open('operaQuizbot/management/commands/questions.csv', 'r') as f:
            # Open the opera categories CSV
            dr = csv.DictReader(f, dialect='excel')
            dr = [x for x in dr]
            for x in dr:
                print(x)

        # Delete all the existing questions
        Question.objects.all().delete()
        Answer.objects.all().delete()
        AnswerCategoryWeighting.objects.all().delete()

        # Loop through the questions, only considering those that actually have text in them
        for row in dr:
            if row['question_text']:
                question, _ = Question.objects.get_or_create(id=row['question_no'], text=row['question_text'])

                # Loop through three answers on sheet
                for x in range(1, 4):
                    # If the answer is there
                    if row["answer{}_text".format(x)]:
                        # Get the answer
                        answer, _ = Answer.objects.get_or_create(text=row["answer{}_text".format(x)], question=question)

                        # Reading the format in which the weights are added
                        weights = row["answer{}_categories".format(x)].split("/")
                        weights = [x.strip(")").split("(") for x in weights]

                        for x in weights:
                            # Create the category if you need to
                            category, _ = OperaCategory.objects.get_or_create(name=x[0])
                            print(f"Creating acw with answer {answer.id}, category {category} and weighting {x[1]}")
                            acw = AnswerCategoryWeighting.objects.create(answer=answer,
                                                                         category=category,
                                                                         weighting=x[1])
                            acw.save()

        # Now set the 'next question' variables.
        # We have to do this afterwards because you can't set a question as the next question
        # when it hasn't been created yet.
        for row in dr:
            if row['question_text'] and row['next_question']:
                q = Question.objects.get(id=row["question_no"])
                nq = Question.objects.get(id=row["next_question"])
                # If no 'next question' is set, that won't be added.
                # We then move to the end of the quiz after that question.
                q.next_question = nq
                q.save()

        self.stdout.write(self.style.SUCCESS("Imported the questions!"))

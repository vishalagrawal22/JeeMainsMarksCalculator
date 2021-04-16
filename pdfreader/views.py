import csv
import io
import os
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import permission_required
from .models import MCQQuestion, SAQuestion
from django.contrib import messages
import fitz
import re

# Create your views here.


def fake_calculate(request):
    context = upload(request)
    return render(request, "upload2.html", context)


def calculate(request):
    context = upload(request)
    return render(request, "upload.html", context)


def upload(request):
    context = {}
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['document']
        except:
            messages.error(
                request, 'Please upload your response key, you may consider watching the video tutorial if you do not know how to get pdf of response key')
            return {"ERROR": "EMPTY INPUT"}
        if not uploaded_file.name.endswith(".pdf"):
            messages.error(
                request, 'Uploaded file is not a pdf file, you may consider watching the video tutorial if you do not know how to get pdf of response key')
        else:
            fs = FileSystemStorage()
            fs.save(uploaded_file.name, uploaded_file)
            pdf_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            doc = fitz.open("{}".format(pdf_path))
            no_of_pages = doc.pageCount
            question_MCQ_ids = []
            question_SA_ids = []
            option_ids = []
            score_negative = 0
            correct_MCQ_ids = []
            correct_SA_ids = []
            temp_list = []
            q_type = 0
            ansNext = False
            score = 0
            wrongAnswerList = [[], [], []]
            page = doc.loadPage(0)
            text = page.getText()
            texts = text.split("\n")
            regex_name = re.compile("^Candidate Name$")
            next_line_name = False
            for line in texts:
                search_name = re.search(regex_name, line)
                if (search_name != None):
                    next_line_name = True
                elif (next_line_name):
                    name = list(line.split())
                    if(len(name) == 2):
                        context['firstName'] = name[0][0]+name[0][1:].lower()
                        context['lastName'] = name[1][0]+name[1][1:].lower()
                    if (len(name) == 3):
                        context['firstName'] = name[0][0] + name[0][1:].lower()
                        context['lastName'] = name[1][0] + name[1][1:].lower() + \
                            " " + name[2][0] + name[2][1:].lower()
                    next_line_name = False

            regex_type = re.compile("^Question Type : (.*)$")
            regex_q = re.compile("^Question ID : (.*)$")
            regex_a = re.compile("^Option (.) ID : (.*)$")
            regex_ca = re.compile("^Chosen Option : (.*)$")
            regex_sca = re.compile("^Answer :$")
            for i in range(no_of_pages):
                page = doc.loadPage(i)
                text = page.getText()
                texts = text.split("\n")
                for line in texts:
                    search_type = re.findall(regex_type, line)
                    if(search_type != []):
                        if(search_type[0] == "MCQ"):
                            q_type = 0
                        elif(search_type[0] == "SA"):
                            q_type = 1

                    search_q = re.findall(regex_q, line)
                    if(q_type == 0):
                        if(search_q != []):
                            question_MCQ_ids.append(search_q[0])
                    elif(q_type == 1):
                        if(search_q != []):
                            question_SA_ids.append(search_q[0])

                    search_a = re.findall(regex_a, line)
                    if(search_a != []):
                        temp_list.append(search_a[0][1])
                        if(search_a[0][0] == '4'):
                            option_ids.append(temp_list)
                    search_ca = re.findall(regex_ca, line)
                    if(search_ca != []):
                        if(search_ca[0] == "--"):
                            correct_MCQ_ids.append("-")
                        else:
                            correct_MCQ_ids.append(
                                temp_list[int(search_ca[0])-1])
                        temp_list = []
                    search_sca = re.findall(regex_sca, line)
                    if(search_sca != []):
                        ansNext = True
                    elif(ansNext):
                        correct_SA_ids.append(line)
                        ansNext = False
            doc.close()
            for i in range(len(question_MCQ_ids)):
                if(correct_MCQ_ids[i] != "-"):
                    obj = MCQQuestion.objects.filter(
                        QuestionId=question_MCQ_ids[i])
                    if not obj.exists():
                        messages.error(
                            request, 'looks like you have uploaded a pdf which is either a previous years response key of jee or not at all related to jee')
                        return render(request, 'upload.html', context)
                    result = obj[0].AnswerId
                    if(result == ("-"*10)):
                        score += 4
                    elif(result == correct_MCQ_ids[i]):
                        score += 4
                    elif(result != correct_MCQ_ids[i]):
                        section = (i//20)+1
                        wrongAnswerList[section-1].append([(i % 20)+1, (option_ids[i].index(
                            correct_MCQ_ids[i])+1), (option_ids[i].index(result)+1)])
                        score -= 1
                        score_negative += 1

            for i in range(len(question_SA_ids)):
                if(correct_SA_ids[i] != "--"):
                    obj = SAQuestion.objects.filter(
                        QuestionId=question_SA_ids[i])
                    if not obj.exists():
                        messages.error(
                            request, 'looks like you have uploaded a pdf which is either a previous years response key of jee or not at all related to jee')
                        return render(request, 'upload.html', context)

                    result = obj[0].Answer
                    if(result == ("-"*10)):
                        score += 4

                    elif("or" not in result and "OR" not in result and "TO" not in result and "to" not in result):
                        if(float(result) == float(correct_SA_ids[i])):
                            score += 4
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

                    elif(("or" in result or "OR" in result) and ("TO" not in result and "to" not in result)):
                        if("or" in result):
                            answers = list(map(str.strip, result.split("or")))
                        else:
                            answers = list(map(str.strip, result.split("OR")))
                        answers = list(map(float, answers))
                        if(float(correct_SA_ids[i]) in answers):
                            score += 4
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

                    elif(("or" not in result and "OR" not in result) and ("TO" in result or "to" in result)):
                        if("to" in result):
                            answers = list(map(str.strip, result.split("to")))
                        else:
                            answers = list(map(str.strip, result.split("TO")))
                        if(float(answers[0]) <= float(correct_SA_ids[i]) <= float(answers[1])):
                            score += 4
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

                    elif("to" in result and "or" in result):
                        answers = list(map(str.strip, result.split("or")))
                        for relation in answers:
                            if("to" in relation):
                                x = list(map(str.strip, relation.split("to")))
                                if(float(x[0]) <= float(correct_SA_ids[i]) <= float(x[1])):
                                    score += 4
                                    break
                            elif(float(relation) == float(correct_SA_ids[i])):
                                score += 4
                                break
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

                    elif("TO" in result and "or" in result):
                        answers = list(map(str.strip, result.split("or")))
                        for relation in answers:
                            if("TO" in relation):
                                x = list(map(str.strip, relation.split("TO")))
                                if(float(x[0]) <= float(correct_SA_ids[i]) <= float(x[1])):
                                    score += 4
                                    break
                            elif(float(relation) == float(correct_SA_ids[i])):
                                score += 4
                                break
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

                    elif("to" in result and "OR" in result):
                        answers = list(map(str.strip, result.split("OR")))
                        for relation in answers:
                            if("to" in relation):
                                x = list(map(str.strip, relation.split("to")))
                                if(float(x[0]) <= float(correct_SA_ids[i]) <= float(x[1])):
                                    score += 4
                                    break
                            elif(float(relation) == float(correct_SA_ids[i])):
                                score += 4
                                break
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

                    elif("TO" in result and "OR" in result):
                        answers = list(map(str.strip, result.split("OR")))
                        for relation in answers:
                            if("TO" in relation):
                                x = list(map(str.strip, relation.split("TO")))
                                if(float(x[0]) <= float(correct_SA_ids[i]) <= float(x[1])):
                                    score += 4
                                    break
                            elif(float(relation) == float(correct_SA_ids[i])):
                                score += 4
                                break
                        else:
                            section = (i // 5) + 1
                            wrongAnswerList[section - 1].append(
                                [21 + (i % 5), correct_SA_ids[i], result])

            for i in range(len(wrongAnswerList)):
                if len(wrongAnswerList[i]) == 0:
                    wrongAnswerList[i].append(['NA', 'NA', 'NA'])

            context['listfortable'] = wrongAnswerList
            context['positive'] = score + score_negative
            context['negative'] = score_negative
            context['marks'] = score
            context['physics'] = wrongAnswerList[0]
            os.remove(pdf_path)

    return context


@permission_required('admin.can_add_log_entry')
def data_upload(request):
    if(request.method == 'GET'):
        return render(request, "dataupload.html")
    elif(request.method == 'POST'):
        csv_file = request.FILES['csvfile']
        csv_file_2 = request.FILES['csvfile2']

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        for column in csv.reader(io_string, delimiter=","):
            _, created = MCQQuestion.objects.update_or_create(
                QuestionId=column[0],
                AnswerId=column[1]
            )

        data_set_2 = csv_file_2.read().decode('UTF-8')
        io_string_2 = io.StringIO(data_set_2)
        for column in csv.reader(io_string_2, delimiter=","):
            _, created = SAQuestion.objects.update_or_create(
                QuestionId=column[0],
                Answer=column[1]
            )
    return render(request, 'dataupload.html')


@permission_required('admin.can_add_log_entry')
def delete_everything(request):
    if(request.method == 'POST'):
        MCQQuestion.objects.all().delete()
        SAQuestion.objects.all().delete()
    return render(request, 'deleteall.html')

import json
import traceback
import jieba
import re
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from extract_tags import find_resume_by_id
from loadFile.constant_position import ConstantPosition

category_keywords = ConstantPosition.category_keywords


@csrf_exempt
def resume_tag(request):
    if request.method == "POST":
        son = {}
        try:
            tag_list = []
            code = "0000"
            cv_id = request.POST.get("cv_id")
            source = request.POST.get("source")
            type = request.POST.get("type")
            doc = find_resume_by_id(cv_id, source)
            if doc:
                tag_list = getResumeTag(doc, type)
                msg = "successful"
            else:
                code = "0001"
                msg = "current resume is missing."
            son["code"] = code
            son["msg"] = msg
            son["tag_list"] = tag_list
        except:
            son = {"code": "0002", "msg": "program exception", "tag_list": []}
            traceback.print_exc()

        re = json.dumps(son)
        return HttpResponse(re)


def getResumeTag(doc, type):
    resume_info = doc["self_introduction"]
    workExperienceList = doc["workExperienceList"]
    projectList = doc["projectList"]
    for experience in workExperienceList:
        resume_info += experience["experience_desc"]
    for project in projectList:
        resume_info += project["project_desc"]

    word_list = get_jd_analysis(resume_info)
    return word_list


def get_jd_analysis(jd):
    word_list = []
    LENGTH = 6
    try:
        words = set(jieba.cut(jd))
        english_words = get_english_words(words)
        word_list.extend(list(english_words))
        if len(word_list) >= LENGTH:
            return word_list[:6]
        category_words = set(category_keywords[type]) & words
        word_list.extend(list(category_words))
        word_list = list(set(word_list))
        if len(word_list) >= LENGTH:
            return word_list[:6]
    except:
        print "extract keywords error"
    return word_list


def get_english_words(words):
    english_words = set()
    for word in words:
        if word.encode('utf-8').isalnum():
            if not word.encode('utf-8').isdigit() and len(word) > 2:
                english_words.add(word)
            elif len(word) == 2:
                match = re.search(u"\d", word)
                if not match:
                    english_words.add(word)
            elif len(word) == 1:
                word = word.lower()
                if word == "c":
                    english_words.add(word)
    return english_words
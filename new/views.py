import os
from pathlib import Path
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from .models_coko import CkDocuments, CkDocumentsDivisions, CkDocumentsLevels
import datetime
from django.template.defaultfilters import slugify as django_slugify
from django.views.generic import ListView, DetailView, CreateView
from ftplib import FTP


alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu',
            'я': 'ya'}

def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))


def name_folder_division(div):
    div_dict = {
        'Аттестация педагогических работников': 'att-ped-rab',
        'Аттестация руководящих работников': 'att-ruk-rab',
        'Исследование компетенций учителей': 'iss-komp-uch',
        'Независимая оценка квалификации': 'nez-oce-kva',
        'ГИА-11 (ЕГЭ, ГВЭ-11)': 'gia-11',
        'ГИА-9 (ОГЭ, ГВЭ-9)': 'gia-9',
        'Диагностика образовательных достижений учащихся': 'dia-obr-dos',
        'Анализ деятельности ОО и систем': 'ana-deya-oo',
        'Национальный проект "Образование"': 'nac-pro-obr',
        'Дополнительное профессиональное образование': 'dop-pro-obr',
    }
    return div_dict[div]


def check_auth(request):
    if request.user.is_authenticated:
        return False
    else:
        return True


def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    try:
        login(request, user)
    except:
        info = 'Неудачная попытка аутентификации'
        return render(request, 'registration/login.html', {'info': info})
    return HttpResponse('<meta http-equiv="refresh" content="0; URL=/">')


class DocsView(ListView): # Список документов в зависимости от выбранных параметров
    model = CkDocuments

    def get_queryset(self):
        return CkDocuments.objects.using('coko38').\
            filter(division_id=self.kwargs.get('id_div')).\
            filter(level_id=self.kwargs.get('id_lev')).order_by('-id')


def choice_docs(request): #Выбор направления и уровня принятия документа
    if check_auth(request):
        return HttpResponse('<meta http-equiv="refresh" content="0; URL=/accounts/login/">')
    if request.method == 'POST':
        division = request.POST['division']
        level = request.POST['level']
        id_div = CkDocumentsDivisions.objects.using('coko38').get(division=division).id
        id_lev = CkDocumentsLevels.objects.using('coko38').get(level=level).id
        return redirect('https://doc.coko38.ru/'+str(id_div)+'/'+str(id_lev)+'/')
    divisions = CkDocumentsDivisions.objects.using('coko38').all()
    levels = CkDocumentsLevels.objects.using('coko38').all()
    context = {
        'divisions': divisions,
        'levels': levels,
    }
    return render(request, 'new/edit/choice.html', context)


def main(request): #Главная страница
    if check_auth(request):
        return HttpResponse('<meta http-equiv="refresh" content="0; URL=/accounts/login/">')
    return render(request, 'new/main.html')


def delete(request, id): #Удаление документы (из базы и из папки)
    if check_auth(request):
        return HttpResponse('<meta http-equiv="refresh" content="0; URL=/accounts/login/">')
    rec = CkDocuments.objects.using('coko38').get(id=id)
    path = 'C:/inetpub/PHPSites/coko38.ru/bank'+rec.link
    #ftp = FTP('172.16.55.26')
    #ftp.login(settings.FTP_LOGIN, settings.FTP_PASSWORD)
    #ftp.delete(path)
    #os.remove(path)
    rec.delete(using='coko38')
    request.method = 'GET'
    return render (request, 'new/main.html', {'info': 'Документ успешно удален'})


def new(request): #Добавление нового документа
    if check_auth(request):
        return HttpResponse('<meta http-equiv="refresh" content="0; URL=/accounts/login/">')
    if request.method == 'POST':
        level = request.POST['level']
        division = request.POST['division']
        file = request.FILES['file']
        name = request.POST['name']
        trans_name = slugify(name)
        fold = name_folder_division(division)
        path = fold+"\\"+slugify(level)+"\\"+datetime.datetime.now().strftime("%d-%m-%Y")\
               +"\\"+trans_name[:40]+"_"+datetime.datetime.now().strftime("%H-%M-%S")+file.name[-4:]
        fs = FileSystemStorage()
        fs.save(path, file)
        new_rec = CkDocuments()
        new_rec.description = name
        new_rec.link = "/bank/"+fold+"/"+slugify(level)+"/"+datetime.datetime.now().strftime("%d-%m-%Y")\
                       +"/"+trans_name[:40]+"_"+datetime.datetime.now().strftime("%H-%M-%S")+file.name[-4:]
        new_rec.level_id = CkDocumentsLevels.objects.using('coko38').get(level=level).id
        new_rec.division_id = CkDocumentsDivisions.objects.using('coko38').get(division=division).id
        new_rec.theme_id = 1
        new_rec.save(using='coko38')
        return redirect('https://coko38.ru/index.php/aboutorganization/documents')
    levels = CkDocumentsLevels.objects.using('coko38').all()
    divisions = CkDocumentsDivisions.objects.using('coko38').all()
    context = {
        'levels': levels,
        'divisions': divisions,
    }
    return render(request, 'new/new/new.html', context)

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView
from .models import job_m_category
from .models import job_t_diary
from .models import job_t_comment
from datetime import datetime
from .forms import DiaryForm
from .forms import NameForm
from .forms import CommentForm
from .forms import CommnterName

# from diary.lib import analysis

# Create your views here.
def index(request):
  diaries = job_t_diary.objects.order_by('create_day')#日誌データを取得
  params={
    'diaries':diaries,
    'from':'index'
  }
  return render(request, 'diary/index.html', params)

def show(request, num):
  diary = job_t_diary.objects.get(id=num)
  comments = job_t_comment.objects.filter(comment_diary_id=num).order_by('create_day')
  name = CommnterName()
  commentForm = CommentForm()
  params={
    'diary':diary,
    'comments':comments,
    'nameForm':name,
    'commentForm':commentForm
  }
  # 何時間前の機能をつける
  return render(request, 'diary/show.html',params)

def create(request):
  categories = job_m_category.objects.all()
  if 'name' in request.session and 'body' in request.session and 'formName' in request.session and 'formDiary' in request.session:
    errorName = request.session['name']
    errorDiary = request.session['body']
    formName = request.session['formName']
    formDiary = request.session['formDiary']
    del request.session['name']
    del request.session['body']
    del request.session['formName']
    del request.session['formDiary']
    name = NameForm({'user_name':errorName})
    Diary = DiaryForm({'article':errorDiary})
  else:
    name = NameForm()
    Diary = DiaryForm()
    formName = ""
    formDiary = ""
  params={
    'categories':categories,
    'nameForm':name,
    'diaryForm':Diary,
    'formName':formName,
    'formDiary':formDiary
  }
  return render(request, 'diary/create.html', params)


def diaryForm(request):
  try:
    category_id = int(request.POST['category_id'])
    category = job_m_category.objects.get(id=category_id)
    userName = request.POST['user_name']#非ログイン時は入力した名前
    body = request.POST['article']
    if NameForm(request.POST).is_valid() and DiaryForm(request.POST).is_valid():
      user_id = 0 #非ログイン時のuser_idは0となる
      title = '日直日誌'
      createDay = datetime.now()
      diaryDate = job_t_diary(writer_name = userName, user_id=user_id, title=title, diary=body, category_id=category, create_day=createDay ,delete_frg=0, like_number=0, comment_number=0)
      diaryDate.save()
      return redirect(to='/diary')
    else:
      request.session['name'] = userName
      request.session['body'] = body
      request.session['formName'] = NameForm(request.POST).errors
      request.session['formDiary'] = DiaryForm(request.POST).errors
      return redirect('/diary/create')
  except Exception as e:
    return HttpResponse("システムエラー発生")

def commentForm(request, num):
  commenterName = request.POST['commenter']
  comment = request.POST['comment']
  user_id = 0
  diary_id = job_t_diary.objects.get(id=num)
  createDay = datetime.now()
  commentLength = int(diary_id.comment_number) + 1
  commentDate = job_t_comment(commenter_name = commenterName, user_id = user_id, comment = comment, delete_frg = 0, comment_diary_id = diary_id, create_day = createDay)
  commentDate.save()
  diary_id.comment_number = commentLength
  diary_id.save()
  response = redirect('/diary/show/'+str(num))
  return response

def searchForm(request):
  searchWord = request.POST["search"]
  if searchWord == "":
    response = redirect('/diary')
  else:
    hit_data = job_t_diary.objects.filter(writer_name__contains=searchWord).order_by('create_day')
    params={
      'diaries':hit_data,
      'from':'search'
    }
    response = render(request, 'diary/index.html', params)
  return response

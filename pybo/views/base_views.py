from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404

from ..models import Question, Answer, Category


def index(request, category_name='qna'):
    """
    pybo 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준

    category = get_object_or_404(Category, name=category_name)
    _question_list = Question.objects.filter(category__name=category.name)


    # 정렬
    _question_list = _question_list.annotate(
        num_voter=Count('voter', distinct=True)+Count('answer__voter', distinct=True),
        num_answer=Count('answer', distinct=True)+Count('comment', distinct=True)+Count('answer__comment', distinct=True))
    if so == 'recommend':
        _question_list = _question_list.order_by('-notice', '-num_voter', '-create_date')
    elif so == 'popular':
        _question_list = _question_list.order_by('-notice', '-num_answer', '-create_date')
    else:  # recent
        _question_list = _question_list.order_by('-notice', '-create_date')

    # 검색
    if kw:
        _question_list = _question_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
             Q(answer__content__icontains=kw) |  # 답변내용검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(_question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'category': category, 'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}
    return render(request, 'pybo/question_list.html', context)


def detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id)
    page = request.GET.get('page', '1')
    so = request.GET.get('so', 'recommend')

    # 정렬
    if so == 'recommend':
        answer_list = Answer.objects.filter(question=question).annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')

    else:
        answer_list = Answer.objects.filter(question=question).order_by('-create_date')

    paginator = Paginator(answer_list, 5)
    page_obj = paginator.get_page(page)

    context = {'question': question, 'answer_list': page_obj, 'page': page, 'so': so, 'category': question.category}
    return render(request, 'pybo/question_detail.html', context)

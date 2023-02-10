from django.core.paginator import Paginator

POSTS_IN_PAGE = 10


def get_page(request, post_list):
    paginator = Paginator(post_list, POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

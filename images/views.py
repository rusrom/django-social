from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import ImageCreateForm
from .models import Image

from common.decorators import ajax_required

from actions.utils import create_action

import redis
from django.conf import settings


# Connect to Redis
r = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            # cd = form.cleaned_data
            new_item = form.save(commit=False)
            # assign current user to the item
            new_item.user = request.user
            new_item.save()

            # Adding user actions to the activity stream
            create_action(request.user, 'bookmarked image', new_item)

            messages.success(request, 'Image added successfully')
            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())

    # build form with data provided by the bookmarklet via GET
    form = ImageCreateForm(data=request.GET)

    return render(
        request,
        'images/image/create.html',
        {
            'section': 'js',
            'form': form,
        }
    )


def image_details(request, id, slug):
    image = get_object_or_404(Image, pk=id, slug=slug)

    # Redis increment total image views by 1
    total_views = r.incr(f'image:{image.id}:views')

    # Redis image rating
    r.zincrby('image_ranking', 1, image.id)

    return render(
        request,
        'images/image/detail.html',
        {
            'section': 'images',
            'image': image,
            'total_views': total_views,
        }
    )


@login_required
def image_ranking(request):
    # get image ranking dictionary
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(image_id) for image_id in image_ranking]
    # get most viewed images
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed}
    )

@login_required
@ajax_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    status = 'ko'
    try:
        image = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        image = None
    if image and action in ['like', 'unlike']:
        status = 'ok'
        if action == 'like':
            image.users_likes.add(request.user)
            # Adding user actions to the activity stream
            create_action(request.user, 'likes', image)
        else:
            image.users_likes.remove(request.user)
    return JsonResponse({'status': status})


# @login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 5)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если переданная страница не является числом, возвращаем первую.
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # Если получили AJAX - запрос с номером страницы, большим, чем их количество,
            # возвращаем пустую страницу.
            return HttpResponse('')
        # Если номер страницы больше, чем их количество, возвращаем последнюю.
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(
            request,
            'images/image/list_ajax.html',
            {'section': 'images', 'images': images}
        )
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images}
    )

# def image_list(request):
#     images = Image.objects.all()
#     paginator = Paginator(images, 5)
#     page = request.GET.get('page')
#
#
#     images = paginator.get_page(page)
#     if request.is_ajax():
#         return render(
#             request,
#             'images/image/list_ajax.html',
#             {'section': 'images', 'images': images}
#         )
#     return render(
#         request,
#         'images/image/list.html',
#         {'section': 'images', 'images': images}
#     )


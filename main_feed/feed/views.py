from django.shortcuts import render, redirect
from datetime import datetime, timedelta
import pytz
import feedparser
from feed.models import NewsPiece, Topic, Website
from feed.forms import WebsiteForm, TopicForm, NewsPieceTopicForm
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from dateutil.parser import parse
from urllib.error import URLError
from django.contrib.auth.decorators import login_required
import traceback

# functions without views
def scrape(user):
    # make a set with website names that already exist in a database
    websites_set = set()
    websites_list = NewsPiece.objects.filter(user = user).order_by().values_list('website').distinct()
    for w in websites_list:
        websites_set.add(w[0])

    for site in Website.objects.filter(user = user):
        # handling errors if some website doesn't open
        try:
            nf = feedparser.parse(site.rss)
            print(user, site.name)

            if site.pk in websites_set:
                last_pub = NewsPiece.objects.filter(website = site).order_by('published')[::-1][0]

                for i in range(len(nf.entries)):
                    try:
                        piece_pub = datetime.strptime(nf.entries[i].published, "%a, %d %b %Y %H:%M:%S %z")
                    except ValueError:
                        try:
                            piece_pub = datetime.strptime(nf.entries[i].published, "%a, %d %b %Y %H:%M:%S")
                            piece_pub = piece_pub - timedelta(hours=5)
                            t = pytz.timezone('UTC')
                            piece_pub = t.localize(piece_pub)
                        except:
                            piece_pub = parse(nf.entries[i].published)
                    
                    except:
                        piece_pub = parse(nf.entries[i].published)
                    #print(piece_pub, last_pub)
                    if piece_pub > last_pub.published:
                        if nf.entries[i].title != last_pub.title:
                            piece_of_news = NewsPiece()
                            piece_of_news.website = site
                            piece_of_news.title = nf.entries[i].title
                            piece_of_news.published = piece_pub
                            piece_of_news.description = nf.entries[i].description
                            piece_of_news.link = nf.entries[i].link
                            piece_of_news.user = user
                            piece_of_news.save()
                        else:
                            pass
                    else:
                        pass
    
            else:
                for i in range(len(nf.entries)):
                    try:
                        piece_pub = datetime.strptime(nf.entries[i].published, "%a, %d %b %Y %H:%M:%S %z")
                    except ValueError:
                        try:
                            piece_pub = datetime.strptime(nf.entries[i].published, "%a, %d %b %Y %H:%M:%S")
                            piece_pub = piece_pub - timedelta(hours=5)
                            t = pytz.timezone('UTC')
                            piece_pub = t.localize(piece_pub)
                        except:
                            piece_pub = parse(nf.entries[i].published)
                    
                    except:
                        piece_pub = parse(nf.entries[i].published)

                    piece_of_news = NewsPiece()
                    piece_of_news.website = site
                    piece_of_news.title = nf.entries[i].title
                    piece_of_news.published = piece_pub
                    piece_of_news.description = nf.entries[i].description
                    piece_of_news.link = nf.entries[i].link
                    piece_of_news.user = user
                    piece_of_news.save()
        # handling errors if some website doesn't open
        except URLError:
            print(f"URLError occured. The website {site} has not been scraped.")
            pass
        except Exception as e:
            print(f"The {type(e)} error occurred. The website {site} has not been scraped.")
            traceback.print_exc()

    
    return redirect('../')

def contains_words(text, alert_words):
    for word in alert_words:
        if word in text:
            return True
    return False

def is_alert_news(news, alert_words, ignor_words):
    unnecessary_characters = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    empty_line = '                                '
    news = news.translate(str.maketrans(unnecessary_characters, empty_line))
    text = set(news.lower().split())
    
    if contains_words(text, alert_words):
        if not(contains_words(text, ignor_words)):
            return True
        else:
            return False
    else:
        return False

def filter_news(user):
    unfiltered_news = NewsPiece.objects.filter(user = user, filtered = False)

    for piece in unfiltered_news:
        text = (piece.title + ' ' + piece.description).lower()
        for item in Topic.objects.filter(user = user):
            if is_alert_news(text, item.key_words.split(), item.ignor_words.split()):
                piece.chosen = True
                piece.topics_filtered.add(item)
                piece.topics_assigned.add(item)
        piece.filtered = True
        piece.save()


# Create your views here.
@login_required
def main_dashboard(request):
    user = request.user
    #set all displayed to false
    NewsPiece.objects.filter(user = user).update(displayed = False)
    #then set the news that will be displayed to True
    unread_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, unread = True)
    if len(unread_news) > 20:
        pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False).order_by('-unread', '-published')[:20]
        ids = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False).order_by('-unread', '-published').values_list('id', flat = True)[:20]
        NewsPiece.objects.filter(id__in = ids).update(displayed = True)
    else:
        pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, unread = True).order_by('-published')
        NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, unread = True).update(displayed = True)
    
    context = {
        'object_list': pieces_of_news,
        'displayed_news': len(pieces_of_news),
        'undisplayed_news': len(NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, unread = False)),
        'topics': Topic.objects.filter(user = user).order_by('pk'),
        'websites': Website.objects.filter(user = user).order_by('pk'),
        'last_upd': request.user.last_upd,
        'website_form': WebsiteForm(),
        'topic_form': TopicForm(),
    }
    return render(request, 'main_dashboard.html', context)

@login_required
def handle_form(request):
    if 'rss' in request.POST:
        website_form = WebsiteForm(request.POST)
        if website_form.is_valid():
            entry = website_form.save(commit=False)
            entry.unread_pieces = 777
            entry.user = request.user
            entry.save()
    elif 'key_words' in request.POST:
        topic_form = TopicForm(request.POST)
        if topic_form.is_valid():
            entry = topic_form.save(commit=False)
            entry.unread_pieces = 777
            entry.user = request.user
            entry.save()
    else:
        pass
    return redirect(request.POST['next'])

def get_unread_values(user):
    topic_pk = Topic.objects.filter(user=user).values_list('pk', flat = True)
    topic_values = []
    for pk in topic_pk:
        pk_dict = {'id': 'topic' + str(pk), 'value': Topic.objects.filter(pk = pk)[0].unread_pieces}
        topic_values.append(pk_dict)

    website_pk = Website.objects.filter(user=user).values_list('pk', flat = True)
    website_values = []
    for pk in website_pk:
        pk_dict = {'id': 'web' + str(pk), 'value': Website.objects.filter(pk = pk)[0].unread_pieces}
        website_values.append(pk_dict)
    return topic_values, website_values

@login_required
def update(request):
    if request.method == "GET":
        user = request.user
        user.last_upd = datetime.now(pytz.timezone('UTC'))
        scrape(user)
        filter_news(user)
        user.save()
        category = request.GET['category']
        if category == "all":
            updated_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, unread = True, displayed = False).order_by('published')[::-1]
            #update the displayed status so that when we load old news, they won't be displayed
            NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, unread = True, displayed = False).update(displayed = True)
        elif category == "website":
            website_pk = request.GET['pk']
            updated_news =  NewsPiece.objects.filter(user = user, website = website_pk, unread = True, displayed = False).order_by('published')[::-1]
            #update the displayed status so that when we load old news, they won't be displayed
            NewsPiece.objects.filter(user = user, website = website_pk, unread = True, displayed = False).update(displayed = True)
        elif category == "topic":
            topic_pk = request.GET['pk']
            updated_news = NewsPiece.objects.filter(user = user, topics_assigned = topic_pk, unread = True, displayed = False).order_by('published')[::-1]
            #update the displayed status so that when we load old news, they won't be displayed
            NewsPiece.objects.filter(user = user, topics_assigned = topic_pk, unread = True, displayed = False).update(displayed = True)
        elif category == "important":
            updated_news = []
        
        context = {
            'object_list': updated_news,
            'displayed_news': len(NewsPiece.objects.filter(user = user, displayed = True)),
            'topics': Topic.objects.filter(user = user),
        }
        topic_unread_values, website_unread_values = get_unread_values(user)
        data = [{"last_upd": user.last_upd.astimezone().strftime("%B %d, %Y, %I:%M%p"),
                 "updated_content": render_to_string('news_card.html', context),
                 "topic_unread_values": topic_unread_values,
                 "website_unread_values": website_unread_values}]
        return JsonResponse(data, safe = False)
    else:
        return HttpResponse("Fail")

@login_required
def load_old(request):
    user = request.user
    if request.method == "GET" and request.is_ajax:
        category = request.GET['category']
        if category == "all":
            old_pieces = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, displayed = False).order_by('-unread', '-published')[:20]
            ids = NewsPiece.objects.filter(user = user, topics_assigned__isnull = False, displayed = False).order_by('-unread', '-published').reverse().values_list('id', flat = True)[:20]
        elif category == "website":
            website_pk = request.GET['pk']
            old_pieces = NewsPiece.objects.filter(user = user, website = website_pk, displayed = False).order_by('-unread', '-published')[:20]
            ids = NewsPiece.objects.filter(user = user, website = website_pk, displayed = False).order_by('-unread', '-published').values_list('id', flat = True)[:20]
        elif category == "topic":
            topic_pk = request.GET['pk']
            old_pieces = NewsPiece.objects.filter(user = user, topics_assigned = topic_pk, displayed = False).order_by('published')[::-1][:20]
            ids = NewsPiece.objects.filter(user = user, topics_assigned = topic_pk, displayed = False).order_by('published').reverse().values_list('id', flat = True)[:20]
        elif category == "important":
            topic_pk = request.GET['pk']
            if topic_pk == '0':
                old_pieces = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True, displayed = False).order_by('published')[::-1][:20]
                ids = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True, displayed = False).order_by('published').reverse().values_list('id', flat = True)[:20]
            else:
                old_pieces = NewsPiece.objects.filter(user = user, topics_assigned = topic_pk, important = True, displayed = False).order_by('published')[::-1][:20]
                ids = NewsPiece.objects.filter(user = user, topics_assigned = topic_pk, important = True, displayed = False).order_by('published').reverse().values_list('id', flat = True)[:20]
        else:
            return HttpResponse("Fail, no such category")

        NewsPiece.objects.filter(id__in = ids).update(displayed = True)

        context = {
            'object_list': old_pieces,
            'displayed_news': len(old_pieces),
            'topics': Topic.objects.filter(user = user), # here we use topics not websites because topics are used when displaying topics in the news card
        }
        return render(request, 'news_card.html', context)
        
    else:
        return HttpResponse("Fail")


@login_required
def news_important(request, topic_pk):
    user = request.user
    if topic_pk == "Other" or Topic.objects.get(pk = topic_pk).user == user:
        if topic_pk == "Other":
            topic = "Other"
            topic_pk = 0
            #set all displayed to false
            NewsPiece.objects.filter(user = user).update(displayed = False)
            #then set the news that will be displayed to True
            NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True, unread = True).update(displayed = True)
            pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True, unread = True).order_by('published')[::-1]
            if len(pieces_of_news) < 20:
                pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True).order_by('unread', 'published')[::-1][:20]

                ids = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True).order_by('unread', 'published').reverse().values_list('id', flat = True)[:20]
                NewsPiece.objects.filter(id__in = ids).update(displayed = True)

                undisplayed_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True).order_by('unread', 'published')[::-1][20:]
            else:
                undisplayed_news = NewsPiece.objects.filter(user = user, topics_assigned__isnull = True, important = True, unread = False)
        else:
            topic_object = Topic.objects.get(pk = topic_pk)
            #set all displayed to false
            NewsPiece.objects.filter(user = user).update(displayed = False)
            #then set the news that will be displayed to True
            NewsPiece.objects.filter(user = user, topics_assigned = topic_object, important = True, unread = True).update(displayed = True)

            pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned = topic_object, important = True, unread = True).order_by('published')[::-1]

            if len(pieces_of_news) < 20:
                pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned = topic_object, important = True).order_by('unread', 'published')[::-1][:20]

                ids = NewsPiece.objects.filter(user = user, topics_assigned = topic_object, important = True).order_by('unread', 'published').reverse().values_list('id', flat = True)[:20]
                NewsPiece.objects.filter(id__in = ids).update(displayed = True)
                undisplayed_news = NewsPiece.objects.filter(user = user, topics_assigned = topic_object, important = True).order_by('unread', 'published')[::-1][20:]
            else:
                undisplayed_news = NewsPiece.objects.filter(user = user, topics_assigned = topic_object, important = True, unread = False)
            topic = topic_object.name


        context = {
            'object_list': pieces_of_news,
            'displayed_news': len(pieces_of_news),
            'undisplayed_news': len(undisplayed_news),
            'topics': Topic.objects.filter(user = user).order_by('pk'),
            'websites': Website.objects.filter(user = user).order_by('pk'),
            'current_topic': topic,
            'topic_pk': topic_pk,
            'last_upd': user.last_upd,
            'website_form': WebsiteForm(),
            'topic_form': TopicForm(),
        }
        return render(request, 'feed_important.html', context)
    else:
        return redirect("main_dashboard")

@login_required
def news_website(request, website_pk):
    user = request.user
    website = Website.objects.get(pk = website_pk)
    if website.user == user:
        #set all displayed to false
        NewsPiece.objects.filter(user = user).update(displayed = False)

        unread_news = NewsPiece.objects.filter(user = user, website = website_pk, unread = True)

        if len(unread_news) > 20:
            pieces_of_news = NewsPiece.objects.filter(user = user, website = website_pk).order_by('-unread', '-published')[:20]
            ids = NewsPiece.objects.filter(user = user, website = website_pk).order_by('-unread', '-published').values_list('id', flat = True)[:20]
            NewsPiece.objects.filter(id__in = ids).update(displayed = True)
        else:
            pieces_of_news = unread_news.order_by('-published')
            NewsPiece.objects.filter(user = user, website = website_pk, unread = True).update(displayed = True)

        context = {
            'object_list': pieces_of_news,
            'displayed_news': len(pieces_of_news),
            'topics': Topic.objects.filter(user = user).order_by('pk'),
            'websites': Website.objects.filter(user = user).order_by('pk'),
            'current_website': website,
            'last_upd': request.user.last_upd,
            'website_form': WebsiteForm(),
            'topic_form': TopicForm(),
        }
        return render(request, 'feed_website.html', context)
    else:
        return redirect("main_dashboard")

@login_required
def news_topic(request, topic_pk):
    user = request.user
    topic_object = Topic.objects.get(pk = topic_pk)
    if topic_object.user == user:   
        #set all displayed to false
        NewsPiece.objects.filter(user = user).update(displayed = False)
        #then set the news that will be displayed to True
        NewsPiece.objects.filter(user = user, topics_assigned = topic_object, unread = True).update(displayed = True)

        pieces_of_news = NewsPiece.objects.filter(user = user, topics_assigned = topic_object, unread = True).order_by('published')[::-1]
        
        context = {
            'object_list': pieces_of_news,
            'displayed_news': len(pieces_of_news),
            'undisplayed_news': len(NewsPiece.objects.filter(user = user, topics_assigned = topic_object, unread = False)),
            'topics': Topic.objects.filter(user = user).order_by('pk'),
            'websites': Website.objects.filter(user = user).order_by('pk'),
            'current_topic': topic_object,
            'last_upd': request.user.last_upd,
            'website_form': WebsiteForm(),
            'topic_form': TopicForm(),
        }
        return render(request, 'feed_topic.html', context)
    else:
        return redirect("main_dashboard")


@login_required
def mark_important(request):
    if request.method == "GET":
        piece_id = request.GET['piece_id']
        piece = NewsPiece.objects.get(pk = piece_id)
        piece.important = not(piece.important)
        piece.save()
        return HttpResponse(piece.important)
    else:
        return HttpResponse("Fail")

@login_required
def mark_read(request):
    if request.method == "GET":
        piece_id = request.GET['piece_id']
        piece = NewsPiece.objects.get(pk = piece_id)
        piece.unread = not(piece.unread)
        piece.save()

        topic_unread_values, website_unread_values = get_unread_values(request.user)
        data = [{"status": piece.unread,
                 "topic_unread_values": topic_unread_values,
                 "website_unread_values": website_unread_values}]
        return JsonResponse(data, safe = False)
    else:
        return HttpResponse("Fail")

@login_required
def mark_all_read(request):
    if request.method == "GET":
        user = request.user

        NewsPiece.objects.filter(user = user, displayed=True, important = False, unread = True).update(unread = False)

        topic_unread_values, website_unread_values = get_unread_values(user)
        data = [{"topic_unread_values": topic_unread_values,
                 "website_unread_values": website_unread_values}]
        return JsonResponse(data, safe = False)
    else:
        return HttpResponse("Fail")

@login_required
def topic_remove(request, pk):
    topic = Topic.objects.get(pk = pk)

    if request.GET['next'] == f'/feed/topic/{topic.pk}/' or request.GET['next'] == f'/feed/important/{topic.pk}/':
        next_page = '/feed/all'
    else:
        next_page = request.GET['next']
    
    topic.delete()
    return redirect(next_page)

@login_required
def website_remove(request, pk):
    website = Website.objects.get(pk = pk)
    return render(request, 'delete_website.html', {'website': website, 'next': request.GET['next']})

@login_required
def website_remove_confirm(request, pk):
    website = Website.objects.get(pk = pk)

    if request.GET['next'] == f'/feed/website/{website.pk}/':
        next_page = '/feed/all'
    else:
        next_page = request.GET['next']
    
    website.delete()
    return redirect(next_page)

@login_required
def edit_topic(request, pk):
    topic = Topic.objects.get(pk = pk)
    if request.is_ajax and request.method == "GET":
        form = TopicForm(instance=topic)
        context = {'topic_edit_form': form, 
                   'topic_name': topic.name.lower(), 
                   'topic': topic, 
                   'next': request.GET['next']}
        return render(request, 'edit_topic.html', context)

    elif request.method == "POST":
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            topic = form.save(False)
            topic.save()
            return HttpResponse(topic.name)
        else:
            return HttpResponse("Error invalid form")
    else:
        return HttpResponse("Error: request not POST not AJAX")

@login_required
def edit_website(request, pk):
    website = Website.objects.get(pk = pk)
    if request.is_ajax and request.method == "GET":
        form = WebsiteForm(instance=website)
        context = {'website_edit_form': form, 
                   'website': website,
                   'next': request.GET['next']}
        return render(request, 'edit_website.html', context)

    elif request.method == "POST":
        form = WebsiteForm(request.POST, instance=website)
        if form.is_valid():
            website = form.save(False)
            website.save()
            return HttpResponse(website.name)
        else:
            return HttpResponse("Error: invalid form")
    else:
        return HttpResponse("Error: request not POST not AJAX")

@login_required
def edit_newspiece_topic(request, pk):
    piece = NewsPiece.objects.get(pk = pk)
    if request.is_ajax and request.method == "GET":
        form = NewsPieceTopicForm(instance=piece, user=request.user)
        context = {'news_topic_form': form, 
                   'piece': piece}
        return render(request, 'edit_news_topic.html', context)

    elif request.method == "POST":
        form = NewsPieceTopicForm(request.POST, instance=piece, user=request.user)
        if form.is_valid():
            piece = form.save(False)
            piece.topics_assigned.clear()
            for t in request.POST.getlist('topics_assigned'):
                topic = Topic.objects.get(pk=t)
                piece.topics_assigned.add(topic)
            piece.save()
            # return redirect(request.POST['next'])
            topic_unread_values, website_unread_values = get_unread_values(request.user)
            data = [{"updated_content": render_to_string('news_card.html', {'displayed_news': 1, 'object_list': [piece]}),
                    "topic_unread_values": topic_unread_values,
                    "website_unread_values": website_unread_values}]
            return JsonResponse(data, safe = False)
        else:
            return HttpResponse("Error: invalid form")
    else:
        return HttpResponse("Error: request not POST not AJAX")
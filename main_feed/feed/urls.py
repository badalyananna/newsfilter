from django.urls import path
from feed import views

urlpatterns = [
    path("all/", views.main_dashboard, name="main_dashboard"),
    path("add/", views.handle_form, name = "add"),
    path("topic/<topic_pk>/", views.news_topic, name = 'news_topic'),
    path("website/<website_pk>/", views.news_website, name = 'news_website'),
    path("markimportant/", views.mark_important, name = 'mark_important'),
    path("read/", views.mark_read, name = 'mark_read'),
    path("markallread/", views.mark_all_read, name = 'mark_all_read'),
    path("important/<topic_pk>/", views.news_important, name = 'news_important'),
    path("update/", views.update, name = 'update'),
    path("loadold/", views.load_old, name = 'load_old'),
    path("remove/topic/<pk>", views.topic_remove, name = 'topic_remove'),
    path("remove-website/<pk>", views.website_remove, name = 'website_remove'),
    path("remove-website-confirm/<pk>", views.website_remove_confirm, name = 'website_remove_confirm'),
    path("edit-topic/<pk>", views.edit_topic, name = 'edit_topic'),
    path("edit-website/<pk>", views.edit_website, name = 'edit_website'),
    path("edit-newspiece/<pk>", views.edit_newspiece_topic, name = 'edit_newspiece'),
]
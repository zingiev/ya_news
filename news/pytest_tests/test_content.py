import pytest
from django.conf import settings  # type: ignore

from news.forms import CommentForm


pytestmark = pytest.mark.django_db
CLIENT = pytest.lazy_fixture('client')  # type: ignore
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')  # type: ignore


def test_news_count(client, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(client, news_detail_url):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (AUTHOR_CLIENT, True),
        (CLIENT, False),
    )
)
def test_form_in_context(
    parametrized_client, form_in_context, news_detail_url
):
    response = parametrized_client.get(news_detail_url)
    assert ('form' in response.context) is form_in_context
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)

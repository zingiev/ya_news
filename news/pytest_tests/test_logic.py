import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')  # type: ignore
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')  # type: ignore
FORM_DATA = {'text': 'Новый коммент'}


def test_anonymous_user_cant_create_comment(client, news_detail_url):
    comments_count = Comment.objects.count()
    client.post(news_detail_url, data=FORM_DATA)
    assert Comment.objects.count() == comments_count


def test_user_can_create_comment(author_client, author, news, news_detail_url):
    comments_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=FORM_DATA)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_user_bad_words(author_client, news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    comments_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=bad_words_data)
    assert Comment.objects.count() == comments_count
    assertFormError(response, 'form', 'text', WARNING)


# Объеденил два функции удалении коммеентарии
@pytest.mark.parametrize(
    'parametrized_client, delete_comment',
    (
        (AUTHOR_CLIENT, True),
        (NOT_AUTHOR_CLIENT, False),
    )
)
def test_delete_comment(
    parametrized_client, delete_comment, delete_comment_url
):
    comments_count = Comment.objects.count()
    parametrized_client.delete(delete_comment_url)
    difference = comments_count - Comment.objects.count()
    assert (difference == 1) is delete_comment


# Объеденил два функции редактирования коммеентарии
@pytest.mark.parametrize(
    'parametrized_client, comment_in_count',
    (
        (AUTHOR_CLIENT, True),  # type: ignore
        (NOT_AUTHOR_CLIENT, False),
    )
)
def test_edit_comment(
    parametrized_client, comment, comment_in_count, edit_comment_url
):
    parametrized_client.post(edit_comment_url, data=FORM_DATA)
    comment_db = Comment.objects.get(pk=comment.id)
    assert (comment_db.text in FORM_DATA['text']) is comment_in_count
    assert comment.news == comment_db.news
    assert comment.author == comment_db.author

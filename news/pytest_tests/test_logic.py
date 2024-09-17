import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_user_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


# def test_author_can_delete_comment(author_client, news, comment):
#     news_url = reverse('news:detail', args=(news.id,))
#     url_to_comments = news_url + '#comments'
#     delete_url = reverse('news:delete', args=(comment.id,))
#     response = author_client.delete(delete_url)
#     assertRedirects(response, url_to_comments)
#     assert Comment.objects.count() == 0


# def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
#     delete_url = reverse('news:delete', args=(comment.id,))
#     response = not_author_client.delete(delete_url)
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     assert Comment.objects.count() == 1


# Объеденил два функции удалении коммеентарии
@pytest.mark.parametrize(
    'parametrized_client, comment_count',
    (
        (pytest.lazy_fixture('author_client'), 0),
        (pytest.lazy_fixture('not_author_client'), 1),
    )
)
def test_delete_comment(parametrized_client, comment_count, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    parametrized_client.delete(delete_url)
    assert Comment.objects.count() == comment_count


# def test_author_can_edit_comment(author_client, news, comment, form_data):
#     news_url = reverse('news:detail', args=(news.id,))
#     url_to_comments = news_url + '#comments'
#     edit_url = reverse('news:edit', args=(comment.id,))
#     response = author_client.post(edit_url, data=form_data)
#     assertRedirects(response, url_to_comments)
#     comment.refresh_from_db()
#     assert comment.text == form_data['text']


# def test_user_cant_edit_comment_of_another_user(
#     not_author_client, comment, form_data
# ):
#     edit_url = reverse('news:edit', args=(comment.id,))
#     response = not_author_client.post(edit_url, data=form_data)
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     comment.refresh_from_db()
#     assert comment.text != form_data['text']


# Объеденил два функции редактирования коммеентарии
@pytest.mark.parametrize(
    'parametrized_client, comment_in_count',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
def test_edit_comment(
    parametrized_client, comment, comment_in_count, form_data
):
    edit_url = reverse('news:edit', args=(comment.id,))
    parametrized_client.post(edit_url, data=form_data)
    comment.refresh_from_db()
    assert (comment.text in form_data['text']) is comment_in_count

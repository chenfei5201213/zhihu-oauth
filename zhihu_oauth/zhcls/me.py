# coding=utf-8

from __future__ import unicode_literals

from .people import People
from .urls import (
    ANSWER_VOTERS_URL,
    ARTICLE_VOTE_URL,
    SELF_DETAIL_URL,
)
from ..exception import MyJSONDecodeError, UnexpectedResponseException

__all__ = ['Me']


class Me(People):
    def __init__(self, pid, cache, session):
        """
        ..  role:: red
        ..  raw:: html

            <style> .red {color:red} </style>

        是 :class：`People` 的子类，表示当前登录的用户。
        设想中准备将用户操作（点赞，评论，收藏，私信等）放在这个类
        里实现，:red:`但是现在还没写！`

        ..  inheritance-diagram:: Me

        ..  seealso:: :class:`People`

        """
        super(Me, self).__init__(pid, cache, session)

    def _build_url(self):
        return SELF_DETAIL_URL

        # TODO: 好多好多用户操作，比如点赞，评论，私信，之类的……

    def vote(self, what, op='up'):
        """
        投票操作。也就是赞同，反对，或者清除（取消赞同和反对）。

        操作对象可以是答案和文章。

        :param what: 要点赞的对象，可以是 :any:`Answer` 或 :any:`Article` 对象。
        :param str op: 对于答案可取值 'up', 'down', 'clear'，
          分别表示赞同、反对和清除。
          对于文章，只能取 'up' 和 'clear'。
        :return: 表示结果的二元组，第一项表示是否成功，第二项表示原因。
        :rtype: (bool, str)
        :raise: :any:`UnexpectedResponseException`
          当服务器回复和预期不符，不知道是否成功时。
        """
        from .answer import Answer
        from .article import Article
        if isinstance(what, Answer):
            if op not in {'up', 'down', 'cancel'}:
                raise ValueError(
                    'Operate must be up, down or clear for Answer.')
            return self._vote(ANSWER_VOTERS_URL, what, op)
        if isinstance(what, Article):
            if op not in {'up', 'cancel'}:
                raise ValueError('Operate must be up or clear for Article')
            return self._vote(ARTICLE_VOTE_URL, what, op)
        else:
            raise TypeError(
                'Unable to voteup a {0}.'.format(what.__class__.__name__))

    def _vote(self, url, what, op):
        data = {
            'voteup_count': 0,
            'voting': {'up': 1, 'down': -1, 'clear': 0}[op],
        }
        url = url.format(what.id)
        res = self._session.post(url, data=data)
        try:
            json_dict = res.json()
            if 'error' not in json_dict:
                return True, ''
            else:
                return False, json_dict['error']['message']
        except (KeyError, MyJSONDecodeError):
            raise UnexpectedResponseException(
                url, res, 'a json contains voting result or error message')

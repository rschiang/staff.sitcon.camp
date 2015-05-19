import re
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree, AtomicString

MENTION_RE = u'(@[0-9A-Za-z\u3400-\u9fff\uf900-\ufaff\u3040-\u30ff_\\-]+)'

class MentionPattern(Pattern):
    def __init__(self):
        super(MentionPattern, self).__init__(MENTION_RE)

    def handleMatch(self, m):
        token = m.group(2)[1:]
        user = User.objects.filter(Q(username__istartswith=token) | Q(profile__display_name__iexact=token)).first()
        if user:
            link = reverse('users:profile', args=(user.username,))
        else:
            group = Group.objects.filter(name__istartswith=token).first()
            if group:
                link = '{}?g={}'.format(reverse('users:list'), group.id)
            else:
                return m.group(2)  # Plain-text output when not matching

        el = etree.Element('a')
        el.set('class', 'user-mention' if user else 'group-mention')
        el.set('href', settings.SITE_URL + link)
        el.text = AtomicString(m.group(2))
        return el

class MentionExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('mention', MentionPattern(), '<automail')

def makeExtension(**kwargs):
    return MentionExtension(**kwargs)

def filter_mentions(content):
	mention_tokens = set(re.findall(u'(?<=@)[0-9A-Za-z\u3400-\u9fff\uf900-\ufaff\u3040-\u30ff_\\-]+', content))
	mentions, extra_receivers = set(), set()
	for mention in mention_tokens:
		mentionee = User.objects.filter(Q(username__istartswith=mention) | Q(profile__display_name__iexact=mention)).first()
		if mentionee:
			mentions.add(mentionee)
		else:
			mention_group = Group.objects.filter(name__istartswith=mention).first()
			if mention_group:
				mentions.update(User.objects.filter(groups=mention_group))
	if settings.BROADCAST_MAGIC_TOKEN in mention_tokens:
		extra_receivers.add(settings.BROADCAST_EMAIL)
	return mentions, extra_receivers

# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.utils import t
from plone.memoize.instance import memoize
from plone.memoize.view import memoize_contextless
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class SetupView(BrowserView):
    """Ordered overview of all Setup Items
    """
    template = ViewPageTemplateFile("templates/setupview.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.set("disable_border", 1)
        return self.template()

    @property
    @memoize
    def bootstrap(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="bootstrapview")

    @property
    def portal(self):
        """Returns the Portal Object
        """
        return api.get_portal()

    @property
    def setup(self):
        """Returns the Senaite Setup Object
        """
        return api.get_setup()

    @memoize_contextless
    def get_icon_for(self, brain, **kw):
        """Returns the icon URL for the given catalog brain
        """
        return self.bootstrap.get_icon_for(brain, **kw)

    def setupitems(self):
        """Lookup available setup items

        :returns: catalog brains
        """
        query = {
            "path": {
                "query": api.get_path(self.setup),
                "depth": 1,
            },
        }
        items = api.search(query, "portal_catalog")
        # filter out items
        items = filter(lambda item: not item.exclude_from_nav, items)

        # sort by (translated) title
        def cmp_by_translated_title(brain1, brain2):
            title1 = t(api.get_title(brain1))
            title2 = t(api.get_title(brain2))
            # XXX: Python 3 compatibility
            return cmp(title1, title2)

        return sorted(items, cmp=cmp_by_translated_title)

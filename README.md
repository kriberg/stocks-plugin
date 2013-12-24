stocks-plugin
=============

A plugin for ECM that keeps track of stocks at a given station of a fitting or
for certain item types.

Installation
------------

Warning: I'm lazy and these instructions requires some basic python/Django
knowledge.

    1. Go to your ECM instance directory
    2. ``mkdir ext_plugins``
    3. ``cd ext_plugins``
    4. ``touch __init__.py``
    5. ``git clone git://github.com/kriberg/stocks-plugin stocks``
    6. Edit settings.py in the instance directory and add the following:
        a. Under ``INSTALLED_APPS`` append ``'django.contrib.humanize',``
        b. Under ``ECM_PLUGIN_APPS`` append ``'ext_plugins.stocks',``
    7. Run ecm-admin with syncdb to create the tables required for stocks
    8. Restart instance


Support
-------

I hang out on #ecm with the rest of the people. Just ask.

Contribution
------------

If you like it, hey, I'm open for donations. Just send any given amount of ISK
to Vittoros and I'll send double, no wait, tripple the amount back to you!

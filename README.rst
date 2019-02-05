Aesel Animation Client
======================

Aesel Animation Client is a high-level client for collaborative animation,
built on top of PyAesel, a lower-level python client mirroring the HTTP API of
the Aesel server.

This client is intended for use within animation software, and includes hooks
to inject API wrappers for those animation softwares to remain agnostic in
terms of where we run.

Currently, the only supported project is BlenderSync.

Aesel
-----

The Animation Client utilizes `Aesel <https://aesel.readthedocs.io/en/latest/>`__ as
the back-end server which drives all functionality.  Therefore, you should
either have `Aesel installed <https://aesel.readthedocs.io/en/latest/pages/install.html>`__,
or have access to an existing Aesel Cloud in order to use BlenderSync.

Get Assistance
--------------

Stuck and need help?  Have general questions about the application?  We encourage you to publish your question
on `Stack Overflow <https://stackoverflow.com>`__.  We regularly monitor for the tag 'aesel' in questions.

We encourage the use of Stack Overflow for a few reasons:

* Once the question is answered, it is searchable and viewable by everyone else.
* The forum format offers an easy method to get a larger community involved with a tougher question.

If you believe that you have found a bug in BlenderSync, or have an enhancement request, we encourage you to raise an issue on our `github page <https://github.com/AO-StreetArt/BlenderSync>`__.

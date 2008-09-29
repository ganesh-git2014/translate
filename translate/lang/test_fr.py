#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import factory

def test_punctranslate():
    """Tests that we can translate punctuation."""
    language = factory.getlanguage('fr')
    assert language.punctranslate(u"abc efg") == u"abc efg"
    assert language.punctranslate(u"abc efg.") == u"abc efg."
    assert language.punctranslate(u"abc efg!") == u"abc efg !"
    assert language.punctranslate(u"abc efg? hij!") == u"abc efg ? hij !"
    assert language.punctranslate(u"Delete file: %s?") == u"Delete file : %s ?"
    assert language.punctranslate(u'"root" is powerful') == u"« root » is powerful"
    assert language.punctranslate(u"'root' is powerful") == u"« root » is powerful"
    assert language.punctranslate(u"`root' is powerful") == u"« root » is powerful"
    assert language.punctranslate(u'The user "root"') == u"The user « root »"
    assert language.punctranslate(u"The user 'root'") == u"The user « root »"
    assert language.punctranslate(u"The user `root'") == u"The user « root »"
    assert language.punctranslate(u'The user "root"?') == u"The user « root » ?"
    assert language.punctranslate(u"The user 'root'?") == u"The user « root » ?"
    assert language.punctranslate(u"The user `root'?") == u"The user « root » ?"
    assert language.punctranslate(u'Watch the " mark') == u'Watch the " mark'
    assert language.punctranslate(u"Watch the ' mark") == u"Watch the ' mark"
    assert language.punctranslate(u"Watch the ` mark") == u"Watch the ` mark"
    assert language.punctranslate(u'The <a href="info">user</a> "root"?') == u'The <a href="info">user</a> « root » ?'
    assert language.punctranslate(u"The <a href='info'>user</a> 'root'?") == u"The <a href='info'>user</a> « root » ?"
    #Broken because we test for equal number of ` and ' in the string
    #assert language.punctranslate(u"The <a href='info'>user</a> `root'?") == u"The <a href='info'>user</a> « root » ?"
    assert language.punctranslate(u"The <a href='http://koeie'>user</a>") == u"The <a href='http://koeie'>user</a>"

def test_sentences():
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage('fr')
    sentences = language.sentences(u"Normal case. Nothing interesting.")
    assert sentences == [u"Normal case.", u"Nothing interesting."]
    sentences = language.sentences(u"Is that the case ? Sounds interesting !")
    assert sentences == [u"Is that the case ?", u"Sounds interesting !"]

# -*- coding: utf-8 -*-

import io

import six

import pytest

from translate.storage import mozilla_lang, test_base


class TestMozLangUnit(test_base.TestTranslationUnit):
    UnitClass = mozilla_lang.LangUnit

    def test_translate_but_same(self):
        """Mozilla allows {ok} to indicate a line that is the
        same in source and target on purpose"""
        unit = self.UnitClass("Open")
        unit.target = "Open"
        assert unit.target == "Open"
        assert str(unit).endswith(" {ok}")

    def test_untranslated(self):
        """The target is always written to files and is never blank. If it is
        truly untranslated then it won't end with '{ok}."""
        unit = self.UnitClass("Open")
        assert unit.target is None
        assert str(unit).find("Open") == 1
        assert str(unit).find("Open", 2) == 6
        assert not str(unit).endswith(" {ok}")

        unit = self.UnitClass("Closed")
        unit.target = ""
        assert unit.target == ""
        assert str(unit).find("Closed") == 1
        assert str(unit).find("Closed", 2) == 8
        assert not str(unit).endswith(" {ok}")

    def test_comments(self):
        """Comments start with #, tags start with ## TAG:."""
        unit = self.UnitClass("One")
        unit.addnote("Hello")
        assert str(unit).find("Hello") == 2
        assert str(unit).find("# Hello") == 0
        unit.addnote("# TAG: goodbye")
        assert (
            "# TAG: goodbye"
            in unit.getnotes(origin="developer").split("\n"))


class TestMozLangFile(test_base.TestTranslationStore):
    StoreClass = mozilla_lang.LangStore

    def test_nonascii(self):
        # FIXME investigate why this doesn't pass or why we even do this
        # text with UTF-8 encoded strings
        pass

    def test_format_layout(self):
        """General test of layout of the format"""
        lang = ("# Comment\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        store.mark_active = False
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == "Target"
        assert "Comment" in unit.getnotes()
        assert bytes(store).decode('utf-8') == lang

    def test_active_flag(self):
        """Test the ## active ## flag"""
        lang = ("## active ##\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        assert store.is_active
        assert bytes(store).decode('utf-8') == lang

    def test_multiline_comments(self):
        """Ensure we can handle and preserve miltiline comments"""
        lang = ("## active ##\n"
                "# First comment\n"
                "# Second comment\n"
                "# Third comment\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        assert bytes(store).decode('utf-8') == lang

    def test_template(self):
        """A template should have source == target, though it could be blank"""
        lang = (";Source\n"
                "Source\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == ""
        assert bytes(store).decode('utf-8') == lang
        lang2 = (";Source\n"
                 "\n\n"
                 ";Source2\n"
                 "\n\n")
        store2 = self.StoreClass.parsestring(lang2)
        assert store2.units[0].source == "Source"
        assert store2.units[0].target == ""
        assert store2.units[1].source == "Source2"
        assert store2.units[1].target == ""

    @pytest.mark.parametrize(
        "ok, target, istranslated", [
            ("", "", False),  # Untranslated, no {ok}
            (" ", "Source ", True),  # Excess whitespace, translated
            (" {ok}", "Source", True),  # Valid {ok}
            (" {ok} ", "Source", True),  # {ok} trailing WS
            ("{ok}", "Source", True),  # {ok} no WS
        ])
    def test_ok_translations(self, ok, target, istranslated):
        """Various renderings of {ok} to ensure that we parse it correctly"""
        lang = (";Source\n"
                "Source%s\n")
        store = self.StoreClass.parsestring(lang % ok)
        unit = store.units[0]
        assert unit.source == "Source"
        assert unit.target == target
        assert unit.istranslated() == istranslated

    def test_headers(self):
        """Ensure we can handle and preserve file headers"""
        lang = ("## active ##\n"
                "## some_tag ##\n"
                "## another_tag ##\n"
                "## NOTE: foo\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        assert (
            store.getlangheaders()
            == [u'## some_tag ##',
                u'## another_tag ##',
                u'## NOTE: foo'])
        out = io.BytesIO()
        store.serialize(out)
        out.seek(0)
        assert (
            out.read()
            == six.text_type(
                "## active ##\n"
                "## some_tag ##\n"
                "## another_tag ##\n"
                "## NOTE: foo\n"
                "\n\n"
                ";Source\n"
                "Target\n"
                "\n\n").encode('utf-8'))

    def test_not_headers(self):
        """Ensure we dont treat a tag immediately after headers as header"""
        lang = ("## active ##\n"
                "## some_tag ##\n"
                "## another_tag ##\n"
                "## NOTE: foo\n"
                "## TAG: fooled_you ##\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        assert "## TAG: fooled_you ##" not in store.getlangheaders()

    def test_tag_comments(self):
        """Ensure we can handle comments and distinguish from headers"""
        lang = ("## active ##\n"
                "# First comment\n"
                "## TAG: important_tag\n"
                "# Second comment\n"
                "# Third comment\n"
                "## TAG: another_important_tag\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        assert not store.getlangheaders()
        assert bytes(store).decode('utf-8') == lang
        assert (
            "# TAG: important_tag"
            in store.units[0].getnotes(origin="developer").split("\n"))
        lang = ("## active ##\n"
                "# First comment\n"
                "## TAG: important_tag\n"
                "# Second comment\n"
                "# Third comment\n"
                "## TAG: another_important_tag\n"
                "# Another comment\n"
                ";Source\n"
                "Target\n"
                "\n\n")
        store = self.StoreClass.parsestring(lang)
        assert not store.getlangheaders()
        assert (
            "First comment"
            in store.units[0].getnotes(origin="developer").split("\n"))
        assert (
            "Second comment"
            in store.units[0].getnotes(origin="developer").split("\n"))
        assert (
            "Another comment"
            in store.units[0].getnotes(origin="developer").split("\n"))
        assert (
            "# TAG: another_important_tag"
            in store.units[0].getnotes(origin="developer").split("\n"))

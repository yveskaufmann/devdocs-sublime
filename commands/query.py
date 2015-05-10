import sublime
import sublime_plugin
import threading
import webbrowser
import re

from ..SuggestionProvider import Index

class DevdocsQueryCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        ListDevDocSuggestions(self.window, language=None).start()

class ListDevDocSuggestions(threading.Thread):
    """
    A Thread which prevents that the ui from freezing
    while the index for the suggestions is fetching.
    """

    def __init__(self, window, language):
        self.window = window
        self.language = language
        threading.Thread.__init__(self)

    def determine_current_language(self):
        if not self.language:
            view = self.window.active_view()
            syntax = view.settings().get('syntax')
            m = re.search('(.*/)*([^\.]+?)\.tmLanguage$', syntax)
            if m:
                self.language = m.groups()[1].lower()

        return self.language

    def run(self):
        language = self.determine_current_language()
        self.index = Index.get(language)
        self.suggestion_list = [[entry['name'], entry['type']] for entry in self.index['entries']]
        self.show_suggestions()

    def on_select(self, suggestion_index):
        if suggestion_index >= 0:
            entry = self.index['entries'][suggestion_index]
            webbrowser.open_new_tab(entry['path'])

    def show_suggestions(self):
        if not self.suggestion_list:
            return
        self.window.show_quick_panel(self.suggestion_list, self.on_select)

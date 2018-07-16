#!/usr/bin/python3
"""
Author: James Lee
Email: jamesl33info@gmail.com
Supported Python version: 3.5.2+
"""


import os
import re

from guessit import guessit
from tvdb_api import tvdb_seasonnotfound


class Episode():
    """Allow the manipulation of a tv show's episode file."""
    def __init__(self, full_path):
        file_info = guessit(os.path.basename(full_path))

        for requirement in ['title', 'season', 'episode']:
            if requirement not in file_info:
                raise ValueError('File name doesn\'t contain enough information')

        self.full_path = full_path

        try:
            self.series_name = '{0} {1}'.format(file_info['title'], file_info['release_group'])
        except KeyError:
            self.series_name = file_info['title']

        self.season_number = file_info['season']
        self.episode_number = file_info['episode']

    @property
    def file_name(self):
        return os.path.basename(self.full_path)

    def get_new_file_name(self, show):
        """Generate a new file name for the tv show episode using TVDB.

        Arguments:
            show (tvdb_api.Show): TVDB show representing the current episode.

        Returns (str): New file name for the current episode.
        """
        def _clean_title(title, multi_part=False):
            expressions = [r'\(a.k.a. .*\)']

            if multi_part:
                expressions += [r'\(\d\)', r'-pt\d', r'pt\d', r'-prt\d', r'prt\d', r'-part\d', r'part\d']

            for regex in expressions:
                title = re.sub(re.compile(regex), '', title)

            title = re.sub('/', '-', title)

            return title.rstrip('')

        if isinstance(self.episode_number, list):
            try:
                episode_title = show[self.season_number][self.episode_number[0]]['episodeName']
            except tvdb_seasonnotfound:
                for index, season in enumerate(sorted(show)):
                    if index == self.season_number:
                        episode_title = show[season][self.episode_number]['episodeName']

            new_title = '{0} - '.format(show['seriesname'])

            for episode in self.episode_number:
                new_title += 'S{0}E{1} - '.format(str(self.season_number).zfill(2),
                                                  str(episode).zfill(2))

            new_title += '{0}{1}'.format(_clean_title(episode_title, True),
                                         os.path.splitext(self.full_path)[-1])

            return new_title

        try:
            episode_title = show[self.season_number][self.episode_number]['episodeName']
        except tvdb_seasonnotfound:
            for index, season in enumerate(sorted(show)):
                if index == self.season_number:
                    episode_title = show[season][self.episode_number]['episodeName']

        return '{0} - S{1}E{2} - {3}{4}'.format(show['seriesname'],
                                                str(self.season_number).zfill(2),
                                                str(self.episode_number).zfill(2),
                                                _clean_title(episode_title),
                                                os.path.splitext(self.full_path)[-1])

    def get_sortable_info(self):
        try:
            return (self.series_name, self.season_number, self.episode_number[0])
        except TypeError:
            return (self.series_name, self.season_number, self.episode_number)

    def __str__(self):
        return self.file_name

#!/usr/bin/env python3
"""
This file is part of pytranscoder.

Copyright (C) 2019, James Lee <jamesl33info@gmail.com>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

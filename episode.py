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
    """Allow the manipulation of a tv show's episode file"""
    def __init__(self, full_path):
        file_info = guessit(os.path.basename(full_path))

        for requirement in ['title', 'season', 'episode']:
            if requirement not in file_info:
                raise ValueError('File name doesn\'t contain enough information')

        self.full_path = full_path
        self.series_name = file_info['title']
        self.season_number = file_info['season']
        self.episode_number = file_info['episode']

    def get_file_name(self):
        return os.path.basename(self.full_path)

    def get_sortable_info(self):
        return (self.series_name, self.season_number, self.episode_number)

    def get_new_file_name(self, show):
        """Generate a new file name for the tv show episode using TVDB.

        Args:
            show (tvdb_api.Show): TVDB show representing the current episode.

        Returns (str): New file name for the current episode.
        """
        try:
            episode_title = show[self.season_number][self.episode_number]['episodeName']
        except tvdb_seasonnotfound:
            for index, season in enumerate(sorted(show)):
                if index == self.season_number:
                    self.season_number = season
                    episode_title = show[season][self.episode_number]['episodeName']

        return '{0} - S{1}E{2} - {3}{4}'.format(show['seriesname'],
                                                str(self.season_number).zfill(2),
                                                str(self.episode_number).zfill(2),
                                                re.sub('/', '-', episode_title),
                                                os.path.splitext(self.full_path)[-1])

    def __str__(self):
        return self.get_file_name()

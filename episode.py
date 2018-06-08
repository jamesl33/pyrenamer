#!/usr/bin/python3
"""
Author: James Lee
Email: jamesl33info@gmail.com
Supported Python version: 3.5.2+
"""


import os

from guessit import guessit


class Episode():
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
        episode_title = show[self.season_number][self.episode_number]['episodeName']
        return '{0} - S{1}E{2} - {3}{4}'.format(show['seriesname'],
                                                str(self.season_number).zfill(2),
                                                str(self.episode_number).zfill(2),
                                                episode_title,
                                                os.path.splitext(self.full_path)[-1])

    def __str__(self):
        return self.get_file_name()

#!/usr/bin/python3
"""
Author: James Lee
Email: jamesl33info@gmail.com
Supported Python version: 3.5.2+
"""


import os

from guessit import guessit


class Movie():
    """Allow the manipulation of data representing a movie."""
    def __init__(self, full_path):
        file_info = guessit(os.path.basename(full_path))

        if 'title' not in file_info:
            raise ValueError('File name doesn\'t contain enough information \'{0}\''.format(
                os.path.basename(full_path)))

        self.full_path = full_path
        self.title = file_info['title']

        try:
            self.year = file_info['year']
        except KeyError:
            self.year = None

    @property
    def file_name(self):
        return os.path.basename(self.full_path)

    def get_sortable_info(self):
        if self.year is not None:
            return (self.title, self.title)
        return self.title

    def get_new_file_name(self, movie):
        """Use imdb to create a new file name for the movie file.

        Arguments:
            movie (imdb.Movie.Movie): Information about the current movie fetched using imdbpy.

        Returns:
            (str): Generated file name.
        """
        try:
            return '{0} ({1}){2}'.format(movie['title'],
                                         movie['year'],
                                         os.path.splitext(self.full_path)[-1])
        except KeyError:
            return '{0}{1}'.format(movie['title'],
                                   os.path.splitext(self.full_path)[-1])

    def __str__(self):
        return self.get_file_name

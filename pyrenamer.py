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
from imdb import IMDb
from tvdb_api import Tvdb
from tvdb_api import tvdb_shownotfound

from episode import Episode
from movie import Movie


class Renamer():
    """Automatically rename tv shows and movies using the TVDB and IMDB.
    Arguments:
        config (dict): Dictionary containing information to change the behaviour
        of the program.
    """
    def __init__(self, config):
        self.config = config

    def rename(self, directory):
        """Rename all the valid files in the given directory.
        Arguments:
            directory (str): The path to a folder containing valid files.
        """
        movies, tv_shows = self._get_video_files(directory)

        for movie in movies:
            self._rename_file(movie.full_path,
                              movie.get_new_file_name(self._get_correct_movie(movie.full_path)))

        current_show = [None, None]
        for show in tv_shows:
            if current_show[0] != show.series_name:
                current_show[0] = show.series_name
                current_show[1] = self._get_correct_tv_show(os.path.basename(show.series_name))

            self._rename_file(show.full_path, show.get_new_file_name(current_show[1]))

    def _get_correct_movie(self, full_path):
        """Prompt the user to select the correct movie from the imdb search results.
        Arguments:
            full_path (str): The path to the movie file.

        Returns:
            (imdb.Movie.Movie): The movie that the user chose.
        """
        movie_info = guessit(full_path)
        imdb_movies = IMDb().search_movie(movie_info['title'])
        valid_imdb_movies = []

        for movie in imdb_movies:
            if re.search('movie', movie['kind']) and len(valid_imdb_movies) < 5:
                valid_imdb_movies.append(movie)

        print('\nIMDB Search Results for \'{0}\''.format(movie_info['title']))
        for index, movie in enumerate(valid_imdb_movies):
            try:
                print('{0}: {1} ({2})'.format(index + 1, movie['title'], movie['year']))
            except KeyError:
                print('{0}: {1}'.format(index + 1, movie['title']))

        if len(valid_imdb_movies) == 1:
            print('Automatically choosing only result')
            return valid_imdb_movies[0]

        return valid_imdb_movies[self._parse_input()]

    def _get_correct_tv_show(self, full_path):
        """
        Arguments:
            full_path (str): The path to the episode file.
        Returns:
            (tvdb_api.Show): The tv show that the user chose.
        """
        tv_show_info = guessit(full_path)

        try:
            tvdb_shows = Tvdb().search(tv_show_info['title'])
        except tvdb_shownotfound:
            print('Error: TV Show not found')
            exit(1)

        valid_tvdb_shows = []

        for show in tvdb_shows:
            if show['seriesName'] != '** 403: Series Not Permitted **':
                if len(valid_tvdb_shows) < 5:
                    valid_tvdb_shows.append(show)

        print('\nTVDB Search Results for \'{0}\''.format(tv_show_info['title']))
        for index, show in enumerate(valid_tvdb_shows):
            print('{0}: {1}'.format(index + 1, show['seriesName']))

        if len(valid_tvdb_shows) == 1:
            print('Automatically choosing only result')
            return Tvdb()[valid_tvdb_shows[0]['id']]

        return Tvdb()[valid_tvdb_shows[self._parse_input()]['id']]

    def _rename_file(self, full_path, new_file_name):
        """Rename a valid file and respect whether the user wanted it to be a dry run."""
        if os.path.basename(full_path) == new_file_name:
            return

        if not self.config['dry_run']:
            os.rename(full_path, os.path.join(os.path.dirname(full_path), new_file_name))
        print('{0} -> {1}'.format(os.path.basename(full_path), new_file_name))

    @classmethod
    def _get_video_files(cls, directory):
        """Get all the valid movie/tv show files from the search directory.

        Arguments:
            directory (str): The directory to search in.

        Returns:
            (tuple): Two lists one for movie files another tv show files.
        """
        movies = []
        tv_shows = []

        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                if os.path.splitext(filename)[-1] not in ['.avi', '.mp4', '.mkv', '.srt']:
                    continue

                if guessit(filename)['type'] == 'movie':
                    movies.append(Movie(os.path.join(dirpath, filename)))
                else:
                    tv_shows.append(Episode(os.path.join(dirpath, filename)))

        print('{0} TV Shows Found / {1} Movies Found.'.format(len(tv_shows), len(movies)))

        return (movies, sorted(tv_shows, key=lambda file_name: file_name.get_sortable_info()))

    @classmethod
    def _parse_input(cls):
        """Prompt the user a number. Keep trying until we get what we want.

        Returns:
            (int): The users choice.
        """
        while True:
            try:
                user_input = input('Enter choice ')
            except KeyboardInterrupt:
                print('\nAborted!')
                exit(0)

            if user_input == '':
                return 0

            try:
                return int(user_input) - 1
            except ValueError:
                pass


def main():
    """Main driver code containing the command line user interface."""
    parser = argparse.ArgumentParser(
        description='simple yet effective batch movie/tv show renamer'
    )

    parser.add_argument(
        'folder',
        action='store',
        help='folder containing media files',
        type=str
    )

    parser.add_argument(
        '-d',
        '--dry-run',
        action='store_true',
        help='run the program without making and changes'
    )

    arguments = parser.parse_args()

    config = {
        'dry_run': arguments.dry_run
    }

    renamer = Renamer(config)
    renamer.rename(arguments.folder)


if __name__ == '__main__':
    import argparse
    main()

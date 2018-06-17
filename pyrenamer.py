#!/usr/bin/python3
"""
Author: James Lee
Email: jamesl33info@gmail.com
Supported Python version: 3.5.2+
"""


import os

from guessit import guessit
from imdb import IMDb
from tvdb_api import Tvdb

from episode import Episode
from movie import Movie


class Renamer():
    def __init__(self, config):
        self.config = config

    def rename(self, directory):
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
        movie_info = guessit(full_path)
        imdb_movies = IMDb().search_movie(movie_info['title'])
        valid_imdb_movies = []

        for movie in imdb_movies:
            if movie['kind'] == 'movie' and len(valid_imdb_movies) < 5:
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
        tv_show_info = guessit(full_path)
        tvdb_shows = Tvdb().search(tv_show_info['title'])
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
        if os.path.basename(full_path) == new_file_name:
            return

        if not self.config['dry_run']:
            os.rename(full_path, os.path.join(os.path.dirname(full_path), new_file_name))
        print('{0} -> {1}'.format(os.path.basename(full_path), new_file_name))

    @classmethod
    def _get_video_files(cls, directory):
        movies = []
        tv_shows = []

        accepted_extensions = ['.avi', '.mp4', '.mkv']

        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                if os.path.splitext(filename)[-1] not in accepted_extensions:
                    continue

                if guessit(filename)['type'] == 'movie':
                    movies.append(Movie(os.path.join(dirpath, filename)))
                else:
                    tv_shows.append(Episode(os.path.join(dirpath, filename)))

        print('{0} TV Shows Found / {1} Movies Found.'.format(len(tv_shows), len(movies)))

        return (movies, sorted(tv_shows, key=lambda file_name: file_name.get_sortable_info()))

    @classmethod
    def _parse_input(cls):
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
    parser = argparse.ArgumentParser(
        description=''
    )

    parser.add_argument(
        'folder',
        action='store',
        help='',
        type=str
    )

    parser.add_argument(
        '-d',
        '--dry-run',
        action='store_true',
        help=''
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

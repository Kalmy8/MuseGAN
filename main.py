from mido import MidiFile
import pandas as pd
import glob
import re
import numpy as np

class Validation_config(object):
    """ Конфигуратор для валидатора, доработать при надобности """
    min_track_duration = 0
    min_required_instruments_from_top = 1


class MidiDF_collector(object):
    """
        Класс для сбора информации о MIDI - файлах в виде единого DF
    """
    @staticmethod
    def __parse_child_directories():
        """Парсит список всех midi файлов в дочерних директориях проекта"""
        files = []
        for file in glob.glob('**/*.mid', recursive=True):
            files.append(file)
        return files

    @staticmethod
    def __parse_instruments(midi_file):
        """Для миди-файла выводит список уникальных инструментов (в виде id)"""
        id_instruments = []
        midi_file = MidiFile(midi_file, clip=True)
        for msg in midi_file:
            if msg.type == 'program_change':
                id_instruments.append(re.findall(r'\d+', str(msg))[0])
        return list(set(id_instruments))

    @staticmethod
    def __parse_instruments_names(midi_file):
        """Для миди-файла выводит список уникальных инструментов (в виде id)"""
        names_instruments = []
        midi_file = MidiFile(midi_file, clip=True)
        for msg in midi_file:
            if msg.type == 'track_name':
                names_instruments.append(str(msg.name))
        return list(set(names_instruments))


    @staticmethod
    def return_midi_df():
        """Проходит по всем дочерним папкам, собирает информацию по каждому из треков """
        midi_df = pd.DataFrame({'midi_file' : [],
                                'instruments_amount' : [],
                                'instruments_ids' : [],
                                'instruments_names': [],
                                'duration (sec)': [] })

        for midi in MidiDF_collector.__parse_child_directories():
            some_md = MidiFile(midi, clip = True)
            instruments = MidiDF_collector.__parse_instruments(midi)
            instruments_names = MidiDF_collector.__parse_instruments_names(midi)

            new_row = pd.Series({'midi_file' : midi,
                                'instruments_amount' : len(instruments),
                                'instruments_ids' : instruments,
                                'instruments_names': instruments_names,
                                'duration (sec)' : some_md.length})

            midi_df = pd.concat([midi_df, new_row.to_frame().T], ignore_index=True)
        return midi_df



class MidiDF_Analyzer(object):
    """Класс для анализа и валидации MIDI - треков"""
    min_track_duration = None
    min_required_instruments_from_top = None
    midi_df = None

    def __init__(self, validator_config, midies_df):
        self.min_track_duration = validator_config.min_track_duration
        self.min_required_instruments_from_top = validator_config.min_required_instruments_from_top
        self.midies_df = midies_df


    def get_top_instruments(self):
        """Выводит id из топа самых популярных инструментов"""

        all_instrument_occurence = np.array(self.midies_df['instruments_ids'].sum())
        unique = np.unique(all_instrument_occurence)
        return unique[:self.min_required_instruments_from_top]

    def get_valid_midies(self):
        """Используя конфигуратор, фильтрует исходный midi датафрейм, оставляя только валидные файлы"""
        # Первичная фильтрация по количеству инструментов
        filtered_df = self.midi_df[self.midi_df["instruments_amount"] >= self.min_required_instruments_from_top]
        top_instruments = MidiDF_Analyzer.get_top_instruments(self)

        # Вторичная фильтрация по наличию инструментов из топа
        filtered_df['matches_amount'] = MidiDF_Analyzer.__intersect_instruments(filtered_df['instruments_ids'], top_instruments)
        filtered_df = filtered_df[filtered_df['matches_amount'] >= self.min_required_instruments_from_top]
        return filtered_df

    @staticmethod
    def __intersect_instruments(instrument_series, top_instruments):
        top_instruments = set(top_instruments)
        return pd.Series([len(set.intersection(x,top_instruments)) for x in instrument_series.apply(set)])

def main():
    try:
        midies_df = pd.read_pickle('midie_df')
        print("Midies_df from project directory")

    except:
        print("Midies_df not found in project directory")
        config = Validation_config()
        midies_df = MidiDF_collector.return_midi_df()
        midies_df.to_pickle('midies_df')

    print(midies_df[midies_df['instruments_ids'].apply(len) > 2])
    midi_file = MidiFile('autumn5[1].mid', clip=True)
    print(midi_file)

if __name__ == '__main__':
    main()


from mido import MidiFile
import pandas as pd
import glob
import re
from progress.bar import IncrementalBar


class Validation_config(object):
    """ Конфигуратор для валидатора, доработать при надобности """
    min_track_duration = 0
    min_required_instruments_from_top = 3


class MidiAnalyzer(object):
    """
        Класс проводит валидацию миди файлов, лежащих в дочерней категории.
    """
    min_track_duration = 0;
    min_required_instruments_from_top = 0;
    all_midi = [];

    def __init__(self, validator_config):
        self.min_track_duration = validator_config.min_track_duration
        self.min_required_instruments_from_top = validator_config.min_required_instruments_from_top
        self.all_midi = self.__parse_child_directories()

    def __parse_child_directories(self):
        files = []
        for file in glob.glob('**/*.mid', recursive=True):
            files.append(file)
        return files

    @staticmethod
    def __parse_instruments(midi_file):
        id_instruments = []
        midi_file = MidiFile(midi_file, clip=True)
        for msg in midi_file:
            if msg.type == 'program_change':
                id_instruments.append(re.findall(r'\d+', str(msg))[0])
        return list(set(id_instruments))

    def midi_info_collector(self):
        """Проходит по всем дочерним папкам, собирает информацию по каждому из треков """
        midi_df = pd.DataFrame({'midi_file' : [],
                                'instruments_amount' : [],
                                'instruments_ids' : []})


        bar = IncrementalBar('Countdown', max=len(self.all_midi))
        import time
        fs = time.time()
        for midi in self.all_midi:
            bar.next()
            instruments = self.__parse_instruments(midi)
            new_row = pd.Series({'midi_file' : midi,
                                'instruments_amount' : len(instruments),
                                'instruments_ids' : instruments})

            midi_df = pd.concat([midi_df, new_row.to_frame().T], ignore_index=True)

        bar.finish()
        return midi_df

def main():
    config = Validation_config()
    analyzer = MidiAnalyzer(config)
    midies_df = analyzer.midi_info_collector()
    print(midies_df)

if __name__ == '__main__':
    main()


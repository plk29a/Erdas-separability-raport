import os


class Error(Exception):
    def __init__(self, len1, len2):
        self.len1 = len1
        self.len2 = len2

    def __str__(self):
        return f'Tabela z opisem stosunkow {self.len1}, ma inna wielkosc niz tabela z stosunkami {self.len2}'


class Legend:
    """Tworzy i edytuje opis typow."""
    def read_legend(self):
        legend_records = []
        while True:
            line = self.file.readline()
            line = line.strip()
            if line:
                legend_records.append(line)
            else: break
        return legend_records

    def _clean_legend(self, legend_records):
        clean_legend_records = []
        for line in legend_records:
            line = line.split('   ')
            line[-1] = line[-1].rsplit('_', 1)[0]
            clean_legend_records.append(line)
        return clean_legend_records

    def _dict_legend(self, clean_legend_record):
        dict_legend = {}
        lenght = 0
        for no, type in clean_legend_record:
            dict_legend[type] = []
            lenght +=1
        for no, type in clean_legend_record:
            dict_legend[type].append(int(no))
        return dict_legend

    def create_legend(self):
        legend_records = self.read_legend()
        legend_records = self._clean_legend(legend_records)
        self.legend = self._dict_legend(legend_records)
        return self.legend


class SeparabilityListing:
    """Ogarnia zczytanie i przygotowanie tablic z Separability Listing"""
    def __init__(self, separability_listing_array):
        self.raw_array = separability_listing_array

    def create_sl_arrays(self):
        self.array_description = []
        self.array_values = []
        what = True
        for line in self.raw_array:
            line = line.replace(': ',':')
            line_list = line.split()
            length = len(line_list)
            if length == 10 and what:
                self.band = int(line_list.pop(0))
                line_list = line_list[2:]
                what = False
                length = len(line_list)

            if what and length == 7:
                line_list = line.split('  ')
                line_tuple = [tuple([int(val.split(':')[0]), int(val.split(':')[-1])]) for val in line_list]
                self.array_description += line_tuple
            elif not what and length == 7:
                values_list = [int(val) for val in line_list]
                self.array_values += values_list

        len1, len2 = len(self.array_description), len(self.array_values)
        if len1 == len2:
            self.arrays_lenght = len1
            return self.band, self.array_description, self.array_values
        else:
            raise Error(len1, len2)



class ListingFile(Legend, SeparabilityListing):
    """Zajmuje sie otwarciem o zaczytaniem pojedynczego pliku"""
    def __init__(self, file):
        self.file_path = file
        self.file_out = os.path.splitext(file)[0] + '_raport.csv'

        self.file = self.open_file()
        self.file_name = os.path.split(file)[-1]

    def skip_lines(self, how_much:int):
        for skip in range(how_much+1): self.file.readline()

    def open_file(self):
        return open(self.file_path, 'r')

    def __del__(self):
        self.file.close()

    def separability_listing_reader(self):
        """Wyodrenia z pliku czesc z SL i wysyla do odpoweidniej klasy - generator"""
        header_main = "   Bands         AVE    MIN    Class Pairs:\n"
        header_ok = "                              Separability Listing\n"
        header_end = "                           Best Minimum Separability\n"
        array_class_pair = []
        for line in self.file:
            if line == header_end:
                break
            elif array_class_pair and line == '\n':
                one_separability_listing = SeparabilityListing(array_class_pair)
                yield one_separability_listing.create_sl_arrays()
                del one_separability_listing
                array_class_pair = []

            elif line == '\n' or line == header_ok:
                continue
            elif line == header_main:
                array_class_pair = []
                continue
            elif line != '\n':
                line = line.strip()
                array_class_pair.append(line)

    def legend(self):
        self.skip_lines(11)
        self.legend = self.create_legend()

    def read_file_writeraport(self):
        """Wczytuje plik ogarnia kolejne kroki i zapisuje raport w odpowiednim formacie"""
        self.legend()
        outcome_file = open(self.file_out, 'w+')
        for one_band in self.separability_listing_reader():
            band, array_description, array_values = one_band
            array = zip(array_description, array_values)
            array = list(array)
            outcome_file.write((f'band: {band},' + ','.join(self.legend.keys())))
            for type1, valu1 in self.legend.items():
                outcome_file.write(f'\n{type1}')
                for type2, valu2 in self.legend.items():
                    array_copy = array.copy()
                    choosen = filter(lambda x: x[0][0] in valu1 and x[0][1] in valu2, array_copy)

                    values = [x[-1] for x in choosen]
                    suma = sum(values)
                    amount = len(values)

                    try:
                        average = suma / amount
                        outcome_file.write(',' + format(average, '.2f'))
                    except ZeroDivisionError:
                        outcome_file.write(',')

                    except Exception as e:
                        raise e

            outcome_file.write('\n\n')
        outcome_file.close()

def get_list_check(uri):
    path = uri
    file_list = []
    for r, d, f in os.walk(path):
        for file in f:
            fileName = os.path.join(r, file)
            file_list.append(fileName)
    return file_list

def input_data():
    file_list = []
    dir = input(r'Plik lub folder do przetworzenia: ')
    while dir:
        dir = dir.strip('"')
        if os.path.isdir(dir):
            dir_list = get_list_check(dir)
            if len(dir_list) > 0:
                file_list.extend(dir_list)
            else:
                print('folder nie zawiera plikow')

        elif os.path.isfile(dir):
            file_list.append(dir)

        dir = input(rf'Kolejny folder, lub plik [enter konczy wprowadzanie]: ')

    else:
        file_set = set(file_list)
        print('\n\tLista plikow do edycji:')
        for file in file_set: print('\t\t', file)
    return set(file_set)

if __name__ == '__main__':
    files = input_data()
    print('\n')
    for file in files:
        try:
            x = ListingFile(file)
            x.read_file_writeraport()
            print(f'{file} - Stworzono raport dla pliku')
            del x
        except Exception as e:
            print(f'!!!\t{file} - nie udalo sie stworzyc raportu')
    input("press ENTER to exit")

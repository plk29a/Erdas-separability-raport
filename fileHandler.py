import os, sys

class Error(Exception):
    def __init__(self, len1, len2):
        self.len1 = len1
        self.len2 = len2

    def __str__(self):
        return f'Tabela z opisem stosunków {self.len1}, ma inna wielkosc niz tabela z stosunkami {self.len2}'

class Legend:
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
    def __init__(self, file):
        self.file_path = file
        self.file = self.open_file()
        self.file_name = os.path.split(file)[-1]

    def skip_lines(self, how_much:int):
        for skip in range(how_much+1): self.file.readline()

    def open_file(self):
        return open(self.file_path, 'r')

    def __del__(self):
        self.file.close()

    def separability_listing_reader(self):
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

    def read_file(self):
        self.skip_lines(11)
        self.legend = self.create_legend()
        results_dict = {}
        outcome_file = open(file_out, 'w+')
        for one_band in self.separability_listing_reader():
            band, array_description, array_values = one_band
            array = zip(array_description, array_values)
            array = list(array)
            outcoms = []
            results_dict[band] = outcoms
            outcome_file.write((f'band: {band}\t' + '\t'.join(self.legend.keys())))
            for type1, valu1 in self.legend.items():
                outcome_file.write(f'\n{type1}\t')
                for type2, valu2 in self.legend.items():
                    array_copy = array.copy()
                    choosen = filter(lambda x: x[0][0] in valu1 and x[0][1] in valu2, array_copy)

                    values = [x[-1] for x in choosen]
                    suma = sum(values)
                    amount = len(values)

                    try:
                        average = suma / amount
                        print(f'{type1} - {type2}')
                        print(f'srednia: {average}')
                        outcome_file.write(format(average, '.2f').replace('.',',') + '\t')
                        outcoms.append([type1, type2, average])
                    except Exception as e:
                        outcome_file.write('\t')
                        pass
                # outcome_file.write('\n\n')
            outcome_file.write('\n\n')

        outcome_file.close()

        ...



if __name__ == '__main__':
    # file = input(r'wskaz plik: ')
    file = r'E:\Radek\Kasia_skrypt\dane\jm_red_2m_gran_s4'
    file_out = file + '_raport.csv'
    # file_out = r'E:\Radek\Kasia_skrypt\jm_red_2m_gran_s4_raport.csv'
    x = ListingFile(file)
    x.read_file()
    print('koniec')
import xml.etree.ElementTree as ET
import re
import os

class SDF_Parse:
    def __init__(self, sdf_file):
        self.file = sdf_file
        self.filename = os.path.basename(sdf_file)
        self.active_file = open(self.file, 'r')
        self.sdf_data = self.active_file.readlines()

        # Parse symbol data from .sdf
        self.symbol_data = self.parse_sdf(self.sdf_data)

    def parse_sdf(self, sdf_data):
        """ This function will parse the symbol table data from the sdf data

        :param sdf_data:
        :return: symbol_data
        """

        symbol_data = []
        for line in sdf_data:
            line = line.replace('\n', '')
            line = line[1:-1]
            data =  line.split('","')
            #data = data.remove('"')
            name, address, data_type, comment =  data
            perph_type = address[:address.find(' ')]
            perph_addr = address[re.search(r"\d", address).start():]
            if perph_addr.isdigit():
                perh_addr = int(perph_addr)
            else:
                perph_addr = float(perph_addr)
            symbol_data.append({
                'name': name.replace(" ",''),
                'perph_type': perph_type,
                'perph_addr': perph_addr,
                'data_type': data_type.replace(" ", ''),
                'comment': comment.replace(" ", '')
            })
        return symbol_data


if __name__ == "__main__":
    # Sample input from the previously decoded content
    s7g = SDF_Parse("../../S7_Data/B3Z11502.sdf")

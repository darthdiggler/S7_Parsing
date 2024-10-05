
import os
from deep_translator import GoogleTranslator


class AWL_Translate:
    """AWL Translate  will extract the text from named

    German to English language conversions were done through deep_translator python library

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Args:
        root_dir (str): Path to root directory containing all of the pdf documents to extract.

    Attributes:
        root_dir (str): Path to root directory containing all of the pdf documents to extract.
        pdf_list (list(tuple))): List of tuples information extracted from pdf files.
    """
    FC_TYPE = 'FUNCTION'  # Function PLC type
    FB_TYPE = 'FUNCTION_BLOCK'  # Function Block PLC type
    UNK_TYPE = 'Unknown'  # Unknown PLC type
    FILE_EXT = '.awl'
    BATCH_SIZE = 100

    def __init__(self, root_dir, file):
        # Check file exists
        self.file = root_dir + file + self.FILE_EXT
        if not os.path.isfile(self.file):
            print("Not a proper file name or path.")
            return
        self.root_dir = root_dir
        self.output_file = root_dir + file + "_EN" + self.FILE_EXT

        # Open files for reading and writing
        self.active_file =  open(self.file, "r")
        self.output_file = open(self.output_file, "w")
        file_data = self.active_file.readlines()
        self.extract_file_comments(file_data)

    def extract_file_comments(self, file_data):
        """Example function with types documented in the docstring.

        Args:
            file_data list(): File data to be translated.

        Returns:
            translate_data list(): data_for_translation, line_data, line, position
        """
        total_translated = 0
        comment_data = []
        translate_data = []
        translate_data_info = []
        # Iterate through comments and batch translate
        for line in range(len(file_data)):
            data = ''
            line_data = file_data[line]
            # Extract Comments and create metadata for replacing with translations
            position = line_data.find("//")
            if position > -1:
                data = line_data[position+2:]
                comment_data.append(data)
                total_translated += 1
            translate_data_info.append((line_data, line, position))

            # Batch translate data
            if len(comment_data) >= self.BATCH_SIZE:
                translate_data.extend(GoogleTranslator('de', 'en').translate_batch(comment_data))
                comment_data = []
                print("Translated 100 words batch")

        # Validate translated data size
        if not total_translated == len(translate_data):
            print("Mismatched translation size: Total->" + str(total_translated) +
                  " Translated->" + str(len(translate_data)))
            return None

        # Iterate through metadata to rebuild file
        for line in range(len(file_data)):
            data = file_data[line]
            if translate_data_info:
                data_info, line_info, position_info = translate_data_info.pop(0)
                if line_info == line and position_info > -1:
                    data = data[:position] + "//" + str(translate_data.pop(0)) + "\n"

            self.output_file.write(data)
        pass

    def extract_file_titles(self, file_data):
        """Example function with types documented in the docstring.

        Args:
            pdf_list (list(tuple)): The first parameter.

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        for line in file_data:
            # Extract TITLE
            position = line.find("TITLE =")
            if position == 0:
                data = line[position+7:]
                if not data == '\n':
                    en_data = GoogleTranslator(source='auto', target='en').translate(data)
                    en_data = en_data + '\n'
                    pass

if __name__ == "__main__":
    awl = AWL_Translate('C:/Users/Justin/Desktop/Mercedes Benz/VM Software/integra/Project/AWL/',
                        'B3Z22511')
    pass
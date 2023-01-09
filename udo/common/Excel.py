import pandas as pd
from udo import default_settings


# data: [(1,2,3), ('a','b','c'), (3,4,'汉字')]
# columns: ['aaa', 'bbb', 'ccc']
def writer_excel(data, columns, filename):
    excel_path = default_settings.EXCEL_DIR + filename
    file_path = pd.ExcelWriter(excel_path)
    df = pd.DataFrame(data, columns=columns)
    df.fillna('', inplace=True)
    df.to_excel(file_path, encoding='utf-8', index=False)
    file_path.save()
    return excel_path

import os
import random
import string

current_directory = os.getcwd()
# windows
path = current_directory + "\\files\\"
# linux or mac
# path = current_directory + "/files/"
print(f'path : {path}')

if os.path.exists(path):
    print('already exists')
else:
    print(f"mkdir : files")
    os.mkdir("files")

# 每個檔案的大小（以字節為單位）
file_size = 15 * 1024 * 1024

# 創建8個檔案
for i in range(1, 9):
    # 建立檔案名稱
    filename = path + f"file{i}.txt"
    print(filename)
    
    # 創建空檔案
    with open(filename, 'w') as f:
        # 寫入隨機英文字串直到檔案大小到達要求
        while f.tell() < file_size:
            random_str = ''.join(random.choices(string.ascii_letters, k=1024))
            f.write(random_str)
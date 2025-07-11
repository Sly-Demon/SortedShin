

with open(r'Minerals (and flora) list .txt', 'r') as fp:


    lines = fp.readlines()
    for row in lines:
        word1 = 'Minerals:'  # String to search for
        if row.find(word1  ) != -1:
            print('String exists in file')
            print('Line Number:', lines.index(row))
        word2 = 'FLORA'  # String to search for
        if row.find(word2) != -1:
            print('String exists in file')
            print('Line Number:', lines.index(row))
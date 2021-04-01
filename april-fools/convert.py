import json

with open('data.json') as f:
    d = json.load(f)

    for frame in d:
        for row in frame:
            for elem in row:
                with open('input.txt', 'a+') as i:
                    i.write(str(elem))
            with open('input.txt', 'a+') as i:
                i.write('\n')

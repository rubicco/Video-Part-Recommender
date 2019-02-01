import Algorithmia

# keyword extraction variables
client_keyword = Algorithmia.client(<API KEY>)
algo_keyword = client_keyword.algo('cindyxiaoxiaoli/KeywordExtraction/0.3.0')

def keyword_extract(input):
    if type(input) is str and len(input)!=0:
        a = algo_keyword.pipe(input)
        return a.result

def count_kword(text, x):
    count = 0
    if len(x.split(' '))!=1:
        count = text.count(x)
    else:
        words = clean_symbols(text).split(' ')
        for w in words:
            if w == x:
                count+=1
    return count

def clean_symbols(input):
    symbols = ['.', ',', '!', '?', '(', ')', ':', ';']
    for i in symbols:
        input = input.replace(i, '')
    return input

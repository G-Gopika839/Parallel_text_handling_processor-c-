def process_chunk(chunk):
    text = "".join(chunk)      # convert list of lines to single string
    words = text.split()       # split into words
    word_count = len(words)
    return word_count
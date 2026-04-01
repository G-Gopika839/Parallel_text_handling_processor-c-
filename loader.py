def load_file(path):

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    reviews = [line.strip() for line in lines if line.strip()]

    return reviews


#def create_chunks(lines, chunk_size=100):
    #chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]
    #return chunks
    
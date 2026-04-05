from data import DbConnection
from pipeline import download_and_parse
from parse import parse_many_demos



if __name__ == "__main__":
    connection = DbConnection()

    download_and_parse(19, "regulation", connection)
    download_and_parse(19, "combines", connection)
    download_and_parse(19, "preseason", connection)
    
    # parse_many_demos("CSC", "Regulation", 19, "C:/Users/Sjh47/Downloads/dems", connection)

    
    
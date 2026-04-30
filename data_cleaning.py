import pandas as pd 

"""
This file contains the data cleaning function that loads the raw book data, cleans it, and prepares it for graph. The data was abtained from Kaggle: https://www.kaggle.com/datasets/mdhamani/goodreads-books-100k?resource=download, which originally came from Goodreads. The data had 100,000 books, but for the purpose of this project, we will only be using the top 2,000 popular books (determined by the number of ratings). 
"""

# Excluding genres that are too broad or describe the format/target audience rather than the content of the book 
GENRE_EXCLUDE = {"audiobook", "young adult", "adult", "fiction", "nonfiction", "novels", "childrens"}

def load_and_clean_data(file_path, max_books=2000): 

    df = pd.read_csv(file_path)

    # Keeping only the relevant columns 
    df = df[["author", "title", "genre", "rating", "totalratings"]]

    # Dropping rows with missing values 
    df = df.dropna(subset=["author", "title", "genre", "rating", "totalratings"]) 

    #Converting rating and totalratings to numeric 
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["totalratings"] = pd.to_numeric(df["totalratings"], errors="coerce")

    df.dropna(subset=["rating", "totalratings"], inplace=True)

    # Filtering books with at least 100 ratings 
    df = df[df["totalratings"] >= 100]  

    # Formatting genre into a clean list separated by |, and excluding genres in GENRE_EXCLUDE 
    df["genre_list"] = df["genre"].apply(
    lambda x: "|".join([
        g.strip()
        for g in str(x).split(",")
        if g.strip() != "" and g.strip().lower() not in GENRE_EXCLUDE
    ])
)

    df = df.sort_values(
        by=["totalratings", "rating"],
        ascending=False
    )

    df = df.drop(columns=["genre"])

    df = df.head(max_books)

    return df 

if __name__ == "__main__":
    print("Cleaning data")
    df = load_and_clean_data("books.csv")
    df.to_csv("cleaned_books.csv", index=False)
    print("Saved file")
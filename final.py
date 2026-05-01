
from collections import deque
import heapq 
import pandas as pd 


class Book:
    """
    Represents a book with its title, author, genres, rating, and total ratings.

    Attributes: 
    - title (str): The title of the book.
    - author (str): The author of the book.
    - genres (list): A list of genres for the book.
    - rating (float): The rating of the book.
    - totalratings (int): The total number of ratings for the book.

    Methods: 
    - __init__(self, title, author, genres, rating, totalratings): Initializes a Book instance 
    - __repr__(self): Returns a string representation of the book.

   """

    def __init__(self, title, author, genres, rating, totalratings):
        self.title = title
        self.author = author
        self.genres = genres
        self.rating = rating
        self.totalratings = totalratings

    def __repr__(self):
        return f"{self.title} by {self.author}"
    


class BookGraph: 

    """
    Represents a graph where nodes are books are edges are weighted by similarity scores based on shared genres, author, and rating. 

    Attributes: 
    - adj_list (dict): An adjacency list representing the graph. The keys are book titles and values are dictionaries of neighboring books and edge data.

    Methods: 
    - __init__(self): Initializes an empty graph.
    - add_node(self, book_title): Adds a book node to the graph.
    - add_edge(self, book1, book2, shared_genres, similarity_score): Adds an edge between two books with the given shared genres and similarity score. 
    - get_neighbors(self, book_title): Returns the neighbors of a book title.
    - shortest_path(self, start_title, target_title): Finds the shortest path between two book titles using BFS.
    - weighted_path(self, start_title, target_title, max_length=5): Finds the path with the highest similarity score between two book using a weighted Dijkstra's algorithm 
    - reconstruct_path(self, previous, start_title, target_title): Helper function to reconstruct the path  graph search algorithm.
    """

    def __init__(self):
        self.adj_list = {}

    def add_node(self, book_title):
        if book_title not in self.adj_list:
            self.adj_list[book_title] = {}

    def add_edge(self, book1, book2, shared_genres, similarity_score):
        self.add_node(book1.title)
        self.add_node(book2.title)

        edge_data = {
            "weight": similarity_score,
            "shared_genres": shared_genres,
            #"relationship": "shared_genre"
        }

        self.adj_list[book1.title][book2.title] = edge_data
        self.adj_list[book2.title][book1.title] = edge_data


    def get_neighbors(self, book_title):

        return self.adj_list.get(book_title, {})
    

    def shortest_path(self, start_title, target_title):
        
        if start_title not in self.adj_list or target_title not in self.adj_list:
            return None

        queue = deque([start_title])
        visited = {start_title}
        previous = {}

        while queue:
            current = queue.popleft()

            if current == target_title:
                break

            for neighbor in self.adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    previous[neighbor] = current
                    queue.append(neighbor)

        if target_title not in visited:
            return None

        return self.reconstruct_path(previous, start_title, target_title)


    def weighted_path(self, start_title, target_title, max_length=5):

        if start_title not in self.adj_list:
            return None

        if target_title not in self.adj_list:
            return None
        
        priority_queue = [(0, start_title, 1)]  
        distances = {start_title: 0}
        previous = {}
        path_lengths = {start_title: 1}

        while priority_queue:
            current_cost, current, length = heapq.heappop(priority_queue)

            if length > max_length:
                continue

            if current == target_title:
                break

            for neighbor, edge_data in self.adj_list[current].items():
                similarity = edge_data["weight"]

                if similarity <= 0:
                    continue

                edge_cost = 1 / similarity
                new_cost = current_cost + edge_cost
                new_length = length + 1

                if new_length > max_length:
                    continue

                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    previous[neighbor] = current
                    path_lengths[neighbor] = new_length

                    heapq.heappush(priority_queue, (new_cost, neighbor, new_length))

        if target_title not in previous:
            return None

        return self.reconstruct_path(previous, start_title, target_title)


    def reconstruct_path(self, previous, start_title, target_title):

        path = []
        current = target_title

        while current != start_title:
            path.append(current)
            current = previous[current]

        path.append(start_title)
        path.reverse()

        return path
    
class RecommendationSystem:

    """
    Represents the book recommendation system that loads book data, builds a graph based on book similarities, and provides options ot search for books, view book details, find path between books, and recommend similar books. 

    Attributes:
    - books (dict): A dictionary of book titles to Book objects.
    - graph (BookGraph): The graph representing book similarities.

    Methods:
    - __init__(self): Initializes the recommendation system with an empty book dictionary and a new BookGraph.
    - load_data(self, filepath): Loads and cleans book data from a CSV file
    - similarity_score(self, book1, book2): Calculates a similarity score based on shared genres, author, and rating.
    - build_graph(self): Builds the graph by adding nodes for each book and edges based on similarity scores.
    - search_books(self, keyword): Searches for books by title keyword.
    - get_book_details(self, title): Retrieves details for a specific book title.
    - find_book_path(self, start_title, target_title, weighted=True): Finds a path between two books using either the weighted or the unweighted option 
    - recommend_similar_books(self, title, top_n=5): Recommends similar books based on shared genres and similarity scores.
    - explain_path(self, path): Provides an explanation of the path between books, including shared genres and similarity scores for each step.

    """
    def __init__(self):

        self.books = {}
        self.graph = BookGraph()


    def load_data(self, filepath):
        
        df = pd.read_csv(filepath)

        for _, row in df.iterrows():
            title = row["title"]
            genres = row["genre_list"].split("|")

            book = Book(
                title=row["title"],
                author=row["author"],
                genres=genres,
                rating=row["rating"],
                totalratings=row["totalratings"]
            )

            self.books[title] = book
    

    def similarity_score(self, book1, book2):

        # Calculate shared genres: each shared genre adds 1 point to the score
        shared_genres = list(set(book1.genres) & set(book2.genres))

        if not shared_genres:
            return 0, []

        genre_score = len(shared_genres)

        # Calculate author similarity: same author adds 1 point
        if book1.author == book2.author: 
            author_score = 1
        else:
            author_score = 0
        
        # Calculate rating similarity: average rating of the two node books normalized to 0-1 scale
        # avg_rating = (book1.rating + book2.rating) / 2
        # rating_score = avg_rating / 5

        # Final similarity score is a weighted sum of genre and author similarities
        similarity = genre_score + author_score 

        return similarity, shared_genres
    

    def build_graph(self):

        book_list = list(self.books.values())

        for book in book_list:
            self.graph.add_node(book.title)

        for i in range(len(book_list)):
            for j in range(i + 1, len(book_list)):
                book1 = book_list[i]
                book2 = book_list[j]

                score, shared_genres = self.similarity_score(book1, book2)

                if score > 0:
                    self.graph.add_edge(book1, book2, shared_genres, score)


    def search_books(self, keyword):
       
        results = []

        for title, book in self.books.items():
            if keyword.lower() in title.lower():
                results.append(book)

        return results
    

    def get_book_details(self, title):
        
        return self.books.get(title)
    

    def find_book_path(self, start_title, target_title, weighted=True):
        
        if weighted:
            return self.graph.weighted_path(start_title, target_title)

        return self.graph.shortest_path(start_title, target_title)
    

    def recommend_similar_books(self, title, top_n=5):
        
        if title not in self.graph.adj_list:
            return []

        neighbors = self.graph.get_neighbors(title)

        neighbor_list = list(neighbors.items())

        def get_weight(pair):
            return pair[1]["weight"]
    
        neighbor_list.sort(key=get_weight, reverse=True)

        return neighbor_list[:top_n]

    def explain_path(self, path):
        
        if path is None:
            return []

        explanations = []

        for i in range(len(path) - 1):
            book1 = path[i]
            book2 = path[i + 1]

            edge = self.graph.adj_list[book1][book2]

            explanations.append({
                "from": book1,
                "to": book2,
                "shared_genres": edge["shared_genres"],
                "similarity_score": edge["weight"]
            })

        return explanations

def main(): 
    system = RecommendationSystem()
    system.load_data("cleaned_books.csv")
    system.build_graph()

    print("Book Recommendation System")
    print("Books loaded:", len(system.books))

    print("The purpose of this system is to recommend books based on shared genres and author. It would help you develop a path of book recoemmndations from a book you like to a book that you would like to read and enjoy. You can also search for books and view book details.")

    while True:
        print("\nChoose what you want to do:")
        print("1. Search for a book")
        print("2. View book details")
        print("3. Find path between two books")
        print("4. Recommend similar books")
        print("5. Quit")

        choice = input("Enter 1-5: ")

        if choice == "1":
            keyword = input("Enter a keyword (part of a book title): ")
            results = system.search_books(keyword)

            if not results:
                print("No books found.")
            else:
                for book in results[:10]:
                    print(book)

        elif choice == "2":
            title = input("Enter exact book title: ")
            book = system.get_book_details(title)

            if book is None:
                print("Book not found.")
            else:
                print("\nTitle:", book.title)
                print("Author:", book.author)
                print("Rating:", book.rating)
                print("Total ratings:", book.totalratings)
                print("Genres:", ", ".join(book.genres))

        elif choice == "3":
            start = input("Enter starter book title: ")
            target = input("Enter target book title: ")

            method = input("Choose path method: 1 for unweighted (shortest path), 2 for weighted (smoothest path using similarity scores): ")

            if method == "1":
                path = system.find_book_path(start, target, weighted=False)
            elif method == "2":
                path = system.find_book_path(start, target, weighted=True)

            if path is None:
                print("No path found.")
            else:
                print("\nRecommended path:")
                print(" -- ".join(path))

                explanation = system.explain_path(path)
                for step in explanation:
                    print()
                    print(step["from"], "--", step["to"])
                    print("Shared genres:", ", ".join(step["shared_genres"]))
                    print("Similarity score:", round(step["similarity_score"], 2))


        elif choice == "4":
            title = input("Enter exact book title: ")
            recs = system.recommend_similar_books(title)

            if not recs:
                print("No recommendations found.")
            else:
                print("\nSimilar books:")
                for rec_title, edge_data in recs:
                    print()
                    print(rec_title)
                    print("Shared genres:", ", ".join(edge_data["shared_genres"]))
                    print("Similarity score:", round(edge_data["weight"], 2))

        elif choice == "5":
            print("End!")
            break

        else:
            print("Invalid choice. Please enter 1-5.")



if __name__ == "__main__":
    main()

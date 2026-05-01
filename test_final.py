import unittest
from final import Book, BookGraph, RecommendationSystem

class TestBookGraph(unittest.TestCase):
    
    def test_add_book(self): 
        graph = BookGraph()
        graph.add_node("Book A")
        self.assertIn("Book A", graph.adj_list)

    def test_add_edge(self):
        graph = BookGraph()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 1000)
        book2 = Book("Book B", "Author B", ["Genre1"], 4.0, 800)

        graph.add_edge(book1, book2, ["Genre1"], 0.5)
        self.assertIn("Book B", graph.adj_list["Book A"])
        self.assertIn("Book A", graph.adj_list["Book B"])
        self.assertEqual(graph.adj_list["Book A"]["Book B"]["shared_genres"], ["Genre1"])

    def test_shortest_path(self): 
        graph = BookGraph()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 1000)
        book2 = Book("Book B", "Author B", ["Genre1"], 4.0, 800)
        book3 = Book("Book C", "Author C", ["Genre2"], 3.5, 500)

        graph.add_edge(book1, book2, ["Genre1"], 0.5)
        graph.add_edge(book2, book3, ["Genre2"], 0.5)

        path = graph.shortest_path("Book A", "Book C")
        self.assertEqual(path, ["Book A", "Book B", "Book C"])

    def test_weighted_path(self): 
        graph = BookGraph()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 1000)
        book2 = Book("Book B", "Author B", ["Genre1"], 4.5, 1000)
        book3 = Book("Book C", "Author C", ["Genre2"], 4.5, 1000)
        book4 = Book("Book D", "Author D", ["Genre1"], 4.5, 1000)

        # book 1 to book 2 to book 4 
        graph.add_edge(book1, book2, ["Genre1"], 0.5)
        graph.add_edge(book2, book4, ["Genre2"], 0.9)

        # book 1 to book 3 to book 4
        graph.add_edge(book1, book3, ["Genre1"], 0.5)
        graph.add_edge(book3, book4, ["Genre2"], 0.5)

        # should prefer option 2 since it has higher similarity score
        path = graph.weighted_path("Book A", "Book D")
        self.assertEqual(path, ["Book A", "Book B", "Book D"])

class TestRecommendationSystem(unittest.TestCase):

    def test_similarity_score_not_sharing_genres(self): 
        sys = RecommendationSystem()

        book1 = Book("Book A", "Author A", ["Genre2"], 4.5, 800)
        book2 = Book("Book B", "Author B", ["Genre1"], 4.0, 800)

        score, shared = sys.similarity_score(book1, book2)
        self.assertEqual(score, 0)
        self.assertEqual(shared, [])

    def test_similarity_score_sharing_genres(self):
        sys = RecommendationSystem()

        book1 = Book("Book ", "Author A", ["Genre1", "Genre2"], 4.5, 800)
        book2 = Book("Book B", "Author B", ["Genre1"], 4.0, 800)

        score, shared = sys.similarity_score(book1, book2)
        self.assertEqual(score, 1)
        self.assertEqual(shared, ["Genre1"])

    def test_search_books(self):
        sys = RecommendationSystem()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 800)
        sys.books["Book A"] = book1

        results = sys.search_books("Book A")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Book A")
    
    def test_book_details(self): 
        sys = RecommendationSystem()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 800)

        sys.books["Book A"] = book1

        details = sys.get_book_details("Book A")    
        self.assertEqual(details.author, "Author A")

    def test_recommend_similar_books(self): 
        
        sys = RecommendationSystem()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 800)
        book2 = Book("Book B", "Author A", ["Genre1"], 4.0, 800)

        sys.books["Book A"] = book1
        sys.books["Book B"] = book2

        sys.graph.add_edge(book1, book2, ["Genre1"], 1.5)
        recommendations = sys.recommend_similar_books("Book A", top_n=1)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0][0], "Book B")

    def test_build_graph(self): 

        sys = RecommendationSystem()

        book1 = Book("Book A", "Author A", ["Genre1"], 4.5, 800)
        book2 = Book("Book B", "Author A", ["Genre1"], 4.0, 800)
        book3 = Book("Book C", "Author B", ["Genre2"], 3.5, 500)

        sys.books["Book A"] = book1
        sys.books["Book B"] = book2
        sys.books["Book C"] = book3

        sys.build_graph()

        self.assertIn("Book B", sys.graph.adj_list["Book A"])
        self.assertIn("Book A", sys.graph.adj_list["Book B"])
        self.assertNotIn("Book C", sys.graph.adj_list["Book A"])
        self.assertNotIn("Book C", sys.graph.adj_list["Book B"])


if __name__ == "__main__":
    unittest.main()
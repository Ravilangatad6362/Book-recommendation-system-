from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

# Load necessary data and models
try:
    popular_df = pickle.load(open('populars.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    raise RuntimeError("Required pickle files are missing.")

app = Flask(__name__)


# Home Route
@app.route('/')
def index():
    return render_template(
        'index.html',
        book_name=popular_df['Book-Title'].to_list(),
        author=popular_df['Book-Author'].to_list(),
        img=popular_df['Image-URL-M'].to_list(),
        votes=popular_df['num_ratings'].to_list(),
        ratings=popular_df['avg_rating'].to_list()
    )


# Recommendation Page
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


# Recommend Books Logic
@app.route('/recommend_books', methods=['POST'])
def recommend():
    try:
        user_input = request.form.get('user_input')
        if user_input not in pt.index:
            return render_template('recommend.html', data=None, error="Book not found!")

        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(
            list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True
        )[1:5]

        data = []
        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item = [
                temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0],
                temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0],
                temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]
            ]
            data.append(item)

        return render_template('recommend.html', data=data)

    except Exception as e:
        print(f"Error: {e}")
        return render_template('recommend.html', data=None, error="An error occurred while processing your request.")


# Run the application
if __name__ == '__main__':
    app.run(debug=True)

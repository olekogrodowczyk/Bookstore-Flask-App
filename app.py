from flask import Flask, render_template, redirect, url_for, request, flash, session
from models import db, Book, User, Genre
from forms import BookForm, GenreForm
from auth import bp as auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db.init_app(app)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    if 'user_id' not in session:
        flash('You must be logged in to view the book list', 'error')
        return redirect(url_for('auth.login'))
    
    books = Book.query.join(Genre, Book.genre_id == Genre.id).add_columns(
        Book.id, Book.title, Book.author, Book.year, Genre.name.label('genre_name')
    ).all()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to add a book', 'error')
        return redirect(url_for('index'))

    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            genre_id=form.genre.data,
            year=form.year.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_book.html', form=form)

@app.route('/update/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to update a book', 'error')
        return redirect(url_for('index'))

    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.genre_id = form.genre.data
        book.year = form.year.data
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('update_book.html', form=form, book=book)

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to delete a book', 'error')
        return redirect(url_for('index'))

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        books = Book.query.join(Genre, Book.genre_id == Genre.id).add_columns(
            Book.id, Book.title, Book.author, Book.year, Genre.name.label('genre_name')
        ).filter(
            (Book.title.like(f'%{search_query}%')) |
            (Book.author.like(f'%{search_query}%')) |
            (Genre.name.like(f'%{search_query}%'))
        ).all()
        return render_template('search.html', books=books, search_query=search_query)
    return render_template('search.html')

@app.route('/add_genre', methods=['GET', 'POST'])
def add_genre():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to add a genre', 'error')
        return redirect(url_for('index'))

    form = GenreForm()
    if form.validate_on_submit():
        new_genre = Genre(name=form.name.data)
        db.session.add(new_genre)
        db.session.commit()
        flash('Genre added successfully!', 'success')
        return redirect(url_for('add_genre'))
    return render_template('add_genre.html', form=form)

@app.route('/genres', methods=['GET'])
def list_genres():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to view genres', 'error')
        return redirect(url_for('index'))

    genres = Genre.query.all()
    return render_template('list_genres.html', genres=genres)

@app.route('/update_genre/<int:genre_id>', methods=['GET', 'POST'])
def update_genre(genre_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to update a genre', 'error')
        return redirect(url_for('index'))

    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm(obj=genre)
    if form.validate_on_submit():
        genre.name = form.name.data
        db.session.commit()
        flash('Genre updated successfully!', 'success')
        return redirect(url_for('list_genres'))
    return render_template('update_genre.html', form=form, genre=genre)

@app.route('/delete_genre/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('You must be an administrator to delete a genre', 'error')
        return redirect(url_for('index'))

    genre = Genre.query.get_or_404(genre_id)
    if Book.query.filter_by(genre_id=genre_id).first():
        flash('Cannot delete genre with associated books', 'error')
        return redirect(url_for('list_genres'))

    db.session.delete(genre)
    db.session.commit()
    flash('Genre deleted successfully!', 'success')
    return redirect(url_for('list_genres'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Genre.query.first():
            genres = ['Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Biography', 'Mystery']
            for genre_name in genres:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            db.session.commit()
    app.run(debug=True)

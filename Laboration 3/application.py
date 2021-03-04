from bottle import get, post, run, request, response
import sqlite3


db = sqlite3.connect("movies.sqlite")


@get('/ping')
def get_ping():
    c = db.cursor()

    response.status = 200
    return {"pong": response.status}


@post('/reset')
def movies_reset():
    c = db.cursor()

    c.execute(
        """
        DELETE FROM theaters
        """,
    )

    c.execute(
        """
        DELETE FROM movies
        """,
    )

    c.execute(
        """
        DELETE FROM screenings
        """,
    )

    c.execute(
        """
        DELETE FROM tickets
        """,
    )

    c.execute(
        """
        DELETE FROM users
        """,
    )

    c.execute(
        """
       INSERT
       INTO   theaters(theater, capacity)
       VALUES ('Kino', 10 ),
              ('Regal', 16),
              ('Skandia', 100);
        """,
    )
    db.commit()

    return{"reset complete" : response.status}


@post('/users')
def post_user():
    user = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT username
        FROM users
        WHERE username = ?
        """,
        [user['username']]
    )
    found = [{"username" : username} for username in c]

    if not found:
        c.execute(
            """
            INSERT
            INTO      users(username, fullName, pwd)
 	        VALUES    (?, ?, ?)
            """,
            [user['username'], user['fullName'], user['pwd']]
            #[user['username'], user['fullName'], user[hash('pwd')]]
        )
        response.status = 201
        db.commit()
        return {"/user/" + user['username'] + " " + response.status}

    else:
        response.status = 400
        return {" " : response.status}



@post('/movies')
def post_movies():
    movie = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT imdbKey
        FROM movies
        WHERE imdbKey = ?
        """,
        [movie['imdbKey']]
    )
    found = [{"imbdKey" : imdbKey} for imdbKey in c]

    if not found:
        c.execute(
            """
            INSERT
            INTO    movies (imdbKey, title, year)
	        VALUES (?, ?, ?)
            """,
            [movie['imdbKey'], movie['title'], movie['year']]
        )
        response.status = 200
        db.commit()
        return {"/movies/" + movie['imdbKey'] + " for " + movie['title'] + " " + response.status}

    else:
        response.status = 400
        return {" " : response.status}



@post('/performances')
def post_performance():
    movie = request.json
    theater = request.json
    screening = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT imdbKey
        FROM movies
        WHERE imdbKey = ?
        """,
        [movie['imdbKey']]
    )
    c2 = db.cursor()
    c2.execute(
        """
        SELECT theater
        FROM theaters
        WHERE theater = ?
        """,
        [theater['theater']]
    )

    found_title = [{"imdbKey" : imdbKey} for imdbKey in c]
    found_theater = [{"theater" : theater} for theater in c2]

    if found_theater and found_title:
        c.execute(
        """
        SELECT capacity
        FROM theaters
        WHERE theater = ?
        """,
        [theater['theater']]
        )
        capacity = c.fetchone()[0]

        c.execute(
            """
            INSERT
            INTO screenings (imdbKey, theater, date, time)
	        VALUES ( ?, ?, ?, ?)
            """,
            [screening['imdbKey'], screening['theater'], screening['date'], screening['time']]
        )
        db.commit()
        c.execute(
            """
            SELECT performanceId
            FROM screenings
            WHERE rowid = last_insert_rowid()
            """,
        )
        id = c.fetchone()[0]
        c.execute(
        """
           UPDATE screenings
           SET remainingSeats = (
                                SELECT capacity
                                FROM theaters
                                WHERE theater = ?
                                )
           WHERE performanceId = (
                                  SELECT performanceId
                                  FROM screenings
                                  WHERE rowid = last_insert_rowid()
                                 )
           """,
           [screening['theater']]
        )

        response.status = 201
        db.commit()
        return {"/performances/" + id + " " + response.status}

    else:
        response.status = 400
        return {"No such movie or theater" : response.status}





@get('/movies')
def get_movies():
    c = db.cursor()
    query = """
        SELECT   imdbKey, title, year
        FROM    movies
        WHERE 1 = 1
        """
    params = []
    if request.query.title:
        query += " AND title = ?"
        params.append(request.query.title)

    if request.query.year:
        query += " AND year = ?"
        params.append(request.query.year)
    c = db.cursor()
    c.execute(
        query,
        params
    )
    found = [{"imdbKey": imdbKey, "title": title, "year": year} for imdbKey, title, year in c]
    return {"data" : found}


@get('/movies/<imdbKey>')
def get_movie(imdbKey):
    c = db.cursor()
    c.execute(
        """
        SELECT imdbKey, title, year
        FROM movies
        WHERE imdbKey = ?
        """,
        [imdbKey]
    )
    found = [{"imdbKey": imdbKey, "title": title, "year": year} for imdbKey, title, year in c]

    if found:
        return {"data" : found}

    else:
        return {" "}



@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute(
        """
        SELECT performanceId, date, time, title, year, theater, remainingSeats
        FROM screenings
        JOIN movies
        USING (imdbKey)
        """,
    )
    found = [{"performanceId": performanceId, "date": date, "time": time, "title": title, "year": year, "theater": theater, "remainingSeats": remainingSeats} for performanceId, date, time, title, year, theater, remainingSeats in c]
    return {"data" : found}


@post('/tickets')
def post_tickets():
    ticket = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT username
        FROM users
        WHERE username = ? AND pwd = ?
        """,
        [ticket['username'], ticket['pwd']]
    )

    found_user = [{"username" : username} for username in c]
    
    if found_user:
        c.execute(
        """
        SELECT performanceId
        FROM screenings
        WHERE  performanceId = ? AND remainingSeats > 1
        """,
        [ticket['performanceId']]
    )
        found_seat = [{"performanceId" : performanceId} for performanceId in c]

        if found_seat:
            c.execute(
            """
            INSERT
            INTO tickets (theater, imdbKey, time, date)
	        SELECT theater, imdbKey, time, date
            FROM screenings
            WHERE performanceId = ?
            """,
            [ticket['performanceId']]
        )

            db.commit()

            c.execute(
            """
            SELECT id
            FROM tickets
            WHERE rowid = last_insert_rowid()
            """,
        )
            ticketId = c.fetchone()[0]

            c.execute(
            """
            UPDATE tickets
            SET username = ?
            WHERE rowid = last_insert_rowid()
            """,
            [ticket['username']]
        )

            c.execute(
            """
            UPDATE screenings
            SET remainingSeats = remainingSeats - 1
            WHERE performanceId = ?
            """,
            [ticket['performanceId']]
        )

            db.commit()

            response.status = 201
            return {"/tickets/" + ticketId + " " + response.status}

        else:
            response.status = 400
            return {"No tickets left" : response.status}

    else:
        response.status = 401
        return {"Wrong user credentials" : response.status}


@get('/users/<username>/tickets')
def get_users_tickets(username):
    user = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT date, time as startTime, theater, title, year, count() as numberOfTickets
        FROM tickets
        JOIN movies
        USING (imdbKey)
        WHERE username = ?
        GROUP BY date, startTime, theater, title, year
        """,
        [username]
    )

    found = [{"date": date, "startTime": startTime, "theater": theater, "title": title, "year": year, "numberOfTickets": numberOfTickets} for date, startTime, theater, title, year, numberOfTickets in c]
    return {"data" : found}

def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()


run(host='localhost', port=7007)
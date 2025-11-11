from flask import Blueprint, render_template, abort, request, redirect, url_for
from .db import get_connection

bp = Blueprint("routes", __name__)

@bp.route("/")
def home():
    return "<p>Hi Julian! Try <a href='/pokemon'>/pokemon</a>, <a href='/thunderbolt'>/thunderbolt</a>, or <a href='/comments'>/comments</a>.</p>"

@bp.route("/comments", methods=["GET", "POST"])
def comments():
    # Handle form submission
    if request.method == "POST":
        pokemon_id = request.form.get("pokemon_id", "").strip()
        username   = request.form.get("username", "").strip()
        body       = request.form.get("body", "").strip()

        # Simple validation
        if not pokemon_id or not username or not body:
            return _render_comments(err="Please fill in all fields.")

        if len(username) > 40:
            return _render_comments(err="Username must be 40 characters or fewer.")
        if len(body) > 500:
            return _render_comments(err="Comment must be 500 characters or fewer.")

        # Insert safely (parameterized)
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO poke.[Comment] (PokemonID, Username, Body) VALUES (?, ?, ?);",
                        (int(pokemon_id), username, body)
                    )
                    conn.commit()
        except Exception as e:
            return _render_comments(err=f"DB error while saving: {e}")

        # Redirect to avoid resubmission on refresh
        return redirect(url_for("routes.comments", ok=1))

    # GET
    return _render_comments(ok=1 if request.args.get("ok") else 0)

def _render_comments(ok=0, err=None):
    # Load Pokémon for dropdown
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT PokemonID, PokedexNo, Name
                    FROM poke.Pokemon
                    ORDER BY PokedexNo;
                """)
                pokemon = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    except Exception as e:
        abort(500, f"DB error loading pokemon: {e}")

    # Load latest comments (joined to Pokémon name)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT TOP 20
                        c.CreatedAt,
                        p.Name AS PokemonName,
                        c.Username,
                        c.Body
                    FROM poke.[Comment] c
                    JOIN poke.Pokemon p ON p.PokemonID = c.PokemonID
                    ORDER BY c.CreatedAt DESC;
                """)
                cols = [d[0] for d in cur.description]
                comments = [dict(zip(cols, r)) for r in cur.fetchall()]
    except Exception as e:
        abort(500, f"DB error loading comments: {e}")

    return render_template("comments.html",
                           pokemon=pokemon,
                           comments=comments,
                           ok=ok,
                           err=err)

@bp.route("/pokemon")
def pokemon_list():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.PokedexNo, p.Name, t1.Name AS PrimaryType, t2.Name AS SecondaryType
                    FROM poke.Pokemon p
                    LEFT JOIN poke.Type t1 ON t1.TypeID = p.PrimaryTypeID
                    LEFT JOIN poke.Type t2 ON t2.TypeID = p.SecondaryTypeID
                    ORDER BY p.PokedexNo;
                """)
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
    except Exception as e:
        abort(500, f"DB error: {e}")

    data = [dict(zip(cols, r)) for r in rows]
    return render_template("pokemon_list.html", rows=data)

@bp.route("/thunderbolt")
def thunderbolt():
    sql = """
        SELECT p.Name
        FROM poke.Pokemon p
        JOIN poke.PokemonMove pm ON pm.PokemonID = p.PokemonID
        JOIN poke.Move m ON m.MoveID = pm.MoveID
        WHERE m.Name = 'Thunderbolt'
        ORDER BY p.Name;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = [r[0] for r in cur.fetchall()]
    except Exception as e:
        abort(500, f"DB error: {e}")

    return render_template("thunderbolt.html", names=rows)

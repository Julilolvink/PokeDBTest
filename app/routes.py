from flask import Blueprint, render_template, abort
from .db import get_connection

bp = Blueprint("routes", __name__)

@bp.route("/")
def home():
    return "<p>Hi Julian! Try <a href='/pokemon'>/pokemon</a> or <a href='/thunderbolt'>/thunderbolt</a>.</p>"

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

from app import create_app
app = create_app()

if __name__ == "__main__":
    # Debug True is fine for local learning
    app.run()

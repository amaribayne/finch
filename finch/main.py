from app import create_app

app = create_app()

# Run the app if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)

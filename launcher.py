import threading
import webview
import app  # this runs your Flask app

def start_server():
    app.app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    # Start Flask in background
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # Wait a bit to ensure Flask is ready
    import time
    time.sleep(2)

    # Open in native window
    webview.create_window("Expense Tracker", "http://127.0.0.1:5000", width=1200, height=800)
    webview.start()

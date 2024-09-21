import os
import ssl
import certifi
from urllib import request

def install_certificates():
    if os.name == 'nt':
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        print("SSL context updated to use certifi certificates.")

    # Test the installation by making an HTTPS request
    try:
        response = request.urlopen('https://www.google.com')
        print("Successfully accessed Google with updated SSL context.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    install_certificates()

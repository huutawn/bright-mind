import requests
import sys

def test_gemini_integration(bill_path, charity_path):
    url = "http://localhost:8000/api/gemini/analyze-donation"
    
    try:
        files = [
            ('bill_file', ('bill.jpg', open(bill_path, 'rb'), 'image/jpeg')),
            ('charity_file', ('charity.jpg', open(charity_path, 'rb'), 'image/jpeg'))
        ]
        
        print(f"Sending request to {url}...")
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            print("Success! Response from Gemini:")
            print(response.json())
        else:
            print(f"Failed with status code {response.status_code}")
            print(response.text)
            
    except FileNotFoundError:
        print("Error: Could not find one of the image files.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify_gemini_integration.py <path_to_bill_image> <path_to_charity_image>")
    else:
        test_gemini_integration(sys.argv[1], sys.argv[2])

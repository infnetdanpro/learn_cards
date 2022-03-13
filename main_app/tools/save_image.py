import requests
import os


def save_image(query: str, save_path: str) -> bool:
    r = requests.get(
        url="https://pixabay.com/api/?key=14192256-5d73239f8a547cabd0bac9c2b&image_type=vector&editors_choice&per_page=3&q=%s&lang=ru"
        % query
    )
    if r.status_code == 200:
        response = r.json()
        first_image = response["hits"][0]["previewURL"]
        r = requests.get(url=first_image, stream=True)
        os.makedirs(save_path)
        path = os.path.dirname(save_path, query)
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    else:
        return False


if __name__ == "__main__":
    result = save_image("car")
    print(result)

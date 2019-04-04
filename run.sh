# docker run -it --rm -p 8080:8080 -v $(pwd)/app:/home who_says_dajare:latest /bin/bash
docker run -it --rm -p 5000:5000 -v $(pwd)/app:/home who_says_dajare:latest python3 home/main.py

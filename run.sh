cd "$(dirname "$0")"

docker run -d --restart unless-stopped -p 8501:8501 -v/root/learn_english/html/videos:/html/videos learn_english

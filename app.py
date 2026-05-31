import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def analyze_channel(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'playlist_items': '1,10', # Берем только последние 10 видео для скорости
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
            
            title = info.get('title', 'YouTube Канал')
            entries = info.get('entries', [])
            video_count = len(entries)
            
            pros = []
            minuses = []
            
            # Анализ
            if video_count >= 10:
                pros.append("Высокая активность: регулярный выпуск новых видео.")
            else:
                minuses.append("Низкая частота публикаций или скрытый список видео.")
                
            if info.get('description'):
                pros.append("Описание канала заполнено, что помогает в поиске.")
            else:
                minuses.append("Отсутствует описание канала (плохо для SEO).")

            if any("shorts" in e.get('url', '').lower() for e in entries):
                pros.append("Использует формат Shorts для привлечения трафика.")
            
            score = 5 + (len(pros) * 1.5) - (len(minuses) * 1.0)
            score = max(1, min(10, round(score, 1)))

            return {
                "name": title,
                "score": score,
                "pros": pros or ["Канал только начинает свой путь"],
                "minuses": minuses or ["Явных ошибок не обнаружено"],
                "advice": "Уделяйте больше внимания ключевым словам в названиях и делайте яркие обложки (превью)."
            }
        except Exception as e:
            return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def handle_analyze():
    data = request.get_json()
    url = data.get('url', '')
    if not url:
        return jsonify({"error": "Введите ссылку"}), 400
    
    result = analyze_channel(url)
    return jsonify(result)

if __name__ == '__main__':
    # Порт для деплоя
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
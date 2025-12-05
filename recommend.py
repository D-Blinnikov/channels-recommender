# ЯЧЕЙКА — УНИВЕРСАЛЬНАЯ ФУНКЦИЯ (вставляй в любой ноутбук)
from sentence_transformers import util
import numpy as np

def recommend_channels(
    query,
    bi_encoder,           # ← теперь принимает модель!
    cross_encoder,        # ← и кросс-энкодер
    index,                # ← FAISS индекс
    df,                   # ← твой датафрейм с постами и каналами
    top_k_posts=100,      # сколько постов берём от Bi
    rerank_top=30,        # сколько из них переранжируем Cross
    agg_top_n=10,         # сколько лучших постов канала берём для среднего
    top_k_channels=10     # сколько каналов вернуть
):
    # 1. Bi-Encoder: быстрый поиск
    query_vec = bi_encoder.encode([query], normalize_embeddings=True)
    scores, indices = index.search(np.float32(query_vec), top_k_posts)
    scores = scores[0]
    indices = indices[0]

    # 2. Cross-Encoder: переранжирование лучших
    if rerank_top > 0 and cross_encoder is not None:
        candidate_posts = [df.iloc[i]['post_text'] for i in indices[:rerank_top]]
        pairs = [(query, post) for post in candidate_posts]
        cross_scores = cross_encoder.predict(pairs)
        scores[:rerank_top] = cross_scores

    # 3. Группировка по каналам
    channel_scores = {}
    for score, idx in zip(scores, indices):
        channel = df.iloc[idx]['channel_name']
        if channel not in channel_scores:
            channel_scores[channel] = []
        channel_scores[channel].append(float(score))

    # 4. Считаем среднее по лучшим agg_top_n постам канала
    final_ranking = []
    for channel, sc_list in channel_scores.items():
        top_scores = sorted(sc_list, reverse=True)[:agg_top_n]
        avg_score = np.mean(top_scores)
        final_ranking.append((channel, avg_score))

    # 5. Сортируем каналы и возвращаем топ
    final_ranking = sorted(final_ranking, key=lambda x: x[1], reverse=True)[:top_k_channels]
    return final_ranking
# vision_function.py

from openai import OpenAI
import json

client = OpenAI()


def ask_openai_json(images_base64: list) -> dict:

    content_list = [
        {"type": "text", "text": "Analyze these sheet music images in order."}
    ]

    # 🔹 여러 이미지 순서대로 추가
    for img in images_base64:
        content_list.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img}"},
            }
        )

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a music score analysis assistant.

When images are provided, you must:

1. Images are ordered.
2. Detect how many songs exist across all images.
3. If consecutive pages share the same title, merge them into one song.
4. For each song, generate a key named "song_{i}" where i starts from 1.
5. Each song_{i} must contain a list with one object.
6. The object must follow this structure:

{
  "song_name": string,
  "song_form": string,
  "<PART_NAME>": string
}

Rules:

- song_form may contain structures like A1BB(8)A2BBCCCDA2
- Parentheses such as (8), (n마디간주), (12) indicate instrumental interlude bars and must remain exactly as written in song_form.
- Do NOT remove or modify parentheses sections.
- When extracting section labels, ignore parentheses content.
- Extract only musical section labels such as A, A1, A2, B, C, D etc.
- If a section appears as C', C* (with apostrophe or *), convert it to C0 in both song_form and section key.
- Do NOT keep apostrophes in section labels.
- Do NOT create section keys for parentheses values like (8).
- For each unique section label, create a key with the same name.
- The value must be the first ~25 characters of the lyrics that START within that labeled section.
- Do NOT include lyrics from the previous section, even if they visually overlap.
- If a section boundary cuts through a lyric line, use only the portion that belongs to the labeled section and continue forward.
- Never reference or copy lyrics that appear before the section label.
- Ensure section lyrics begin from the correct starting point of that labeled section (e.g., prefer "찬양해 ..." instead of text belonging to the previous section like "받아주시네").
- Do NOT invent section names not appearing in song_form.
- The song_form must not contain any spaces.
- Ensure that spacing in each section's lyrics is natural and grammatically correct.
- Output must be valid JSON only.
- No explanation text.
""",
            },
            {
                "role": "user",
                "content": content_list,
            },
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except Exception:
        return {"error": "Invalid JSON response", "raw": content}


def request_openai_autofill(selected_song: dict, full_lyrics: str) -> dict:
    """
    selected_song: auto_maker에서 선택된 곡 정보 전체(JSON dict)
    full_lyrics: 원곡 전체 가사 문자열
    """
    selected_song_text = json.dumps(selected_song, ensure_ascii=False, indent=2)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a Korean worship-song section mapping assistant.

Return JSON only.
No markdown, no code fences, no explanation text.

Task:
1) Use the full original lyrics as the source of truth.
2) Use selected_song JSON as the section-start hints from score parsing.
3) Build section lyrics for each part key appearing in selected_song.
4) Keep song_form exactly as given in selected_song.

Rules:
- Do not invent new part names.
- Ignore metadata keys when building parts: song_name, song_form.
- For each part key, map the correct lyric block from full_lyrics.
- Keep Korean spacing natural.
- Format each part lyric with readability line breaks:
  * Insert one empty line after every 2 non-empty lines.
  * Output shape should look like "2 lines + blank line + 2 lines + blank line ...".
- If a part cannot be confidently mapped, return empty string for that part.

Output schema:
{
  "song_name": string,
  "song_form": string,
  "<PART_KEY>": string
}
""",
            },
            {
                "role": "user",
                "content": f"""selected_song JSON:
{selected_song_text}

full_lyrics:
{full_lyrics}
""",
            },
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except Exception:
        return {"error": "Invalid JSON response", "raw": content}

"""
YouTube Upload Script - Lingexa Vocabulary
Updated for 2025
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()


def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else "MISSING"
    print(f"[youtube] Client ID: {mask(client_id)}")
    print(f"[youtube] Client Secret: {mask(client_secret)}")
    print(f"[youtube] Refresh Token: {mask(refresh_token)}")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError(
            "Missing credentials! Set these environment variables:\n"
            "  - YOUTUBE_CLIENT_ID or YT_CLIENT_ID\n"
            "  - YOUTUBE_CLIENT_SECRET or YT_CLIENT_SECRET\n"
            "  - YOUTUBE_REFRESH_TOKEN or YT_REFRESH_TOKEN"
        )

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    try:
        creds.refresh(Request())
    except Exception as e:
        if "invalid_grant" in str(e).lower():
            print("\n[youtube] AUTH ERROR: Refresh token has EXPIRED or been REVOKED.")
            print("SOLUTION: Generate a new refresh token.")
        raise

    return build('youtube', 'v3', credentials=creds)


def generate_video_metadata(word: str, reel_data: dict = None):
    title = f"Word of the Day: {word} - English Vocabulary"
    if reel_data and reel_data.get("level"):
        title = f"Word of the Day: {word} ({reel_data['level']}) - Learn English"

    description_lines = [
        f"Learn the word '{word}' with Lingexa!",
        "",
    ]

    if reel_data:
        pos = reel_data.get("part_of_speech", "")
        definition = reel_data.get("definition", "")
        example = reel_data.get("example", "")
        synonyms = reel_data.get("synonyms", [])
        pronunciation = reel_data.get("pronunciation", "")
        fun_fact = reel_data.get("fun_fact", "")
        level = reel_data.get("level", "")

        if pronunciation:
            description_lines.append(f"Pronunciation: {pronunciation}")
        if pos:
            description_lines.append(f"Part of Speech: {pos}")
        if level:
            description_lines.append(f"Level: {level}")
        description_lines.append("")
        if definition:
            description_lines.append(f"Meaning: {definition}")
            description_lines.append("")
        if example:
            description_lines.append(f"Example: {example}")
            description_lines.append("")
        if synonyms:
            description_lines.append(f"Synonyms: {', '.join(synonyms)}")
            description_lines.append("")
        if fun_fact:
            description_lines.append(f"Fun Fact: {fun_fact}")
            description_lines.append("")

    description_lines.extend([
        "Learn a new word every day with Lingexa!",
        "Subscribe for daily English vocabulary lessons!",
        "",
        "#Lingexa #Vocabulary #LearnEnglish #WordOfTheDay #EnglishLearning",
        "#VocabularyBuilder #EnglishWords #StudyEnglish #DailyVocabulary",
        "#Shorts"
    ])

    description = "\n".join(description_lines)

    tags = [
        "vocabulary",
        "learn english",
        "word of the day",
        "english vocabulary",
        "english learning",
        "vocabulary builder",
        "english words",
        "lingexa",
        word.lower(),
        "study english",
        "daily vocabulary",
        "english practice"
    ]

    if reel_data and reel_data.get("level"):
        tags.append(reel_data["level"].lower())

    return title, description, tags


def upload_to_youtube(video_path, title, description, tags=None, category_id='27'):
    if tags is None:
        tags = ['education', 'vocabulary', 'english learning', 'lingexa']
    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }

    if '#Shorts' not in body['snippet']['description']:
        body['snippet']['description'] += '\n\n#Shorts'

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True,
        mimetype='video/mp4'
    )

    print(f"[youtube] Uploading: {title}")
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube] Progress: {int(status.progress() * 100)}%")

    print(f"[youtube] Uploaded! Video ID: {response['id']}")
    print(f"[youtube] URL: https://youtube.com/shorts/{response['id']}")

    return response


def main():
    video_file = Path('final_video.mp4')

    if not video_file.exists():
        print("[youtube] No video found at final_video.mp4")
        return

    title = "Learn English Vocabulary Daily"
    description = "#shorts #vocabulary #learnenglish #lingexa"
    tags = ['vocabulary', 'english learning', 'lingexa']

    try:
        upload_to_youtube(
            video_path=video_file,
            title=title,
            description=description,
            tags=tags,
            category_id='27'
        )
    except Exception as e:
        print(f"[youtube] Upload failed: {e}")
        raise


if __name__ == '__main__':
    main()
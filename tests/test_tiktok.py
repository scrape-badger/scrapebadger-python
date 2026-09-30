def test_video_media_headers_survive_model_parsing():
    from scrapebadger.tiktok.models import TikTokVideoMeta

    headers = {"Cookie": "tt_chain_token=anonymous", "Referer": "https://www.tiktok.com/"}
    media = TikTokVideoMeta.model_validate(
        {"play_addr": "https://v16-webapp-prime.tiktok.com/video", "media_headers": headers}
    )
    assert media.model_dump()["media_headers"] == headers

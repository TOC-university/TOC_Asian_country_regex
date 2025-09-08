from pydantic import BaseModel

class Settings(BaseModel):
    BASE_URL: str = "https://en.wikipedia.org"
    START_PAGE: str = "/wiki/Lists_of_universities_and_colleges_by_country"
    TIMEOUT: int = 20
    USER_AGENT: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126 Safari/537.36"
    )
    SLEEP_SEC: float = 0.6

settings = Settings()

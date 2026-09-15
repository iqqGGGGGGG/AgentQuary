from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ai_base_url: str = "https://token-plan-cn.xiaomimimo.com/v1"
    ai_model: str = "mimo-v2.5-pro"
    ai_api_key: str

    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "agentquary"

    wx_appid: str = ""
    wx_secret: str = ""

    dev_mode: bool = True
    auth_secret: str = ""
    auth_token_ttl_seconds: int = 7 * 24 * 60 * 60

    search_enabled: bool = True
    tavily_api_key: str = ""
    search_timeout: int = 15

    chroma_persist_dir: str = "./chroma_data"
    embedding_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_model: str = "text-embedding-v4"
    embedding_api_key: str = ""

    cos_bucket: str = "gqq-agent-1310553153"
    cos_region: str = "ap-beijing"
    cos_secret_id: str = ""
    cos_secret_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def db_url(self) -> str:
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"


settings = Settings()

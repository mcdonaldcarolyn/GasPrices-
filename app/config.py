from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    eia_api_key: str = ""
    fred_api_key: str = ""
    database_url: str = "sqlite:///./data/gas_prices.db"

    eia_series: dict[str, str] = {
        "regular_us":  "EMM_EPMR_PTE_NUS_DPG",
        "midgrade_us": "EMM_EPMM_PTE_NUS_DPG",
        "premium_us":  "EMM_EPMP_PTE_NUS_DPG",
        "diesel_us":   "EMD_EPD2D_PTE_NUS_DPG",
        # Regional regular unleaded (PADD districts)
        "regular_east":    "EMM_EPMR_PTE_R10_DPG",
        "regular_midwest": "EMM_EPMR_PTE_R20_DPG",
        "regular_gulf":    "EMM_EPMR_PTE_R30_DPG",
        "regular_rocky":   "EMM_EPMR_PTE_R40_DPG",
        "regular_west":    "EMM_EPMR_PTE_R50_DPG",
    }

    fred_series: dict[str, str] = {
        "brent_crude": "DCOILBRENTEU",
        "wti_crude":   "DCOILWTICO",
        "cpi_energy":  "CPIENGSL",
        "usd_index":   "DTWEXBGS",
    }

settings = Settings()
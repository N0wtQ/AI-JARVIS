# Actions module
from .open_app import open_app, open_url
from .web_search import web_search
from .weather_report import get_weather
from .spotify_control import spotify_control
from .system_info import (
    get_system_status_text,
    format_system_report,
    get_private_ip,
    get_public_ip,
    get_cpu_info,
    get_ram_info,
    get_disk_info,
    get_battery_info,
    get_system_info,
    get_network_info
)
from .wolfram_query import (
    query_wolfram,
    calculate,
    get_fact,
    solve_equation,
    convert_units,
    get_detailed_result,
    format_wolfram_response
)

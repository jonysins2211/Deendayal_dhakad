import jinja2
import os
import urllib.parse
import logging
import aiohttp

from info import *
from Deendayal_botz.Bot import DeendayalBot
from Deendayal_botz.util.human_readable import humanbytes
from Deendayal_botz.util.file_properties import get_file_ids
from Deendayal_botz.server.exceptions import InvalidHash
from Template import jisshu_template


async def render_page(id, secure_hash, src=None):
    file = await DeendayalBot.get_messages(int(LOG_CHANNEL), int(id))
    file_data = await get_file_ids(DeendayalBot, int(LOG_CHANNEL), int(id))

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    src = urllib.parse.urljoin(
        URL,
        f"{id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={secure_hash}",
    )

    tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)

    if tag in ["video", "audio"]:
        template_name = "req.html"
    else:
        template_name = "dl.html"
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                file_size = humanbytes(int(u.headers.get("Content-Length")))

    # ✅ Use absolute path (safe for Heroku or any OS)
    template_path = os.path.join(os.path.dirname(__file__), "Deendayal_botz", "template")
    template_loader = jinja2.FileSystemLoader(searchpath=template_path)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_name)

    file_name = file_data.file_name.replace("_", " ")

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
        template_ne=jisshu_template.JISSHU_NAME,
        jisshu_disclaimer=jisshu_template.JISSHU_DISCLAIMER,
        jisshu_report_link=jisshu_template.JISSHU_REPORT_LINK,
        jisshu_colours=jisshu_template.JISSHU_COLOURS
    )

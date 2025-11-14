# plugins/_help.py
# Ultroid - UserBot (Telethon inline help with inline-result keyboard)
from math import ceil
import re
from telethon import events
from telethon.tl import types
from telethon.tl.custom import Button

from pyUltroid.dB._core import HELP, LIST
from pyUltroid.fns.tools import cmd_regex_replace

from . import HNDLR, LOGS, OWNER_NAME, asst, get_string, inline_pic, udB, ultroid_cmd

# Main static menu (kept for fallback)
_main_help_menu = [
    [Button.inline(get_string("help_4"), data="uh_Official_"), Button.inline(get_string("help_5"), data="uh_Addons_")],
    [Button.inline(get_string("help_6"), data="uh_VCBot_"), Button.inline(get_string("help_7"), data="inlone")],
    [Button.inline(get_string("help_8"), data="ownr"), Button.url(get_string("help_9"), url=f"https://t.me/{asst.me.username}?start=set")],
    [Button.inline(get_string("help_10"), data="close")],
]


def paginate_modules(page: int, modules: dict, prefix: str, per_page: int = 6):
    """Return list-of-lists of telethon Buttons for the given page."""
    names = sorted(modules.keys())
    total = len(names)
    last_page = max(0, ceil(total / per_page) - 1)
    page = max(0, min(page, last_page))
    start = page * per_page
    chunk = names[start : start + per_page]

    buttons = []
    row = []
    for name in chunk:
        cb = f"{prefix}_module({name.replace(' ', '_')})"
        row.append(Button.inline(name, data=cb))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # nav row
    nav = []
    if page > 0:
        nav.append(Button.inline("« Prev", data=f"{prefix}_prev({page})"))
    nav.append(Button.inline(f"Page {page+1}/{last_page+1}", data="noop"))
    if page < last_page:
        nav.append(Button.inline("Next »", data=f"{prefix}_next({page})"))
    buttons.append(nav)

    # back row
    buttons.append([Button.inline("• ᴋᴇᴍʙᴀʟɪ •", data=f"{prefix}_back")])
    return buttons


@ultroid_cmd(pattern=r"help( (.*)|$)")
async def _help(ult):
    plug = ult.pattern_match.group(1).strip()
    chat = await ult.get_chat()
    if plug:
        try:
            if plug in HELP["Official"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Official"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
                return
            if HELP.get("Addons") and plug in HELP["Addons"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Addons"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
                return
            if HELP.get("VCBot") and plug in HELP["VCBot"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["VCBot"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
                return

            # try LIST lookup (commands map)
            try:
                x = get_string("help_11").format(plug)
                for d in LIST[plug]:
                    x += HNDLR + d
                    x += "\n"
                x += "\n© @TeamUltroid"
                await ult.eor(x)
                return
            except Exception:
                file = None
                compare_strings = []
                for file_name in LIST:
                    compare_strings.append(file_name)
                    value = LIST[file_name]
                    for j in value:
                        j = cmd_regex_replace(j)
                        compare_strings.append(j)
                        if j.strip() == plug:
                            file = file_name
                            break
                if not file:
                    text = f"`{plug}` is not a valid plugin!"
                    best_match = None
                    for _ in compare_strings:
                        if plug in _ and not _.startswith("_"):
                            best_match = _
                            break
                    if best_match:
                        text += f"\nDid you mean `{best_match}`?"
                    await ult.eor(text)
                    return

                output = f"**Command** `{plug}` **found in plugin** - `{file}`\n"
                if file in HELP["Official"]:
                    for i in HELP["Official"][file]:
                        output += i
                elif HELP.get("Addons") and file in HELP["Addons"]:
                    for i in HELP["Addons"][file]:
                        output += i
                elif HELP.get("VCBot") and file in HELP["VCBot"]:
                    for i in HELP["VCBot"][file]:
                        output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
                return

        except Exception as er:
            LOGS.exception(er)
            await ult.eor("Error 🤔 occured.")
            return

    # no specific plugin requested: show inline result or fallback message with buttons
    try:
        results = await ult.client.inline_query(asst.me.username, "ultd")
    except Exception:
        # Fallback: send menu message with paginated keyboard
        try:
            if udB.get_key("MANAGER") and udB.get_key("DUAL_HNDLR") == "/":
                _main_help_menu[2:3] = [[Button.inline("• Manager Help •", "mngbtn")]]
            await ult.reply(
                get_string("inline_4").format(
                    OWNER_NAME,
                    len(HELP.get("Official", {})),
                    len(HELP.get("Addons", {})),
                    sum(len(v) for v in LIST.values()) + 10,
                ),
                file=inline_pic(),
                buttons=paginate_modules(0, HELP, "help"),
            )
            return
        except Exception as e:
            LOGS.exception(e)
            await ult.eor(get_string("help_2").format(HNDLR))
            return
    else:
        try:
            # click the first inline result (legacy behavior)
            await results[0].click(chat.id, reply_to=ult.reply_to_msg_id, hide_via=True)
            await ult.delete()
            return
        except Exception as e:
            LOGS.exception(e)
            # fallback to message with keyboard
            await ult.reply(
                get_string("inline_4").format(
                    OWNER_NAME,
                    len(HELP.get("Official", {})),
                    len(HELP.get("Addons", {})),
                    sum(len(v) for v in LIST.values()) + 10,
                ),
                file=inline_pic(),
                buttons=paginate_modules(0, HELP, "help"),
            )
            return


@asst.on(events.InlineQuery)
async def inline_help_handler(event: events.InlineQuery.Event):
    query = (event.text or "").strip()
    # Only answer exact 'help' (case-insensitive)
    if not query or query.lower() != "help":
        return

    summary = get_string("inline_4").format(
        OWNER_NAME,
        len(HELP.get("Official", {})),
        len(HELP.get("Addons", {})),
        sum(len(v) for v in LIST.values()) + 10,
    )
    full_msg = summary + "\n\n© @TeamUltroid"

    # Convert telethon Button.inline rows to types.ReplyInlineMarkup so the inserted message contains the keyboard.
    def buttons_to_reply_markup(btn_rows):
        rows = []
        for row in btn_rows:
            kb_buttons = []
            for b in row:
                try:
                    lbl = b.text
                    data = b.data if hasattr(b, "data") else None
                    if data is None:
                        continue
                    if isinstance(data, str):
                        data = data.encode()
                    kb_buttons.append(types.KeyboardButtonCallback(text=lbl, data=data))
                except Exception:
                    continue
            if kb_buttons:
                rows.append(types.KeyboardButtonRow(buttons=kb_buttons))
        return types.ReplyInlineMarkup(rows=rows)

    tele_rows = paginate_modules(0, HELP, "help")
    reply_markup = buttons_to_reply_markup(tele_rows)

    send_message = types.InputBotInlineMessageText(
        message=full_msg,
        reply_markup=reply_markup,
    )

    result = types.InputBotInlineResult(
        id="ultroid_help_1",
        type="article",
        title="Ultroid Help",
        description="Open Ultroid main help menu",
        send_message=send_message,
    )

    try:
        await event.answer([result], cache_time=0)
    except Exception:
        LOGS.exception("Failed to answer inline query")


@asst.on(events.CallbackQuery)
async def help_menu_callback(event: events.CallbackQuery.Event):
    data = event.data.decode() if isinstance(event.data, (bytes, bytearray)) else (event.data or "")
    mod_match = re.match(r"help_module\((.+?)\)", data)
    prev_match = re.match(r"help_prev\((.+?)\)", data)
    next_match = re.match(r"help_next\((.+?)\)", data)
    back_match = re.match(r"help_back", data)

    try:
        prefix_list = udB.get_key("PREFIXES") or [HNDLR]
        top_text = f"<blockquote><b>❏ menu inline <a href=tg://user?id={event.sender_id}>{event.sender.first_name} {event.sender.last_name or ''}</a>\n╰ prefix: {', '.join(prefix_list)}</b></blockquote>"
    except Exception:
        top_text = "<b>Help Menu</b>"

    if mod_match:
        module = (mod_match.group(1)).replace(" ", "_")
        try:
            prefix_list = udB.get_key("PREFIXES") or [HNDLR]
            p = prefix_list[0]
        except Exception:
            p = HNDLR

        if module in HELP["Official"]:
            text = "".join(HELP["Official"][module])
        elif HELP.get("Addons") and module in HELP["Addons"]:
            text = "".join(HELP["Addons"][module])
        elif HELP.get("VCBot") and module in HELP["VCBot"]:
            text = "".join(HELP["VCBot"][module])
        else:
            text = f"<b>Module {module} not found</b>"

        button = [[Button.inline("• ᴋᴇᴍʙᴀʟɪ •", callback_data="help_back")]]
        await event.edit(text=text + "\n<b>Xnxx</b>", buttons=button, parse_mode="html", link_preview=False)
        return

    if prev_match:
        curr_page = int(prev_match.group(1))
        await event.edit(text=top_text, buttons=paginate_modules(curr_page - 1, HELP, "help"))
        return

    if next_match:
        next_page = int(next_match.group(1))
        await event.edit(text=top_text, buttons=paginate_modules(next_page + 1, HELP, "help"))
        return

    if back_match:
        await event.edit(text=top_text, buttons=paginate_modules(0, HELP, "help"))
        return

    await event.answer()


# Plain "help" (no prefix) handler: type "help" and it'll open help menu
from telethon import events as _events

@asst.on(_events.NewMessage(pattern=r'(?i)^help$'))
async def plain_text_help(event: _events.NewMessage.Event):
    try:
        text = get_string("inline_4").format(
            OWNER_NAME,
            len(HELP.get("Official", {})),
            len(HELP.get("Addons", {})),
            sum(len(v) for v in LIST.values()) + 10,
        )
        await event.reply(
            text,
            file=inline_pic(),
            buttons=paginate_modules(0, HELP, "help"),
        )
    except Exception as ex:
        LOGS.exception(ex)
        try:
            await event.reply(get_string("help_2").format(HNDLR))
        except Exception:
            pass

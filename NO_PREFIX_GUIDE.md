# How to Use Commands Without Prefix

Ultroid supports using commands without any prefix (like `.` or `/`). You can set the handler to a space or "NO_HNDLR" to enable this feature.

## Method 1: Using Database Command (Easiest)

In any chat with your bot, use:
```
.setvar HNDLR  
```
(Just send a space after `HNDLR`)

Or:
```
.setvar HNDLR NO_HNDLR
```

Then restart your bot.

---

## Method 2: Using Assistant Bot Settings

1. Start your assistant bot: `/start`
2. Click on **Settings ⚙️**
3. Click on **Features**
4. Click on **Handler/ Trigger**
5. Send a **single space** ` ` (just press spacebar)
6. Done!

**Note:** The UI might not accept a space, so Method 1 is more reliable.

---

## Method 3: Direct Database Access

If you have MongoDB access:

```python
# In Python console or script
from pyUltroid.startup._database import UltroidDB

udB = UltroidDB()
udB.set_key("HNDLR", " ")  # Set to space
# OR
udB.set_key("HNDLR", "NO_HNDLR")  # Set to NO_HNDLR
```

---

## Method 4: Environment Variable (Before First Run)

Add to your `.env` file:
```
HNDLR= 
```
(Just a space after the `=`)

---

## After Setting

Once set, you can use commands **without any prefix**:

**Before:**
- `.ping`
- `.alive`
- `.help`

**After:**
- `ping`
- `alive`
- `help`

---

## Important Notes

⚠️ **Warning:** Using commands without prefix means:
- Commands will trigger on **every message** that matches the command name
- This can cause conflicts with normal conversation
- Example: If someone says "ping" in chat, it will trigger the ping command!

💡 **Recommendation:** 
- Use this feature **only in private chats** or **specific groups** where you control the conversation
- Or use a **very unique prefix** like `!` or `$` instead of removing it completely

---

## Revert to Default

To go back to using `.` as prefix:

```
.setvar HNDLR .
```

Or remove the variable:
```
.delvar HNDLR
```

---

## For Multiple Clients

Each client can have its own HNDLR setting. Set it individually for each client using the `.setvar` command in that client's chat.


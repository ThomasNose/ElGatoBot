import settings
from utils.connect_db import connect_db

async def suggest(interaction, context):
    """"
        This function allows users to make suggestions.
    """

    userid = interaction.user.id
    guildid = interaction.guild.id
    if len(context)>500:
        context = context[0:499] 
    else:
        context = context

    conn = connect_db(settings.POSTGRES_LOGIN_DETAILS)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO user_suggestions \
                SELECT '{userid}', '{guildid}', '{context}'")
    conn.commit()
    conn.close
    return (await interaction.response.send_message("Suggestion submitted"))
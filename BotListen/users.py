from utils.connect_db import connect_db
import pandas as pd
import settings

postgres = settings.POSTGRES_LOGIN_DETAILS


def user_update(users):
    conn = connect_db(postgres)
    cur = conn.cursor()
    # Prepare a string to store user information
    user_info = []

    for member in users:
        # Append user information as a dictionary
        user_info.append({
            "userid": str(member.id).strip(),
            "username": member.name,
            "displayname": member.display_name,
            "created_at": member.created_at
        })

    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(user_info, columns=["userid", "username", "displayname", "created_at"])

    # Assuming your DataFrame columns match your table columns
    columns = ','.join(df.columns)

    # Generate placeholders for the query
    placeholders = ','.join(['%s'] * len(df.columns))

    # Construct the SQL query
    query = f'INSERT INTO discordusers ({columns}) VALUES ({placeholders}) \
            ON CONFLICT (userid) DO NOTHING'

    # Execute the query
    data = df.to_records(index=False).tolist()
    cur.executemany(query, data)
    conn.commit()

    cur.execute("with dupes as( select id, row_number() over (partition by userid) as rown from discordusers)\
                delete from discordusers where id in (select id from dupes where rown != 1)")

    conn.commit()
    conn.close()
    # Send user information as a message
    #await interaction.send(user_info)
    
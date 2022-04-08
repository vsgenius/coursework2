import psycopg2


def create_db(user_id):
        try:
            connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres")
            cursor = connection.cursor()
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS vk_bot_{user_id}(
                userid TEXT PRIMARY KEY); """)
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            print(error)
        finally:
            if connection:
                cursor.close()
                connection.close()

def check_db(user, user_id):
        try:
            connect = psycopg2.connect(user="postgres",
                                          password="postgres",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="postgres")
            cursor = connect.cursor()
            query = f"SELECT userid from vk_bot_{user} where userid ='{user_id}'"
            cursor.execute(query)
            result = cursor.fetchall()
            if result != []:
                return False
            else:
                return True
        except (Exception, psycopg2.Error) as error:
            print(error)
        finally:
            if connect:
                cursor.close()
                connect.close()

def update_db(user, user_id):
        try:
            connection = psycopg2.connect(user="postgres",
                                          password="postgres",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="postgres")
            cursor = connection.cursor()
            query = f"INSERT INTO vk_bot_{user} (userid) VALUES ({user_id})"
            cursor.execute(query)
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            print(error)
        finally:
            if connection:
                cursor.close()
                connection.close()

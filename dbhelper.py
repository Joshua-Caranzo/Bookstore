from mysql.connector import connect

def db_connect()->object:
    return connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="bookstoredb"
    )
    
def doProcess(sql:str)->bool:
    db:object = db_connect()
    cursor:object = db.cursor()
    cursor.execute(sql)
    db.commit()
    return True if cursor.rowcount>0 else False
    
def getProcess(sql:str)->list:
    db:object = db_connect()
    cursor:object = db.cursor(dictionary=True)
    cursor.execute(sql)
    return cursor.fetchall()

def getall(table:str)->list:
    sql:str = f"SELECT * FROM `{table}`"
    return getProcess(sql)

def getrecord(table: str, **kwargs) -> list:
    try:
        params = list(kwargs.items())
        flds = list(params[0])
        sql = f"SELECT * FROM `{table}` WHERE `{flds[0]}`='{flds[1]}'"
        return getProcess(sql)
    except Exception as e:
        print(f"Error in getrecord: {e}")
        return []

def getuser(table:str,**kwargs)->list:
    params:list = list(kwargs.items())
    flds:list = list(params)
    sql:str = f"SELECT * FROM `{table}` WHERE `{flds[0][0]}`='{flds[0][1]}' AND `{flds[1][0]}`='{flds[1][1]}'"
    return getProcess(sql)

def addrecord(table:str,**kwargs)->bool:
    flds:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    vals = [int(val) if isinstance(val, bool) else val for val in vals]
    fld:str = "`,`".join(flds)
    val = "','".join(map(str, vals))  # Ensure all values are converted to strings
    sql:str = f"INSERT INTO `{table}`(`{fld}`) values('{val}')"
    print(sql)
    return doProcess(sql)

def updaterecord(table:str,**kwargs)->bool:
    flds:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    fld:list = []
    for i in range(1,len(flds)):
        fld.append(f"`{flds[i]}`='{vals[i]}'")
    params:str = ",".join(fld)
    sql:str = f"UPDATE `{table}` SET {params} WHERE `{flds[0]}`='{vals[0]}'"
    print(sql)
    return doProcess(sql)
    
def deleterecord(table:str,**kwargs)->bool:
    params:list = list(kwargs.items())
    flds:list = list(params[0])
    sql:str = f"DELETE FROM `{table}` WHERE `{flds[0]}`='{flds[1]}'"
    return doProcess(sql)

def mark_customer_inactive(customer_id: int) -> bool:
    sql = f"UPDATE `customers` SET `isActive` = FALSE WHERE `id` = {customer_id}"
    return doProcess(sql)

def get_active_customers() -> list:
    sql = "SELECT * FROM `customers` WHERE `isActive` = TRUE"
    return getProcess(sql)

def get_highest_selling_books(isbn_list):
    sql = f"""
        SELECT * FROM `items`
        WHERE `isbn` IN ({', '.join(map(str, isbn_list))})
        ORDER BY `qty` DESC
        LIMIT 5
    """  
    highest_selling_books = getProcess(sql)
    return highest_selling_books

def get_user_cart_items(user_id: int) -> list:
    try:
        # Construct the SQL query to retrieve cart items for the user
        sql = f"""
            SELECT items.*, cart.quantity
            FROM items
            JOIN cart ON items.id = cart.item_id
            WHERE cart.cust_id = {user_id}
        """
        
        # Execute the query and return the result
        return getProcess(sql)
    except Exception as e:
        print(f"Error in get_user_cart_items: {e}")
        return []

def get_customer_name(user_id: int) -> str:
    # Construct the SQL query to retrieve the customer's name
    sql = f"SELECT name FROM customers WHERE id = {user_id}"

    # Execute the query and return the result
    result = getProcess(sql)
    return(result)

def get_customer_details(user_id: int) -> dict:
    try:
        # Assuming you have a 'customers' table with columns like 'id', 'name', 'email', 'address', etc.
        sql = f"SELECT * FROM `customers` WHERE `id` = {user_id}"
        customer_details = getProcess(sql)

        # Check if customer details are found
        if customer_details:
            return customer_details[0]  # Assuming there is only one customer with the given ID
        else:
            return {}  # Return an empty dictionary if customer details are not found

    except Exception as e:
        print(f"Error in get_customer_details: {e}")
        return {}

def calculate_total_items(user_id: int) -> int:
    sql = f"""
        SELECT SUM(quantity) AS total_items
        FROM cart
        WHERE cust_id = {user_id}
    """
    result = getProcess(sql)
    return result[0]['total_items'] if result else 0

def calculate_total_price(user_id: int) -> float:
    sql = f"""
        SELECT SUM(items.price * cart.quantity) AS total_price
        FROM cart
        JOIN items ON cart.item_id = items.id
        WHERE cart.cust_id = {user_id}
    """
    result = getProcess(sql)
    return result[0]['total_price'] if result else 0.0

def get_customer(user_id: int):
    try:
        # Construct the SQL query
        sql = f"SELECT c.* FROM customers AS c LEFT JOIN users AS u ON u.email = c.email WHERE u.id = {user_id}"

        # Execute the SQL query and get the result
        result = getProcess(sql)

        # Check if there's a result
        if result:
            # You can return the entire customer information
            return result[0]
        else:
            # Return None or any other value indicating no customer found
            return None

    except Exception as e:
        print(f"Error in get_customer: {e}")
        return None

def get_order_history(user_id)->list:
    try:
        # Assuming you have a 'orders' table with columns like 'id', 'customer_id', 'total_price', 'created_at', etc.
        # And an 'order_items' table with columns like 'order_id', 'item_id', 'quantity', 'subtotal', etc.

        # Fetch order history from the database
        sql = f"""
            SELECT o.id AS order_id, o.total_price, o.created_at, o.shipping_address, i.title,i.isbn, i.price , i.author, oi.quantity, oi.subtotal, o.created_at
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN items i ON oi.item_id = i.id
            WHERE o.customer_id = {user_id}
            ORDER BY o.created_at DESC
        """
        order_history = getProcess(sql)

        # Format the datetime in a user-friendly way if needed
        for order in order_history:
            order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        return order_history

    except Exception as e:
        print(f"Error in get_order_history: {e}")
        return []

def search_items(search_query: str) -> list:
    sql = f"""
        SELECT *
        FROM `items`
        WHERE `title` LIKE '%{search_query}%'
            OR `author` LIKE '%{search_query}%'
            OR `isbn` LIKE '%{search_query}%'
            OR `genre` LIKE '%{search_query}%'
            OR `type` LIKE '%{search_query}%'
            OR `price` LIKE '%{search_query}%'
    """
    search_result = getProcess(sql)

    return search_result

def search_customers(search_query: str) -> list:
    sql = f"""
        SELECT *
        FROM `customers`
        WHERE `name` LIKE '%{search_query}%'
            OR `email` LIKE '%{search_query}%'
            OR `address` LIKE '%{search_query}%'
    """
    search_result = getProcess(sql)

    return search_result

def change_password(user_id: int, password: str):
    sql = f"UPDATE `users` SET `password` = '{password}' WHERE `id` = {user_id}"
    success = getProcess(sql)
    if success:
        # Password change successful!
        return True
    else:
        # Password change failed!
        return False

#print(getrecord("student",idno='0002'))
#print(getall("student"))
#updaterecord('student',idno='0004',lastname='foxtrot',firstname='gold',course='bscs',level='3')
from typing import Union
from fastapi import FastAPI, Body
from typing import Dict
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import arrow
import pydash
import re


import mysql.connector

#mysql connection
connection = mysql.connector.connect(
    host="38.242.144.79",
    user="anandhas",
    password="anandhas",
    database="anandhas"
)



cursor = connection.cursor()


import uvicorn
import sys
import os


# TODO, to make this flexible when Vite change their port#, i.e. auto track port allowed list
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:4242",
    "http://localhost:5173",
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://127.0.0.1:4242",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:80",
    "http://127.0.0.1:8080",
]

# with open('pid.txt', 'w') as f:
#     f.write(str(os.getpid()))

# def setPort():
#     p = 4242
#     try:
#         p = sys.argv[1]
#     except:
#         print("error with sys.argv, assigned default port: 4242")
#     return p

app = FastAPI()
# port = setPort()


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'])

def process_bill(menu, bill):
    items = {}
    for itr in bill:
        item = json.loads(pydash.collections.filter_(menu, lambda x:x['menu_id'] == itr['iid'])[0]['items'])
        for itr1 in item:
            itr1['base'] = itr1['qty']
            itr1['qty'] = itr['qty']
            itr1['total'] = '{} {}'.format(round(float(''.join(char for char in itr1['base'] if not char.isalpha())) * float(itr['qty']), 2),
                                           ''.join(char for char in itr1['base'] if char.isalpha()))

        items[itr['iid']] = item

    return items

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/update_staff")
async def update_staff(staff_details: Dict = Body(...)):
    try:
        staff_details = jsonable_encoder(staff_details)
        statement = "update staff set sname = '{}' where sid = {}".format(staff_details['sname'], staff_details['sid'])
        cursor.execute(statement)
        connection.commit()
        return "Staff Updated!"
    except Exception as e:
        return "Update failed"



@app.get("/get_staff/{sid}")
async def get_staff(sid):
    if sid == "-1":
        statement = "select * from staff"
        cursor.execute(statement)

        result = cursor.fetchall()

        data = []
        if result:
            for itr in result:
                data.append(dict(zip(['sid', 'sname', 'department'], itr)))
            return data
        else:
            return "Student not found"

    else:
        statement = "select * from staff where sid = {}".format(sid)
        cursor.execute(statement)

        result = cursor.fetchall()

        data = []
        if result:
            for itr in result:
                data.append(dict(zip(['sid', 'sname', 'department'], itr)))
            return data
        else:
            return "Student not found"


@app.delete("/delete_staff/{sid}")
async def delete_staff(sid):
    try:
        statement = "delete from staff where sid = {}".format(sid)
        cursor.execute(statement)
        connection.commit()
        return "Staff Deleted!"
    except Exception as e:
        return "Staff not deleted"


@app.post("/create_staff")
async def create_staff(staff_details:Dict = Body(...)):
    try:
        staff_details = jsonable_encoder(staff_details)
        statement = "insert into staff (sname, department) values ('{}', '{}')".format(staff_details['name'], staff_details['department'])
        cursor.execute(statement)
        connection.commit()
        return "Staff Created"

    except Exception as e:
        print(e)


@app.post("/create_menu")
async def create_menu(menu_details:Dict = Body(...)):
    try:
        menu_details = jsonable_encoder(menu_details)
        statement = "insert into menu (menu_name) values ('{}')".format(menu_details['name'])
        cursor.execute(statement)
        connection.commit()
        return "Menu Created"

    except Exception as e:
        print(e)


@app.get("/get_menu/{mid}")
async def get_menu(mid):
    if mid == "-1":
        statement = "select * from menu"
        cursor.execute(statement)

        result = cursor.fetchall()

        data = []
        if result:
            for itr in result:
                data.append(dict(zip(['mid', 'name'], itr)))
            return data
        else:
            return "Menu not found"

    else:
        statement = "select * from menu where mid = {}".format(mid)
        cursor.execute(statement)

        result = cursor.fetchall()

        data = []
        if result:
            for itr in result:
                data.append(dict(zip(['mid', 'name'], itr)))
            return data
        else:
            return "Menu not found"


@app.post("/update_menu")
async def update_menu(menu_details: Dict = Body(...)):
    try:
        menu_details = jsonable_encoder(menu_details)
        statement = "update menu set menu_name = '{}' where mid = {}".format(menu_details['name'],menu_details['mid'])
        cursor.execute(statement)
        connection.commit()
        return "Menu Updated!"
    except Exception as e:
        print(e)


@app.delete("/delete_menu/{mid}")
async def delete_menu(mid):
    try:
        statement = "delete from menu where mid = {}".format(mid)
        cursor.execute(statement)
        connection.commit()
        return "Menu Deleted!"
    except Exception as e:
        return "Menu not deleted"


@app.post("/create_menu_item")
async def create_menu_item(menu_items:Dict = Body(...)):
    try:
        menu_items = jsonable_encoder(menu_items)
        inc = 1
        for itr in menu_items['menu_items']:
            itr['iid'] = inc
            inc += 1

        str_menu_items = json.dumps(menu_items['menu_items'])
        statement = "select * from menu_items where iid = {}".format(menu_items['menu_id'])
        cursor.execute(statement)
        menu = cursor.fetchall()
        if menu:
            statement = "update menu_items set menu_items = '{}' where iid = {}".format(str_menu_items, menu_items['menu_id'])
            cursor.execute(statement)
            connection.commit()
            return "Menu Item Updated!"
        else:
            statement = "insert into menu_items values ({}, '{}')".format(
                menu_items['menu_id'],str_menu_items
            )
            cursor.execute(statement)
            connection.commit()
            return "Menu Item Added!"

    except Exception as e:
        return "Menu item error"


@app.get("/get_menu_items/{mid}")
async def get_menu_items(mid):
    try:
        statement = "select * from menu_items where iid = {}".format(mid)
        cursor.execute(statement)
        menu_items = cursor.fetchall()
        if menu_items:
            return json.loads(menu_items[0][1])
        else:
            return []
    except Exception as e:
        return "Error on menu items"


@app.post("/save_bill")
async def save_bill(bill_items:Dict= Body(...)):
    try:
        bill_items = jsonable_encoder(bill_items)


        statement = "select * from menu_items"
        cursor.execute(statement)
        menu_items = cursor.fetchall()
        menu_items_list = [ dict(zip(['menu_id', 'items'], itr)) for itr in menu_items]

        total_items = process_bill(menu_items_list,bill_items['items'])

        statement = "insert into bills (name, mobile, address, bill_no, b_staff, d_staff, o_date, d_date, items, items1) values " \
                    "('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            bill_items['name'], bill_items['mobile'], bill_items['address'], bill_items['bill_no'],bill_items['billing_staff'],
            bill_items['delivery_staff'], bill_items['o_date'], bill_items['d_date'],json.dumps(bill_items['items']),json.dumps(total_items)
        )
        cursor.execute(statement)
        connection.commit()
        return "Bill Saved!"
    except Exception as e:
        return "Error on bill"


@app.get("/get_bills/{bid}")
async def get_bills(bid):
    try:
        if bid == '-1':
            statement = "select bid, name, mobile, address, bill_no, s.sname as b_staff, s1.sname as d_staff, o_date,d_date,items,items1 from bills as b inner join staff as s on b.b_staff = s.sid inner join staff as s1 on s1.sid = b.d_staff;"
            cursor.execute(statement)
            data = cursor.fetchall()
            bill_data = []

            if data:
                for itr in data:
                    itr_list = list(itr)
                    itr_list[9] = json.loads(itr[9])
                    itr_list[10] = json.loads(itr[10])
                    bill_data.append(dict(zip(('bid','name','mobile','address','bill_ref', 'b_staff','d_staff','o_date','d_date', 'items', 'items1'),itr_list)))
            return bill_data
        else:
            statement = "select bid, name, mobile, address, bill_no, s.sname as b_staff, s1.sname as d_staff, o_date,d_date,items,items1 from bills as b inner join staff as s on b.b_staff = s.sid inner join staff as s1 on s1.sid = b.d_staff where bid = {}".format(bid)
            cursor.execute(statement)
            data = cursor.fetchall()
            bill_data = []
            if data:
                for itr in data:
                    itr_list = list(itr)
                    itr_list[9] = json.loads(itr[9])
                    itr_list[10] = json.loads(itr[10])
                    bill_data.append(dict(zip(('bid','name','mobile','address','bill_ref', 'b_staff','d_staff','o_date','d_date', 'items', 'items1'),itr_list)))
            return bill_data

    except Exception as e:
        return "Bill Not found!"


@app.get("/get_bill_details/{bid}")
async def get_bill_details(bid):
    try:
        statement = "select * from bills where bid = {}".format(bid)
        cursor.execute(statement)
        data = cursor.fetchall()

        res = list(data[0])
        res[9] = json.loads(res[9])
        res[10] = json.loads(res[10])

        menu_list = res[9]
        menu_items_list = res[10]

        out = []
        for menu_id,menu in enumerate(menu_list):
            menu_dict = {}
            menu_dict = {
                'id': menu['sid'],
                'name': menu['item'],
                'qty': menu['qty']
            }
            items_list = []
            for item in menu_items_list[str(menu['iid'])]:
                item_dict = {}
                items_list.append({
                    "data" : {
                        'id': item['iid'],
                        'name': item['item'],
                        'qty': item['qty'],
                        'total': item['total']
                    }
                })
            out.append({
                'data': menu_dict,
                'children': items_list
            })
        return out

    except Exception as e:
        return "Error on Bill details"


@app.get("/get_report_data/{bid}")
async def get_report_data(bid):
    try:
        statement = "select * from bills where bid = {}".format(bid)
        cursor.execute(statement)
        data = cursor.fetchall()

        res = list(data[0])
        res[9] = json.loads(res[9])
        res[10] = json.loads(res[10])

        menu_list = res[9]
        menu_items_list = res[10]



        out = []
        sno = 1
        for itr in menu_list:
            itr_list = []
            header = {
                "rowSpan": len(menu_items_list[str(itr['iid'])]),
                "content": itr['item'],
                "styles": {
                    "halign": "center",
                    "valign": "middle"
                }
            }
            for idx,itr1 in enumerate(menu_items_list[str(itr['iid'])]):
                if idx == 0:
                    itr_list = [header,sno, itr1['item'], itr1['qty'], itr1['base'], itr1['total']]
                    sno += 1
                    out.append(itr_list)
                else:
                    itr_list = [sno,itr1['item'], itr1['qty'], itr1['base'], itr1['total']]
                    sno += 1
                    out.append(itr_list)

        out.insert(0, [
            {
                "rowSpan": 1,
                "content": '',
                "styles": {
                    "halign": "center",
                    "valign": "center",
                    "fontStyle": 'bold',
                }
            },
            {
                "rowSpan": 1,
                "content": 'SNO',
                "styles": {
                    "halign": "center",
                    "valign": "middle",
                    "fontStyle": 'bold',
                    "fillColor": [224, 202, 60]
                }
            },
            {
                "rowSpan": 1,
                "content": 'ITEM',
                "styles": {
                    "halign": "center",
                    "valign": "middle",
                    "fontStyle": 'bold',
                    "fillColor": [224, 202, 60]
                }
            },
            {
                "rowSpan": 1,
                "content": 'QTY',
                "styles": {
                    "halign": "center",
                    "valign": "middle",
                    "fontStyle": 'bold',
                    "fillColor": [224, 202, 60]
                }
            },
            {
                "rowSpan": 1,
                "content": 'UNIT',
                "styles": {
                    "halign": "center",
                    "valign": "middle",
                    "fontStyle": 'bold',
                    "fillColor": [224, 202, 60]
                }
            },
            {
                "rowSpan": 1,
                "content": 'TOTAL',
                "styles": {
                    "halign": "center",
                    "valign": "middle",
                    "fontStyle": 'bold',
                    "fillColor": [224, 202, 60]
                }
            }
            ])
        return out

    except Exception as e:
        print("Error on report")


@app.get("/get_bill_no")
async def get_bill_no():
    try:

        statement = "select * from bills where o_date = '{}'".format(arrow.now(tz='Asia/Calcutta').format("DDMMYYYY"))
        cursor.execute(statement)
        bills = cursor.fetchall()

        if bills:
            return len(bills) + 1
        else:
            return 1
    except Exception as e:
        print(e)


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=4242)
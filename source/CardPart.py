import pymysql
import logging

def AddCard(conn,CardNum,Name,Dept,Type,flag):
    #既可以增加借书证，也可以修改原借书证信息
    #具体可以参考图书入库部分
    #flag=0代表增加，flag=1代表修改
    #修改功能是为了考虑到可能会更改单位之类的（比如转专业？)
    if CardNum=="" or Name=="" or Dept=="" or Type=="":
        return "不能有空项"
    try:
        cursor=conn.cursor()
        sql="select * from card where cnum=%s"
        cursor.execute(sql,CardNum)
        result=cursor.fetchone()
        #首先排除两个特殊情况:增加一个已经存在的证，或者是修改一个不存在的证
        if result is None :
            if flag==1:
                return "借书证不存在，修改失败"
        elif flag==0:
            return "此借书证已存在，增加失败"

        if flag==0:
            sql="insert into card values(%s,%s,%s,%s,0)"
            cursor.execute(sql,(CardNum,Name,Dept,Type))
            conn.commit()
            return 1
        else:
            sql="update card set name=%s,department=%s,type=%s where cnum=%s"
            cursor.execute(sql,(Name,Dept,Type,CardNum))
            conn.commit()
            return 2
    except Exception as e:
        conn.rollback()
        return e

def DeleteCard(conn,CardNum):
    if CardNum=="":
        return "卡号不能为空"
    try:
        cursor=conn.cursor()
        sql="select * from card where cnum=%s"
        cursor.execute(sql,CardNum)
        result=cursor.fetchone()
        if result is None:
            return "借书证不存在"
            
        sql="delete from card where cnum=%s"
        cursor.execute(sql,CardNum)
        conn.commit()
        return 1
    except Exception as e:
        conn.rollback()
        return e

import pymysql
import logging
import datetime

def Return(conn,CardNum,BookNum):
    if(CardNum=="" or BookNum==""):
        return "不能为空"
    try:
        cursor=conn.cursor()
        sql="select numbers from card where cnum=%s"
        cursor.execute(sql,CardNum)
        num_=cursor.fetchone()
        num=num_[0]-1
        sql="select bname,collection,rtime from book natural join borrow where bnum=%s and cnum=%s"
        cursor.execute(sql,(BookNum,CardNum))
        result=cursor.fetchone()
        if result is None:
            return "您尚未借阅此书，因此无法还书"
        else:
            name=result[0]
            collection=result[1]
            r_time=result[2]
            collection+=1
            n_time=datetime.datetime.now()
            if(n_time>r_time):
                late=1
            else:
                late=0
            sql="update book set collection=%s where bnum=%s"
            cursor.execute(sql,(collection,BookNum))
            sql="delete from borrow where bnum=%s and cnum=%s"
            cursor.execute(sql,(BookNum,CardNum))
            sql="update card set numbers=%s where cnum=%s"
            cursor.execute(sql,(num,CardNum))
            conn.commit()
        return (name,late)
    except Exception as e:
        logging.exception(e)
        conn.rollback()
        return e
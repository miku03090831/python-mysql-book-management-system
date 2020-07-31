import pymysql
import logging
import datetime

def ShowList(conn,CardNum):
    if(CardNum==""):
        return "借书证号不能为空"
    try:
        cursor=conn.cursor()
        sql="select * from card where cnum=%s"
        cursor.execute(sql,CardNum)
        result=cursor.fetchone()
        #要看输入的卡号是不是有效的
        if result is None:
            return "无效的借书证号"
        
        sql="select bnum,bname,btime,rtime,times from book natural join borrow where cnum=%s"
        cursor.execute(sql,CardNum)
        result=cursor.fetchall()
        return result


    except Exception as e:
        logging.exception(e)
        return e

def Borrow(conn,CardNum,BookNum):
    if(CardNum=="" or BookNum==""):
        return "不能为空"
    try: 
        cursor=conn.cursor()
        sql="select times,rtime from borrow where cnum=%s and bnum=%s"
        cursor.execute(sql,(CardNum,BookNum))
        times=cursor.fetchone()
        if times is None:
            pass
        elif times[0]==1:
            r_time=times[1]
            r_time=r_time+datetime.timedelta(days=30)
            r_time=r_time.strftime("%Y-%m-%d %H:%M:%S")
            sql="update borrow set times=0,rtime=%s where cnum=%s and bnum=%s"
            cursor.execute(sql,(r_time,CardNum,BookNum))
            conn.commit()
            return (1,r_time)
        elif times[0]==0:
            return "续借次数已达上限"
        #前面要判断是否是续借，允许续借一次
        #判断完不是续借之后，还要判断是否借书数量已经达到上限
        sql="select numbers from card where cnum=%s"
        cursor.execute(sql,CardNum)
        result=cursor.fetchone()
        if result[0]>=10:
            return "借书数量超出上限"
        else:
            numbers=result[0]+1
        #
        sql="select bname,collection from book where bnum=%s"
        cursor.execute(sql,BookNum)
        result=cursor.fetchone()
        #此处的判断逻辑其实不是很好。。。先判断了是否超出上限，再判断的书是否存在。可能会导致用户为了借一本不存在的书，先去还书，回来才发现根本没有这本书
        if result is None:
            return "借书失败，书号不存在"
        if result[1]!=0:
            #借书成功
            bname=result[0]
            collection=result[1]-1
            sql="update book set collection=%s where bnum=%s"
            cursor.execute(sql,(collection,BookNum))
            b_time= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            r_time=(datetime.datetime.now()+datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            sql="insert into borrow values(%s,%s,%s,%s,1)"
            cursor.execute(sql,(CardNum,BookNum,b_time,r_time))
            sql="update card set numbers=%s where cnum=%s"
            cursor.execute(sql,(numbers,CardNum))
            conn.commit()
            return (0,r_time,bname)
        else:
            #借书失败，因为库存不足
            #关于如何返回最早的还书时间这一点明天再说
            #查到的方法中，最起码可以把两个表join然后比较
            #但是我比较想用聚合函数来做，因为简单（datatime类型的数据不知道能不能用聚合函数）答案是能！
            sql="select min(rtime) from borrow where bnum=%s"
            cursor.execute(sql,BookNum)
            result=cursor.fetchone()
            r_time=result[0]
            r_time=r_time.strftime('%Y-%m-%d %H:%M:%S')
            return (2,r_time)
            
    except Exception as e:
        logging.exception(e)
        conn.rollback()
        return e
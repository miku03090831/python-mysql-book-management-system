import pymysql
import logging

def QueryBook(conn,para1,para2,index):
    if para1=="" or para2=="":
        return "输入不能为空"
    cursor=conn.cursor()
    ##目前进度：单值查询已做完，区间查询没有做。并且最后return的是一个比较乱的tuple。在show()函数中应该要一层一层的处理
    try:
        if index==0:
            sql="select bnum,bclass,bname,publisher,year,author,price,collection from book where bclass=%s"
        elif index==1:
            sql="select bnum,bclass,bname,publisher,year,author,price,collection from book where bname=%s"
        elif index==2:
            sql="select bnum,bclass,bname,publisher,year,author,price,collection from book where publisher=%s"
        elif index==4:
            sql="select bnum,bclass,bname,publisher,year,author,price,collection from book where author=%s"
        elif index==3:
            y1=int(para1)
            y2=int(para2)
            sql="select bnum,bclass,bname,publisher,year,author,price,collection from book where year>%s and year<%s"
        elif index==5:
            p1=float(para1)
            p2=float(para2)
            sql="select bnum,bclass,bname,publisher,year,author,price,collection from book where price>%s and price<%s"

        try:
            if index==0 or index==1 or index==2 or index==4:
                cursor.execute(sql,para1)
            elif index==5:
                cursor.execute(sql,(p1,p2))
            else:
                cursor.execute(sql,(y1,y2))
            
            conn.commit()
            result=cursor.fetchall()
            return result
        except Exception as e:
            conn.rollback()
            return e

    except Exception as e:
        return e
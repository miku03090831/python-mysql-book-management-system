import pymysql
import logging


def AddOne(conn,BookNum,ClassOfBook,BookName,Publisher,Year,Author,Price,flag,num):
    cursor=conn.cursor()

    try:
        #获取total
        sql="select total from book"
        if(BookNum=="" or ClassOfBook=="" or BookName=="" or Publisher=="" or Year=="" or Author=="" or Price==""):
            return "不能有空项"
        Year=int(Year)
        Price=float(Price)
        cursor.execute(sql)
        total=cursor.fetchone()
        if total is None:#目前还没有书，total为0  
            total=0
        else:
            total=total[0]

        #获取collection
        sql="select collection from book where bnum=%s"
        cursor.execute(sql,BookNum)
        collection=cursor.fetchone()
    except Exception as e:
        conn.rollback()
        logging.exception(e)
        return e

    if  collection is None:#书不存在，新增添一条记录
        if(flag==1):#试图在书不存在的情况下直接修改信息，操作失败
            return "此书尚未被收录，修改失败"
        collection=num
        total+=num
        sql="insert into book values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        try:
            cursor.execute(sql,(BookNum,ClassOfBook,BookName,Publisher,Year,Author,Price,total,collection))
            sql="update book set total=%s"
            cursor.execute(sql,(total))
            conn.commit()
            return (total,collection)
        except Exception as e:
            logging.exception(e)
            conn.rollback()
            return e

    else: #书已经存在，根据flag，修改信息或者是增加一本
        collection=collection[0]
        try:
            old_sql="select bnum,bclass,bname,publisher,year,author,price from book where bnum=%s"
            cursor.execute(old_sql,BookNum)
            old_record=cursor.fetchone() #取出原记录
            sql="update book set bclass=%s,bname=%s,publisher=%s,year=%s,author=%s,price=%s where bnum=%s"#在事务内更新记录，然后再读取出来
            cursor.execute(sql ,(ClassOfBook,BookName,Publisher,Year,Author,Price,BookNum))
            
            new_sql="select bnum,bclass,bname,publisher,year,author,price from book where bnum=%s"
            cursor.execute(new_sql ,BookNum)
            new_record=cursor.fetchone() #取出新记录
            if flag==0:#不修改，只添加
                #比对新老两条记录，如果一样则把数量加一，不一样则报错
                if old_record==new_record:
                    total+=num
                    collection+=num
                    sql="update book set total=%s,collection=%s where bnum=%s"
                    cursor.execute(sql ,(total,collection,BookNum))
                    sql="update book set total=%s"
                    cursor.execute(sql ,(total))
                    conn.commit()
                    return (total,collection)
                else: 
                    #应该会报错
                    conn.rollback()
                    return "与记录中信息不一致！"
            else:
                #要修改信息了
                conn.commit()
                return "修改成功"
        except Exception as e:
            logging.exception(e)
            conn.rollback()
            return e

def AddBatch(conn,file_addr):
    success_cnt=0
    fail_cnt=0
    succeed_list=[]
    fail_list=[]
    try:
        with open(file_addr,"r",encoding="utf8") as f:
            for line in f.readlines():
                str1=line.strip('\n')#用来添加到列表里，保持原始格式
                str2=line.strip('()\n').split(',')#用来取出各个属性值
                if len(str2)!=8:
                    fail_list.append(str1)
                    break
                BookNum=str2[0].strip()
                ClassOfBook=str2[1].strip()
                BookName=str2[2].strip()
                Publisher=str2[3].strip()
                Year=int(str2[4].strip())
                Author=str2[5].strip()
                Price=float(str2[6].strip())
                num=int(str2[7].strip())
                result=AddOne(conn,BookNum,ClassOfBook,BookName,Publisher,Year,Author,Price,0,num)
                if type(result)==type(()):
                    succeed_list.append(str1)
                    success_cnt+=num
                else:
                    fail_list.append(str1)
                    fail_cnt+=num

        
        with open("succeed_log.txt","a") as s_f:
            for line in succeed_list:
                s_f.write(line)
                s_f.write("\n")

        # 以下功能已经不再需要
        # 已经实现了代替功能
        # with open("fail_file.txt","w") as f_f:
        #     for line in fail_list:
        #         f_f.write(line)
        return (len(succeed_list),success_cnt,len(fail_list),fail_cnt,fail_list)
    except Exception as e:
        logging.exception(e)
        return e
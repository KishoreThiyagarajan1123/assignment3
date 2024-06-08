
import easyocr
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import pandas as pd
import numpy as nd
import re
import io
import sqlite3


def totext(imgs):

    img= Image.open(imgs)
    imgarr= nd.array(img)
    reader = easyocr.Reader(['en'])
    text=reader.readtext(imgarr,detail=0)
    return text,img



def toinsert(text):

    edict={"Name":[],"Designation":[],"Company_Name":[],"Contact":[],"Email":[],'Website':[],"Address":[],
          "Pincode":[]}

    edict["Name"].append(text[0])
    edict["Designation"].append(text[1])
    for i in range(2,len(text)):
      if re.findall(r'^[+]',text[i]) or (re.findall(r'^\d{3}-\d{3}-\d{4}$',text[i])):
        edict["Contact"].append(text[i])
      elif (re.findall(r'[\w\.-]+@[\w\.-]+',text[i])):
        edict["Email"].append(text[i])
      elif re.match(r'^WWW(?=.*\.com)', text[i])or 'wwW' in text[i] or '.com' in text[i] or 'Www' in text[i] or 'wWw' in text[i] or 'WWW' in text[i] or 'www' in text[i]:
        edict["Website"].append(text[i])
      elif re.search(r'(\d{6})|\b(\d{3}\s*\d{3})\b', text[i]):
        edict["Pincode"].append(text[i])
      elif re.findall(r'^123+\s[\w\.-]+',text[i]) or ',' in text[i]:
        edict["Address"].append(text[i])
      elif re.match('^[A-Za-z]',text[i]):
        edict["Company_Name"].append(text[i])
    return edict





st.set_page_config(layout='wide')
st.title('Extracting Bussiness Card Data With OCR')


with st.sidebar:
  select=option_menu('Main Menu',['Upload & Extracting','Delete'])


if select=='Upload & Extracting':
  imgs= st.file_uploader('upload the image',type=['png','jpg','jpeg'])

  if imgs is not None:
      st.image(imgs,width=300)


      text,input_image= totext(imgs)
      textddict=toinsert(text)


      if text:
        st.success('text is extracted')

        for key,value in textddict.items():
            if len(value)<=len(value):
              con=" ".join(value)
              textddict[key]=[con]


        df = pd.DataFrame(textddict)

        img_bytes=io.BytesIO()
        input_image.save(img_bytes,format='PNG')


        img_data=img_bytes.getvalue()
        data={"Image":[img_data]}

        df1 = pd.DataFrame(data)

        concats=pd.concat([df,df1],axis=1)

  button1=st.button('save')
  if button1:
    mydb=sqlite3.connect('bizcards2.db')
    cursor= mydb.cursor()
    mydb.commit()
    indata=concats.to_sql('bizcardetails',mydb,index=False ,if_exists='append')
    mydb.commit()
    st.success('saved successfully')
  method=st.radio('select the options',['None','perview','modify'],horizontal=True)
  if method=='None':
    pass
  elif method=='perview':
    mydb=sqlite3.connect('bizcards2.db')
    cursor= mydb.cursor()


    selectquery="SELECT * FROM bizcardetails"
    cursor.execute(selectquery)
    table=cursor.fetchall()
    mydb.commit()
    tdf=pd.DataFrame(table,columns=('NAME','DESIGNATION','COMPANY_NAME','CONTACT','EMAIL','WEBSITE','ADDRESS','PINCODE','IMAGE'))
    st.dataframe(tdf)

  elif method=='modify':
      mydb=sqlite3.connect('bizcards2.db')
      cursor=mydb.cursor()


      selectquery="SELECT * FROM bizcardetails"
      cursor.execute(selectquery)
      tables=cursor.fetchall()
      mydb.commit()
      tdfs=pd.DataFrame(tables,columns=('NAME','DESIGNATION','COMPANY_NAME','CONTACT','EMAIL','WEBSITE','ADDRESS','PINCODE','IMAGE'))


      col1,col2=st.columns(2)

      with col1:
        selectname=st.selectbox('select the name',tdfs['NAME'])

      df3=tdfs[tdfs['NAME']==selectname]
      st.dataframe(df3)

      df4=df3.copy()

      st.dataframe(df4)

      col1,col2=st.columns(2)

      with col1:
        cname=st.text_input('Name',df3['NAME'].unique()[0])
        cname1=st.text_input('Designation',df3['DESIGNATION'].unique()[0])
        cname2=st.text_input('Com_Name',df3['COMPANY_NAME'].unique()[0])
        cname3=st.text_input('Contact',df3['CONTACT'].unique()[0])
        cname4=st.text_input('Email',df3['EMAIL'].unique()[0])

        df4['NAME']=cname
        df4['DESIGNATION']=cname1
        df4['COMPANY_NAME']=cname2
        df4['CONTACT']=cname3
        df4['EMAIL']=cname4



      with col2:
        cname5=st.text_input('Website',df3['WEBSITE'].unique()[0])
        cname6=st.text_input('Address',df3['ADDRESS'].unique()[0])
        cname7=st.text_input('Pincode',df3['PINCODE'].unique()[0])
        cname8=st.text_input('Image',df3['IMAGE'].unique()[0])


        df4['WEBSITE']=cname5
        df4['ADDRESS']=cname6
        df4['PINCODE']=cname7
        df4['IMAGE']=cname8

      st.dataframe(df4)

      col1,col2=st.columns(2)

      with col1:
        button3=st.button('modify')
      if button3:
        mydb=sqlite3.connect('bizcards2.db')
        cursor=mydb.cursor()


        cursor.execute(f"delete from  bizcardetails  where NAME='{selectname}'")
        mydb.commit()


        indatas=df4.to_sql('bizcardetails', mydb,index=False ,if_exists='append')

        mydb.commit()

        st.success('modified successfully')







elif select=='Delete':
    mydb=sqlite3.connect('bizcards2.db')
    cursor=mydb.cursor()


    col1,col2=st.columns(2)
    query1='select * from bizcardetails'
    cursor.execute(query1)
    table1=cursor.fetchall()
    mydb.commit()

    names=[]
    designations=[]

    for i in table1:
      names.append(i[0])
      designations.append(i[1])

    with col1:

       name2=st.selectbox('select the name',names)

    with col2:   

       name3=st.selectbox('select the name',designations)

  
    

    


    remove=st.button('Delete')

    if remove:
      cursor.execute(f"delete from bizcardetails WHERE =NAME'{name2}' and DESIGNATION'{name3}'")
      mydb.commit()

      st.warning('DELETED')



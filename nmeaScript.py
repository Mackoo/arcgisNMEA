#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Maciek
#
# Created:     10-07-2013
# Copyright:   (c) Maciek 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os
import datetime, time,string
import sqlite3 as db

class nmeamain:
    def nmeaDict(self,nmeafile,connectionObject):
        nmeafile.seek(0)
        for line in nmeafile:
             linee=line.split(',')
             if line[3:6]=='GGA' or line[3:6]=='GGA':
                 cur=connectionObject.cursor()
                 key=linee[1][:2]+':'+linee[1][2:4]+':'+linee[1][4:6]
                 qu="""insert or ignore into nmea2GGA(utc,msl) values('"""+key+"""',0)"""
##                 arcpy.AddError(qu)
                 #QMessageBox.information(self.iface.mainWindow(), 'inff', qu)
                 cur.execute(qu)

             if line[3:6]=='GLL':
                 cur=connectionObject.cursor()
                 key=linee[5][:2]+':'+linee[5][2:4]+':'+linee[5][4:6]
                 qu="""insert or ignore into nmea2GGA(utc,msl) values('"""+key+"""',0)"""
                 #QMessageBox.information(self.iface.mainWindow(), 'inff2', qu)
                 cur.execute(qu)
        connectionObject.commit()



        nmeafile.seek(0)

        for line in nmeafile:
            if line.startswith('$'):
                try:
                    parser={'GGA':self.par_gga,'RMC':self.par_rmc,'GLL':self.par_gll}[line[3:6]]
                    query=parser(line)
##                    QMessageBox.information(self.iface.mainWindow(), 'info', query)
                    cursor=connectionObject.cursor()
                    cursor.execute(query)
                except:
##                    arcpy.AddError("cos nie dziala")
                    continue
        connectionObject.commit()



    def addLayer(self):
            ref=arcpy.SpatialReference((4326))
            output=arcpy.GetParameterAsText(1)
            arcpy.CreateFeatureclass_management(os.path.dirname(output), os.path.basename(output),"POINT",'','DISABLED','DISABLED',ref)
            arcpy.AddField_management(output,"msl","FLOAT")
            cursor=arcpy.da.InsertCursor(output,("ID","SHAPE@XY","msl"))

            cur=self.connectionObject.cursor()
            qu="""SELECT lat,lon,msl from nmea2GGA"""
            cur.execute(qu)
            fetched=cur.fetchall()
            a=0
            for f in fetched:
##                arcpy.AddError(f)
                cursor.insertRow((a,(f[1],f[0]),f[2]))
                a+=1



    def par_gga(self,line):
##        arcpy.AddError("jkestem w par_gga")
        data=[]
        data=line.split(',')
        key=data[1]
        utc=data[1][:2]+':'+data[1][2:4]+':'+data[1][4:6]
        latt=float(data[2][:2])+float(data[2][2:])/60
        ind=string.find(data[4],".")
        lonn=float(data[4][:(ind-2)])+float(data[4][(ind-2):])/60
        numsv=data[7]
        hdop=data[8]
        msl=data[9]
        geoid=data[11]
        fixstatus=data[6]
        query="""update nmea2GGA set lat="""+str(latt)+""",lon="""+str(lonn)+""",fixstatus="""+str(fixstatus)+""",numsv="""+str(numsv)+""",hdop="""+str(hdop)+""",msl="""+str(msl)+""",geoid="""+str(geoid)+""" where utc='"""+utc+"""';"""
        return query


    def par_rmc(self,line):
##        arcpy.AddError("jkestem w par_rmc")
        data=[]
        data=line.split(',')
        key=data[1]
        utc=data[1][:2]+':'+data[1][2:4]+':'+data[1][4:6]
        latt=float(data[3][:2])+float(data[3][2:])/60
        ind=string.find(data[5],".")
        lonn=float(data[5][:(ind-2)])+float(data[5][(ind-2):])/60
        speed=data[7]
        datastatus=data[2]

        query="""update nmea2GGA set lat="""+str(latt)+""",lon="""+str(lonn)+""",speed="""+str(speed)+""",datastatus='"""+str(datastatus)+"""' where utc='"""+utc+"""';"""
        return query

    def par_gll(self,line):
##        arcpy.AddError("jkestem w par_gll")
        data=[]
        data=line.split(',')
        key=data[5]
        utc=data[5][:2]+':'+data[5][2:4]+':'+data[5][4:6]
        latt=float(data[1][:2])+float(data[1][2:])/60
        ind=string.find(data[3],".")
        lonn=float(data[3][:(ind-2)])+float(data[3][(ind-2):])/60
        datastatus=data[6]
        query="""update nmea2GGA set lat="""+str(latt)+""",lon="""+str(lonn)+""",datastatus='"""+str(datastatus)+"""' where utc='"""+utc+"""';"""
        return query


    def main(self):
        try:
            nmeafile=open(arcpy.GetParameterAsText(0))
            arcpy.AddMessage(os.getcwd())
    ##    for line in nmeafile:
    ##        arcpy.AddMessage(line)
            try:
##                self.connectionObject=db.connect('C:\Users\Maciek\Documents\GIG\magisterka\STD Oszczak\praca_mag\dbnmea.sqlite')
                self.connectionObject=db.connect(':memory:')
            #QMessageBox.critical(self.iface.mainWindow(), 'info', 'connected to database')
            except:
                 arcpy.AddError("could not connect to database")


            cur=self.connectionObject.cursor()
            qu="CREATE TABLE nmea2GGA(utc datetime primary key, lat real,lon real, fixstatus integer, numsv integer, hdop real, msl real, geoid real,speed real, datastatus text)"
            cur.execute(qu)
            self.connectionObject.commit()

            self.nmeaDict(nmeafile,self.connectionObject)
            self.addLayer()
        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            arcpy.AddError(e.args[0])



if __name__ == '__main__':
    nmea=nmeamain()
    nmea.main()

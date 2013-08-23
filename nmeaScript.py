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

class nmeamain:
    def nmeaDict(self,nmeafile):

            start=time.time()
            self.nmeadict={}
            nmeafile.seek(0)

            for line in nmeafile:
                 linee=line.split(',')
                 if line[3:6]=='GGA' or line[3:6]=='RMC':
                     self.nmeadict[linee[1]]=['',0,0,0,0,0,0,0,0,0,0,0,0]
                 if line[3:6]=='GLL':
                     self.nmeadict[linee[5]]=['',0,0,0,0,0,0,0,0,0,0,0,0]
            nmeafile.seek(0)
            for line in nmeafile:
                if line.startswith('$'):
                    try:
                        parser={'GGA':self.par_gga,'RMC':self.par_rmc,'GLL':self.par_gll}[line[3:6]]
                        parser(line)
                    except:
##                        arcpy.AddMessage('blad')
                        continue

            end=time.time()

            nmeafile.close()

            self.dates=[]
            self.utc=[]
            self.lat=[]
            self.lon=[]
            self.numSV=[]
            self.hdop=[]
            self.vdop=[]
            self.pdop=[]
            self.msl=[]
            self.geoid=[]
            self.speed=[]
            self.fixstatus=[]
            self.datastatus=[]
            for keyy in self.nmeadict.keys():
##                arcpy.AddMessage(self.nmeadict[keyy][0])
                self.utc.append(self.nmeadict[keyy][0])
                self.dates.append(datetime.datetime.strptime(self.nmeadict[keyy][0],'%H:%M:%S'))
                self.numSV.append(float(self.nmeadict[keyy][3]))
                try:    self.hdop.append(float(self.nmeadict[keyy][4]))
                except:  self.hdop.append(0)

                self.lon.append(self.nmeadict[keyy][2])
                self.lat.append(self.nmeadict[keyy][1])
                self.vdop.append(float(self.nmeadict[keyy][5]))
                self.pdop.append(float(self.nmeadict[keyy][6]))
                try:    self.msl.append(float(self.nmeadict[keyy][7]))
                except: self.msl.append(0)
                try:    self.geoid.append(float(self.nmeadict[keyy][8]))
                except: self.geoid.append(0)
                self.speed.append(float(self.nmeadict[keyy][9]))
                self.fixstatus.append(int(self.nmeadict[keyy][11]))
                datastatus=0
                if self.nmeadict[keyy][12]=='A':    datastatus=1
                self.datastatus.append(datastatus)

    def addLayer(self):
            sciezka="D://GIS//schemat_MSL.shp"
            desc=arcpy.Describe(sciezka)
            ref=arcpy.SpatialReference((4326))
##            ref=desc.spatialReference.exporttostring()
            output=arcpy.GetParameterAsText(1)
            arcpy.CreateFeatureclass_management(os.path.dirname(output), os.path.basename(output),"POINT",'','DISABLED','DISABLED',ref)
            arcpy.AddField_management(output,"msl","FLOAT")

##            cursor=arcpy.da.InsertCursor(os.getcwd()+"//warstwaNMEA.shp",("ID","SHAPE@XY"))
            cursor=arcpy.da.InsertCursor(output,("ID","SHAPE@XY","msl"))

            for a, lat in enumerate(self.lat):
                cursor.insertRow((a,(self.lon[a],lat),self.msl[a]))



    def par_gga(self,line):
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
        self.nmeadict[key][0]=utc
##        arcpy.AddMessage(utc)
        self.nmeadict[key][1]=latt
        self.nmeadict[key][2]=lonn
        self.nmeadict[key][3]=numsv
        self.nmeadict[key][4]=hdop
        self.nmeadict[key][7]=msl
        self.nmeadict[key][8]=geoid
        self.nmeadict[key][11]=fixstatus

    def par_rmc(self,line):
        data=[]
        data=line.split(',')
        key=data[1]
        utc=data[1][:2]+':'+data[1][2:4]+':'+data[1][4:6]
        latt=float(data[3][:2])+float(data[3][2:])/60
        ind=string.find(data[5],".")
        lonn=float(data[5][:(ind-2)])+float(data[5][(ind-2):])/60
        speed=data[7]
        datastatus=data[2]
        self.nmeadict[key][0]=utc
##        arcpy.AddMessage(utc)
        self.nmeadict[key][1]=latt
        self.nmeadict[key][2]=lonn
        self.nmeadict[key][9]=speed
        self.nmeadict[key][12]=datastatus

    def par_gll(self,line):
        data=[]
        data=line.split(',')
        key=data[5]
        utc=data[5][:2]+':'+data[5][2:4]+':'+data[5][4:6]
        latt=float(data[1][:2])+float(data[1][2:])/60
        ind=string.find(data[3],".")
        lonn=float(data[3][:(ind-2)])+float(data[3][(ind-2):])/60
        datastatus=data[6]
        self.nmeadict[key][0]=utc
##        arcpy.AddMessage(utc)
        self.nmeadict[key][1]=latt
        self.nmeadict[key][2]=lonn
        self.nmeadict[key][12]=datastatus


    def main(self):
        try:
            nmeafile=open(arcpy.GetParameterAsText(0))
            arcpy.AddMessage(os.getcwd())
    ##    for line in nmeafile:
    ##        arcpy.AddMessage(line)
            self.nmeaDict(nmeafile)
            self.addLayer()
        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            arcpy.AddError(e.args[0])

if __name__ == '__main__':
    nmea=nmeamain()
    nmea.main()

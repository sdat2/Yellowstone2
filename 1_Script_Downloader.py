## example@ python3 Z_Script_Downloader.py 2012 2014
file_name = 'Z_Script_Downloader.py'
## original script written by Sanne Cottaar (sc845@cam.ac.uk)
## adapted by Simon Thomas (sdat2@cam.ac.uk)
## Program for accessing IRIS database to download relevant PICKLE files from seismograms in the Yellowstone region

import obspy
from obspy.clients.fdsn import Client as IRISClient
from obspy import UTCDateTime
import os.path
import time
import datetime
import obspy.geodetics.base
import numpy as np
import obspy.geodetics
import sys, getopt

#--------------------------Specific Yellowstone Useless List (many stations)------------------------
Useless_Networks = []
Useless_List = ['DataRF/ZI.10010', 'DataRF/SY.BW06', 'DataRF/ZI.11240', 'DataRF/ZI.11004', 'DataRF/IE.BCYI', 'DataRF/ZI.10125', 'DataRF/MB.FBMT', 'DataRF/UU.OCP', 'DataRF/PB.B206', 'DataRF/ZH.SW23', 'DataRF/SY.G18A', 'DataRF/SY.C22A', 'DataRF/IM.PD03', 'DataRF/YF.N03', 'DataRF/ZI.11085', 'DataRF/ZI.11236', 'DataRF/ZH.SS182', 'DataRF/ZH.SS04', 'DataRF/SY.E18A', 'DataRF/ZI.11196', 'DataRF/EM.CON20', 'DataRF/EM.WYI17', 'DataRF/SY.F17A', 'DataRF/ZI.10800', 'DataRF/EM.MTE16', 'DataRF/RE.AVOW', 'DataRF/ZI.10565', 'DataRF/ZI.10150', 'DataRF/YH.L02', 'DataRF/SY.J13A', 'DataRF/ZI.10939', 'DataRF/ZH.SW26', 'DataRF/ZH.SM05', 'DataRF/ZI.10325', 'DataRF/XZ.CHP02', 'DataRF/ZI.11177', 'DataRF/ZH.SE18', 'DataRF/X6.A4850', 'DataRF/ZH.SW10', 'DataRF/ZI.10055', 'DataRF/UU.HES', 'DataRF/ZI.11242', 'DataRF/ZI.10420', 'DataRF/SY.H23A', 'DataRF/ZI.10000', 'DataRF/ZI.11032', 'DataRF/YF.N04', 'DataRF/PB.B205', 'DataRF/ZH.SN125', 'DataRF/EM.ORF09', 'DataRF/UU.UTH', 'DataRF/ZI.10975', 'DataRF/UU.TCVU', 'DataRF/ZH.SM08', 'DataRF/ZH.SN16', 'DataRF/ZI.11210', 'DataRF/UU.OF2', 'DataRF/EM.IDD11', 'DataRF/ZI.10415', 'DataRF/UU.ICF', 'DataRF/ZI.10265', 'DataRF/ZI.11238', 'DataRF/GS.WCDR', 'DataRF/ZI.10545', 'DataRF/ZI.11056', 'DataRF/5A.NV160', 'DataRF/MB.YBMT', 'DataRF/MB.MSMT', 'DataRF/MB.NDMT', 'DataRF/5A.NV110', 'DataRF/X6.E2000', 'DataRF/ZI.10030', 'DataRF/ZI.11183', 'DataRF/XZ.TSM13', 'DataRF/ZI.10984', 'DataRF/YH.L39', 'DataRF/SY.L12A', 'DataRF/ZI.11126', 'DataRF/ZI.11042', 'DataRF/ZI.10790', 'DataRF/SY.K26A', 'DataRF/IE.IRCI', 'DataRF/ZI.11140', 'DataRF/ZI.10515', 'DataRF/SY.E21A', 'DataRF/ZI.10630', 'DataRF/SY.N13A', 'DataRF/ZH.GBNO', 'DataRF/YH.A09', 'DataRF/ZI.11165', 'DataRF/ZI.11083', 'DataRF/ZI.10965', 'DataRF/EM.WYI21', 'DataRF/SY.H25A', 'DataRF/YF.N02', 'DataRF/ZI.11143', 'DataRF/ZI.11229', 'DataRF/ZI.11160', 'DataRF/SY.MSO', 'DataRF/SY.G24A', 'DataRF/ZH.SW09', 'DataRF/ZI.10950', 'DataRF/ZI.10435', 'DataRF/ZI.10370', 'DataRF/YH.L29', 'DataRF/UU.QBHW', 'DataRF/ZH.SN33', 'DataRF/UU.HCSU', 'DataRF/XZ.TLM30', 'DataRF/YH.L44', 'DataRF/RE.COLW', 'DataRF/SY.J09A', 'DataRF/ZI.11144', 'DataRF/XZ.TAT04', 'DataRF/ZI.10128', 'DataRF/ZI.11130', 'DataRF/X6.D4850', 'DataRF/EM.MTE21', 'DataRF/EM.MTF19', 'DataRF/MB.LYMT', 'DataRF/ZI.10485', 'DataRF/SY.D22A', 'DataRF/ZI.11044', 'DataRF/RE.MUDI', 'DataRF/XZ.TSM03', 'DataRF/RE.LOHW', 'DataRF/ZI.10085', 'DataRF/EM.IDF12', 'DataRF/EM.IDH13', 'DataRF/SY.H11A', 'DataRF/EM.NVM09', 'DataRF/ZI.11034', 'DataRF/UU.NAI', 'DataRF/ZI.10180', 'DataRF/X6.DEAD', 'DataRF/ZH.SE20', 'DataRF/X6.D4100', 'DataRF/SY.BMN', 'DataRF/XK.N07', 'DataRF/ZI.11212', 'DataRF/XZ.TAP02', 'DataRF/ZI.11081', 'DataRF/EM.WYI19', 'DataRF/ZI.11105', 'DataRF/MB.STMT', 'DataRF/XZ.TSM14', 'DataRF/EM.MTG19', 'DataRF/EM.MTE19', 'DataRF/UU.SLC2', 'DataRF/ZI.10360', 'DataRF/ZI.11074', 'DataRF/UU.QJOT', 'DataRF/ZI.10974', 'DataRF/MB.BHMT', 'DataRF/SY.F20A', 'DataRF/SY.O25A', 'DataRF/ZH.SW07', 'DataRF/XN.PS09', 'DataRF/ZI.11002', 'DataRF/XZ.TSM07', 'DataRF/ZI.10959', 'DataRF/UU.MGU', 'DataRF/XZ.TLC06', 'DataRF/WY.YPK', 'DataRF/XZ.TLM02', 'DataRF/ZI.10465', 'DataRF/UU.BEI', 'DataRF/5A.NV070', 'DataRF/UU.PTU', 'DataRF/5A.NV330', 'DataRF/YH.L33', 'DataRF/ZH.SN20', 'DataRF/XS.Y34', 'DataRF/ZI.11041', 'DataRF/XJ.CIC', 'DataRF/YH.L37', 'DataRF/SY.I18A', 'DataRF/ZI.11108', 'DataRF/YH.A06', 'DataRF/SY.K10A', 'DataRF/XG.SF1L', 'DataRF/SY.I16A', 'DataRF/ZH.SN30', 'DataRF/UU.VES', 'DataRF/WY.YMR', 'DataRF/ZI.10745', 'DataRF/ZI.11173', 'DataRF/GS.WWPK', 'DataRF/IM.PD32', 'DataRF/ZH.SE21', 'DataRF/SY.HLID', 'DataRF/ZI.11209', 'DataRF/ZI.11234', 'DataRF/UW.SFER', 'DataRF/EM.IDJ11', 'DataRF/XZ.CHP04', 'DataRF/SY.TPAW', 'DataRF/YH.L09', 'DataRF/EM.WYYS1', 'DataRF/ZI.11115', 'DataRF/SY.M15A', 'DataRF/SY.N15A', 'DataRF/SY.L26A', 'DataRF/EM.IDJ14', 'DataRF/SY.H15A', 'DataRF/ZH.SM30', 'DataRF/ZI.11224', 'DataRF/SY.FXWY', 'DataRF/WY.YFT', 'DataRF/XZ.TAN01', 'DataRF/EM.IDK16', 'DataRF/SY.F14A', 'DataRF/SY.I10A', 'DataRF/UU.HAFB', 'DataRF/EM.NVN11', 'DataRF/ZH.SM12', 'DataRF/UU.QRJG', 'DataRF/XZ.TLM25', 'DataRF/ZH.SM14', 'DataRF/ZI.10310', 'DataRF/ZH.SS06', 'DataRF/ZI.10981', 'DataRF/ZI.10130', 'DataRF/YH.A02', 'DataRF/SY.O21A', 'DataRF/EM.WYH18', 'DataRF/UW.SGAR', 'DataRF/ZI.10961', 'DataRF/SY.L17A', 'DataRF/ZI.11058', 'DataRF/UU.WBC', 'DataRF/SY.H09A', 'DataRF/NP.7208', 'DataRF/RE.REDW', 'DataRF/ZI.10810', 'DataRF/UU.SSC', 'DataRF/ZI.10540', 'DataRF/SY.K12A', 'DataRF/UU.QJHW', 'DataRF/ZI.11096', 'DataRF/SY.N09A', 'DataRF/IE.COMI', 'DataRF/ZI.11089', 'DataRF/SY.C17A', 'DataRF/RE.TPAW', 'DataRF/ZI.11003', 'DataRF/SY.O16A', 'DataRF/5A.NV310', 'DataRF/ZI.11136', 'DataRF/EM.IDE12', 'DataRF/UU.LSU', 'DataRF/X6.B4850', 'DataRF/5A.NV190', 'DataRF/ZH.SN19', 'DataRF/ZH.SS18', 'DataRF/UU.PCL', 'DataRF/ZI.10720', 'DataRF/SY.E11A', 'DataRF/YH.L43', 'DataRF/ZI.10495', 'DataRF/SY.E19A', 'DataRF/ZH.SN35', 'DataRF/ZH.SM18', 'DataRF/SY.K17A', 'DataRF/EM.IDH10', 'DataRF/5A.NV090', 'DataRF/EM.WYK18', 'DataRF/WY.YNE', 'DataRF/UU.GZU', 'DataRF/ZI.11088', 'DataRF/ZI.11161', 'DataRF/ZI.10954', 'DataRF/ZI.10815', 'DataRF/ZH.SM43', 'DataRF/ZH.SM53', 'DataRF/UU.FPU', 'DataRF/WY.YGC', 'DataRF/UU.ALP', 'DataRF/UU.JVW', 'DataRF/SY.L23A', 'DataRF/ZI.10400', 'DataRF/YH.A03', 'DataRF/IM.PD09', 'DataRF/UU.WLJ', 'DataRF/ZH.SM31', 'DataRF/XZ.TLM33', 'DataRF/SY.I12A', 'DataRF/XZ.TLC08', 'DataRF/XZ.CHP07', 'DataRF/XZ.TSM06', 'DataRF/X6.SHL', 'DataRF/ZH.SM41', 'DataRF/SY.G14A', 'DataRF/ZH.SE19', 'DataRF/UU.CWR', 'DataRF/ZI.11132', 'DataRF/ZI.10510', 'DataRF/ZI.10805', 'DataRF/UU.DUG', 'DataRF/XF.L15', 'DataRF/EM.COO21', 'DataRF/XK.N14', 'DataRF/ZI.11129', 'DataRF/ZI.10270', 'DataRF/EM.MTC17', 'DataRF/XZ.TSM20', 'DataRF/SY.F10A', 'DataRF/ZI.10845', 'DataRF/ZI.11167', 'DataRF/ZH.SM59', 'DataRF/ZH.SM40', 'DataRF/RE.ALPW', 'DataRF/EM.IDH11', 'DataRF/EM.IDH14', 'DataRF/SY.MOOW', 'DataRF/UU.ETW', 'DataRF/WY.YWB', 'DataRF/NP.7202', 'DataRF/UU.PCCW', 'DataRF/ZI.11109', 'DataRF/ZI.10855', 'DataRF/SY.K20A', 'DataRF/ZI.11053', 'DataRF/UW.SPK1', 'DataRF/ZI.11176', 'DataRF/SY.M25A', 'DataRF/5A.NV040', 'DataRF/SY.N14A', 'DataRF/ZI.11151', 'DataRF/ZH.SM33', 'DataRF/XZ.TSM01', 'DataRF/EM.IDI11', 'DataRF/SY.C12B', 'DataRF/EM.WAE10', 'DataRF/ZH.SN09', 'DataRF/RE.PACW', 'DataRF/ZI.10610', 'DataRF/ZI.10280', 'DataRF/EM.MTE14', 'DataRF/MB.BPMT', 'DataRF/ZH.SN08', 'DataRF/EM.IDG12', 'DataRF/ZI.11069', 'DataRF/XG.SF2H', 'DataRF/ZI.11113', 'DataRF/MB.BZMT', 'DataRF/5A.NV150', 'DataRF/ZH.SW20', 'DataRF/ZI.11189', 'DataRF/UU.CTU', 'DataRF/YH.L53', 'DataRF/EM.WYH19', 'DataRF/ZI.10850', 'DataRF/SY.J10A', 'DataRF/ZI.11091', 'DataRF/NQ.RRI', 'DataRF/EM.IDL10', 'DataRF/SY.J21A', 'DataRF/SY.M19A', 'DataRF/ZH.SM62', 'DataRF/ZI.11020', 'DataRF/XK.N23', 'DataRF/UU.RRCU', 'DataRF/UU.BCU', 'DataRF/NP.7203', 'DataRF/UU.LDJ', 'DataRF/ZH.SW19', 'DataRF/IM.PD07', 'DataRF/SY.N10A', 'DataRF/ZI.10978', 'DataRF/ZI.10020', 'DataRF/ZI.11207', 'DataRF/SY.F22A', 'DataRF/ZI.11073', 'DataRF/EM.MTD20', 'DataRF/UW.SPK4', 'DataRF/EM.IDF11', 'DataRF/WY.YHL', 'DataRF/ZI.10802', 'DataRF/XZ.TSM16', 'DataRF/ZI.11201', 'DataRF/XZ.CHP03', 'DataRF/ZI.10780', 'DataRF/SY.G25A', 'DataRF/ZH.SE17', 'DataRF/ZI.10275', 'DataRF/EM.NVM11', 'DataRF/XZ.TLM17', 'DataRF/UU.WVUT', 'DataRF/SY.HWUT', 'DataRF/IM.PD11', 'DataRF/EM.MTF21', 'DataRF/EM.ORL09', 'DataRF/ZI.10050', 'DataRF/XZ.TLM29', 'DataRF/ZI.10430', 'DataRF/ZI.10225', 'DataRF/EM.MTE17', 'DataRF/SY.LAO', 'DataRF/MB.CRMT', 'DataRF/UU.PTI', 'DataRF/EM.CON21', 'DataRF/ZI.10290', 'DataRF/ZI.10952', 'DataRF/SY.K16A', 'DataRF/ZI.10490', 'DataRF/X6.C4850', 'DataRF/ZI.11147', 'DataRF/X6.WTP', 'DataRF/SY.C16A', 'DataRF/ZH.SM07', 'DataRF/ZH.SS14', 'DataRF/XG.SF3L', 'DataRF/WY.YDC', 'DataRF/EM.IDD12', 'DataRF/EM.IDI15', 'DataRF/SY.D11A', 'DataRF/SY.E25A', 'DataRF/RE.RAMW', 'DataRF/ZI.10840', 'DataRF/ZH.SN27', 'DataRF/X6.LHS', 'DataRF/ZI.11134', 'DataRF/ZI.11205', 'DataRF/ZI.10395', 'DataRF/EM.NVO18', 'DataRF/ZH.SM47', 'DataRF/UU.RIV', 'DataRF/ZI.10971', 'DataRF/SY.D21A', 'DataRF/ZH.SN18', 'DataRF/YH.L27', 'DataRF/SY.N11A', 'DataRF/YH.L35', 'DataRF/ZI.10410', 'DataRF/ZI.10970', 'DataRF/ZI.11215', 'DataRF/EM.ORI09', 'DataRF/ZI.10949', 'DataRF/UU.HCO', 'DataRF/SY.O15A', 'DataRF/SY.ELK', 'DataRF/UU.TCUT', 'DataRF/UU.NPI', 'DataRF/ZI.10964', 'DataRF/XZ.TLM10', 'DataRF/XZ.TLC04', 'DataRF/IM.PD12', 'DataRF/ZH.SN10', 'DataRF/XZ.TLM01', 'DataRF/YJ.EPU2', 'DataRF/ZI.11174', 'DataRF/ZI.11232', 'DataRF/XZ.CHP12', 'DataRF/ZI.10895', 'DataRF/ZI.11037', 'DataRF/ZI.10555', 'DataRF/SY.L16A', 'DataRF/SY.O20A', 'DataRF/ZI.11116', 'DataRF/ZI.11223', 'DataRF/YH.L42', 'DataRF/ZH.SW21', 'DataRF/ZI.11055', 'DataRF/EM.IDJ15', 'DataRF/UU.WTU', 'DataRF/XZ.TLM13', 'DataRF/XU.GRSO', 'DataRF/ZI.11052', 'DataRF/UW.SPK3', 'DataRF/ZI.10988', 'DataRF/ZH.RPNE', 'DataRF/SY.M17A', 'DataRF/UU.BYP', 'DataRF/YH.A08', 'DataRF/ZI.11029', 'DataRF/ZI.11188', 'DataRF/ZH.SW03', 'DataRF/SY.C23A', 'DataRF/ZH.SE15', 'DataRF/XU.GRES', 'DataRF/SY.M13A', 'DataRF/IM.PD02', 'DataRF/ZI.11146', 'DataRF/UU.GAS', 'DataRF/EM.IDH12', 'DataRF/ZI.10670', 'DataRF/GS.WTMS', 'DataRF/ZI.11158', 'DataRF/ZI.10070', 'DataRF/ZH.SW11', 'DataRF/ZH.SM24', 'DataRF/ZI.10966', 'DataRF/SY.C11A', 'DataRF/XZ.TLM08', 'DataRF/SY.SPUD', 'DataRF/SY.IUGFS', 'DataRF/XN.PS02', 'DataRF/ZI.11222', 'DataRF/UU.GMV', 'DataRF/XZ.TLM35', 'DataRF/UU.RPF', 'DataRF/ZH.SM42', 'DataRF/ZI.10440', 'DataRF/ZI.11015', 'DataRF/ZI.10956', 'DataRF/ZI.11065', 'DataRF/ZH.SM60', 'DataRF/SY.O24A', 'DataRF/ZI.11145', 'DataRF/ZI.11169', 'DataRF/EM.MTC19', 'DataRF/ZI.10625', 'DataRF/EM.MTD15', 'DataRF/XT.OT12', 'DataRF/SY.E14A', 'DataRF/UU.SLC', 'DataRF/SY.N17A', 'DataRF/ZI.11104', 'DataRF/EM.MTC13', 'DataRF/EM.MTE20', 'DataRF/ZI.11119', 'DataRF/SY.RSSD', 'DataRF/SY.N22A', 'DataRF/XZ.TSM02', 'DataRF/ZI.10998', 'DataRF/5A.NV030', 'DataRF/SY.L15A', 'DataRF/EM.MTD16', 'DataRF/SY.N16A', 'DataRF/UU.QPML', 'DataRF/YJ.BGU1', 'DataRF/RE.GRAI', 'DataRF/ZI.10740', 'DataRF/ZI.10705', 'DataRF/ZI.10355', 'DataRF/ZI.11141', 'DataRF/SY.I17A', 'DataRF/SY.O09A', 'DataRF/ZH.SM48', 'DataRF/EM.WYL17', 'DataRF/UU.WMUT', 'DataRF/ZI.11233', 'DataRF/IE.ECRI', 'DataRF/ZI.10765', 'DataRF/ZI.11102', 'DataRF/ZH.SM09', 'DataRF/ZI.11063', 'DataRF/ZH.SM66', 'DataRF/SY.O17A', 'DataRF/EM.IDK11', 'DataRF/XZ.TLM38', 'DataRF/XZ.TAT01', 'DataRF/XZ.TLC01', 'DataRF/EM.MTF17', 'DataRF/X6.YATES', 'DataRF/ZH.SM11', 'DataRF/SY.REDW', 'DataRF/SY.N25A', 'DataRF/SY.K13A', 'DataRF/UU.QSAR', 'DataRF/XZ.TLM06', 'DataRF/MB.GCMT', 'DataRF/XZ.SPK2', 'DataRF/ZH.SS07', 'DataRF/EM.MTD21', 'DataRF/SY.C19A', 'DataRF/5A.NV240', 'DataRF/ZI.11016', 'DataRF/SY.I23A', 'DataRF/ZI.10200', 'DataRF/WY.MCID', 'DataRF/ZI.10770', 'DataRF/ZI.10825', 'DataRF/XZ.TLC02', 'DataRF/ZI.11168', 'DataRF/UW.SWES', 'DataRF/EM.IDL11', 'DataRF/GS.WTCF', 'DataRF/ZI.11010', 'DataRF/ZI.11028', 'DataRF/ZI.10680', 'DataRF/ZI.10500', 'DataRF/ZH.SM03', 'DataRF/SY.J14A', 'DataRF/IE.PZCI', 'DataRF/SY.O10A', 'DataRF/ZI.11067', 'DataRF/EM.MTD13', 'DataRF/EM.IDI12', 'DataRF/ZI.10635', 'DataRF/UU.EMF', 'DataRF/XG.SF1H', 'DataRF/SY.H10A', 'DataRF/XZ.TLM18', 'DataRF/ZI.11021', 'DataRF/SY.C15A', 'DataRF/IE.GRRI', 'DataRF/ZI.10979', 'DataRF/SY.I20A', 'DataRF/ZI.10575', 'DataRF/SY.C20A', 'DataRF/SY.E17A', 'DataRF/SY.C10A', 'DataRF/ZI.10600', 'DataRF/SY.M26A', 'DataRF/ZH.SS17', 'DataRF/ZI.11033', 'DataRF/SY.I22A', 'DataRF/ZI.11047', 'DataRF/XZ.TSM04', 'DataRF/SY.F18A', 'DataRF/YH.L38', 'DataRF/ZI.11193', 'DataRF/UU.DCU', 'DataRF/ZI.10145', 'DataRF/XZ.CHP11', 'DataRF/ZI.11026', 'DataRF/EM.IDC11', 'DataRF/ZI.10996', 'DataRF/ZI.10685', 'DataRF/ZI.11095', 'DataRF/UW.QWER', 'DataRF/ZI.11099', 'DataRF/YH.L15', 'DataRF/ZI.11190', 'DataRF/SY.O23A', 'DataRF/IE.GTRI', 'DataRF/ZI.11127', 'DataRF/UU.SCC', 'DataRF/EM.WYG21', 'DataRF/UU.BSS', 'DataRF/MB.ALMT', 'DataRF/XZ.CHP13', 'DataRF/X6.ORO', 'DataRF/ZI.10932', 'DataRF/IM.PDAR', 'DataRF/ZI.10385', 'DataRF/ZI.10300', 'DataRF/ZH.SW06', 'DataRF/ZI.11011', 'DataRF/ZI.11181', 'DataRF/ZI.11241', 'DataRF/ZI.10942', 'DataRF/UU.HON', 'DataRF/XN.PS04', 'DataRF/EM.MTG18', 'DataRF/SY.H12A', 'DataRF/ZI.11082', 'DataRF/ZH.SM52', 'DataRF/GS.WNFS', 'DataRF/ZH.SM39', 'DataRF/SY.K09A', 'DataRF/ZH.SE08', 'DataRF/UU.QCWC', 'DataRF/NP.2272', 'DataRF/SY.E23A', 'DataRF/SY.PHWY', 'DataRF/ZI.11213', 'DataRF/WY.YNR', 'DataRF/5A.NV170', 'DataRF/SY.FLWY', 'DataRF/UU.HTU', 'DataRF/ZI.10140', 'DataRF/XZ.TLM03', 'DataRF/RE.ANGW', 'DataRF/ZI.10951', 'DataRF/EM.MTF16', 'DataRF/SY.L13A', 'DataRF/EM.IDL12', 'DataRF/SY.G22A', 'DataRF/ZI.11198', 'DataRF/ZI.11098', 'DataRF/YH.L40', 'DataRF/XZ.TLM15', 'DataRF/ZH.SN17', 'DataRF/ZH.SW12', 'DataRF/SY.F23A', 'DataRF/ZI.10470', 'DataRF/ZI.10040', 'DataRF/5A.NV270', 'DataRF/ZI.10550', 'DataRF/ZI.11128', 'DataRF/5A.NV050', 'DataRF/XU.GRNE', 'DataRF/SY.M20A', 'DataRF/5A.NV250', 'DataRF/SY.JTMT', 'DataRF/IM.PD10', 'DataRF/ZI.11194', 'DataRF/ZH.SM64', 'DataRF/UU.COY', 'DataRF/ZH.SM57', 'DataRF/ZI.11018', 'DataRF/MB.NQMA', 'DataRF/EM.WYK20', 'DataRF/SY.MSOL', 'DataRF/XN.PS06', 'DataRF/XN.PS07', 'DataRF/YH.L01', 'DataRF/ZH.SM65', 'DataRF/ZI.11163', 'DataRF/SY.K25A', 'DataRF/ZI.11137', 'DataRF/UU.WCF', 'DataRF/ZH.SM54', 'DataRF/RE.HAYW', 'DataRF/WY.YLT', 'DataRF/XZ.TLM34', 'DataRF/XZ.TAT02', 'DataRF/ZI.11166', 'DataRF/ZI.10660', 'DataRF/ZI.11182', 'DataRF/YJ.WMU3', 'DataRF/ZI.11185', 'DataRF/SY.I15A', 'DataRF/SY.E10A', 'DataRF/EM.MTE18', 'DataRF/NP.2285', 'DataRF/ZH.SN29', 'DataRF/ZI.10595', 'DataRF/YJ.WMU4', 'DataRF/EM.ORF10', 'DataRF/UU.OPS', 'DataRF/UU.SPU', 'DataRF/ZI.10969', 'DataRF/5A.NV060', 'DataRF/5A.NV380', 'DataRF/ZH.SM37', 'DataRF/5A.NV120', 'DataRF/YH.L06', 'DataRF/ZH.GBSE', 'DataRF/SY.DUG', 'DataRF/UU.HER', 'DataRF/ZI.11152', 'DataRF/ZI.11012', 'DataRF/WY.YTP', 'DataRF/ZI.10255', 'DataRF/ZI.10520', 'DataRF/WY.YMC', 'DataRF/X6.300', 'DataRF/SY.J19A', 'DataRF/ZH.SM13', 'DataRF/ZI.10795', 'DataRF/PN.PPRMH', 'DataRF/X6.D2000', 'DataRF/ZI.11159', 'DataRF/ZI.11059', 'DataRF/UW.QPJE', 'DataRF/XN.PS08', 'DataRF/ZI.11078', 'DataRF/XJ.NST', 'DataRF/ZI.11001', 'DataRF/ZI.11076', 'DataRF/ZI.10450', 'DataRF/XZ.TLM05', 'DataRF/UU.RBU', 'DataRF/EM.NVO12', 'DataRF/ZI.11006', 'DataRF/UU.MAB', 'DataRF/UU.RCJ', 'DataRF/ZI.10990', 'DataRF/YJ.HWU1', 'DataRF/SY.I21A', 'DataRF/SY.RWWY', 'DataRF/RE.CHOI', 'DataRF/SY.F12A', 'DataRF/ZH.SM35', 'DataRF/ZI.11046', 'DataRF/SY.L22A', 'DataRF/ZI.11000', 'DataRF/SY.L18A', 'DataRF/ZH.SM46', 'DataRF/UU.AVE', 'DataRF/ZI.10972', 'DataRF/XU.GRCO', 'DataRF/MB.BEMT', 'DataRF/ZH.SM01', 'DataRF/ZI.10345', 'DataRF/ZI.10230', 'DataRF/YJ.BGU2', 'DataRF/EM.IDK14', 'DataRF/ZI.11106', 'DataRF/YH.L24', 'DataRF/ZI.11023', 'DataRF/XZ.TLM27', 'DataRF/ZI.10110', 'DataRF/MB.LRM', 'DataRF/ZI.10075', 'DataRF/IE.CBTI', 'DataRF/ZI.10375', 'DataRF/UU.PGC', 'DataRF/ZI.11038', 'DataRF/ZH.SN12', 'DataRF/XZ.TSM11', 'DataRF/SY.G10A', 'DataRF/UW.SPK2', 'DataRF/5A.NV230', 'DataRF/EM.NVM13', 'DataRF/YH.L45', 'DataRF/SY.D25A', 'DataRF/ZI.10530', 'DataRF/ZH.SN24', 'DataRF/SY.D23A', 'DataRF/EM.WYJ20', 'DataRF/ZI.10405', 'DataRF/XN.PS01', 'DataRF/WY.YPP', 'DataRF/ZI.10480', 'DataRF/SY.C13A', 'DataRF/UU.DOT', 'DataRF/SY.O26A', 'DataRF/SY.H16A', 'DataRF/XZ.TLM12', 'DataRF/ZI.11070', 'DataRF/YH.L18', 'DataRF/SY.L11A', 'DataRF/YH.L50', 'DataRF/SY.AHID', 'DataRF/UU.HFSU', 'DataRF/WY.YNM', 'DataRF/SY.LKWY', 'DataRF/YF.N06', 'DataRF/XG.CR02', 'DataRF/WY.YMP', 'DataRF/SY.D24A', 'DataRF/SY.K18A', 'DataRF/ZH.SN22', 'DataRF/ZH.SM29', 'DataRF/ZI.11156', 'DataRF/EM.WYJ18', 'DataRF/ZH.SW13', 'DataRF/SY.D20A', 'DataRF/XZ.TLM36', 'DataRF/ZI.10320', 'DataRF/5A.NV130', 'DataRF/ZI.10915', 'DataRF/ZI.11237', 'DataRF/YH.A07', 'DataRF/5A.NV100', 'DataRF/YH.L14', 'DataRF/ZI.10860', 'DataRF/NN.RUBY', 'DataRF/SY.H17A', 'DataRF/EM.MTE13', 'DataRF/UU.QBNA', 'DataRF/ZI.11087', 'DataRF/SY.PD31', 'DataRF/SY.I24A', 'DataRF/MB.PCMT', 'DataRF/UW.QEWU', 'DataRF/EM.MTD18', 'DataRF/SY.WUWY', 'DataRF/XZ.TLM31', 'DataRF/XZ.TLM39', 'DataRF/IE.ICI', 'DataRF/ZH.SS11', 'DataRF/UW.SHLY', 'DataRF/ZI.11121', 'DataRF/YH.L46', 'DataRF/UU.QCSP', 'DataRF/SY.I19A', 'DataRF/EM.NVM10', 'DataRF/YH.L31', 'DataRF/XZ.SPK4', 'DataRF/XZ.TLM14', 'DataRF/SY.G20A', 'DataRF/UU.GMO', 'DataRF/YH.L26', 'DataRF/XZ.TAT03', 'DataRF/SY.J16A', 'DataRF/ZI.10980', 'DataRF/XK.N12', 'DataRF/EM.MTC21', 'DataRF/ZH.SE12', 'DataRF/EM.IDK10', 'DataRF/ZI.11024', 'DataRF/SY.L19A', 'DataRF/SY.F19A', 'DataRF/EM.IDI14', 'DataRF/ZI.10900', 'DataRF/YH.L11', 'DataRF/ZI.10994', 'DataRF/ZI.11043', 'DataRF/ZH.SW15', 'DataRF/ZI.11192', 'DataRF/EM.MTC20', 'DataRF/ZI.11175', 'DataRF/ZI.11228', 'DataRF/ZI.10245', 'DataRF/ZI.10940', 'DataRF/XG.SF2L', 'DataRF/ZH.SM61', 'DataRF/EM.WYYS3', 'DataRF/SY.E15A', 'DataRF/SY.J20A', 'DataRF/ZI.10340', 'DataRF/UU.SPR', 'DataRF/EM.MTG16', 'DataRF/ZH.SN28', 'DataRF/ZI.10820', 'DataRF/SY.G17A', 'DataRF/SY.C21A', 'DataRF/ZI.11150', 'DataRF/YJ.EPU4', 'DataRF/ZH.SM28', 'DataRF/EM.MTC14', 'DataRF/SY.G13A', 'DataRF/ZH.SE16', 'DataRF/IE.CRBI', 'DataRF/SY.C24A', 'DataRF/WY.YHH', 'DataRF/YH.L06A', 'DataRF/ZH.SE22', 'DataRF/ZI.10991', 'DataRF/ZI.11092', 'DataRF/XS.Y46', 'DataRF/XZ.TLM22', 'DataRF/WY.YPC', 'DataRF/NP.7212', 'DataRF/XZ.TLM04', 'DataRF/XZ.CHP15', 'DataRF/ZI.10920', 'DataRF/ZH.SM45', 'DataRF/EM.WAC10', 'DataRF/XZ.TAP03', 'DataRF/EM.MTD14', 'DataRF/SY.O13A', 'DataRF/X6.MAST', 'DataRF/WY.YML', 'DataRF/ZH.SM04', 'DataRF/ZI.11206', 'DataRF/UU.OSS', 'DataRF/ZI.11049', 'DataRF/EM.IDG13', 'DataRF/ZI.10935', 'DataRF/ZI.10999', 'DataRF/ZI.10615', 'DataRF/RE.PINI', 'DataRF/WY.YJC', 'DataRF/ZI.11031', 'DataRF/SY.G12A', 'DataRF/UU.MOR', 'DataRF/X6.B2000', 'DataRF/WY.YLA', 'DataRF/IM.PD01', 'DataRF/ZH.SS02', 'DataRF/SY.MFID', 'DataRF/UU.CHS', 'DataRF/ZH.SE01', 'DataRF/IM.PD06', 'DataRF/YH.L34', 'DataRF/EM.IDL13', 'DataRF/ZI.11040', 'DataRF/ZI.11200', 'DataRF/ZI.10195', 'DataRF/ZI.11068', 'DataRF/SY.G11A', 'DataRF/SY.N19A', 'DataRF/UU.LKC', 'DataRF/ZH.RCEA', 'DataRF/SY.D14A', 'DataRF/SY.N20A', 'DataRF/EM.MTF18', 'DataRF/EM.M2E13', 'DataRF/YH.L51', 'DataRF/MB.JTMT', 'DataRF/IM.PD08', 'DataRF/X6.A2000', 'DataRF/XZ.TLC05', 'DataRF/UU.NOQ5', 'DataRF/EM.MTC15', 'DataRF/SY.M10A', 'DataRF/RE.STEW', 'DataRF/ZH.SS09', 'DataRF/MB.HRY', 'DataRF/ZI.11203', 'DataRF/5A.NV210', 'DataRF/SY.J18A', 'DataRF/YH.L36', 'DataRF/ZI.10976', 'DataRF/ZI.11208', 'DataRF/UU.JLU', 'DataRF/SY.L25A', 'DataRF/UU.QFTG', 'DataRF/ZI.11226', 'DataRF/IE.NPRI', 'DataRF/SY.H18A', 'DataRF/UU.QJMH', 'DataRF/WY.YSB', 'DataRF/UU.MTUT', 'DataRF/XN.PS05', 'DataRF/SY.D13A', 'DataRF/UU.UUE', 'DataRF/XZ.TSM10', 'DataRF/EM.IDL15', 'DataRF/ZI.10963', 'DataRF/SY.I11A', 'DataRF/XS.Y16', 'DataRF/XZ.CHP08', 'DataRF/ZI.11112', 'DataRF/ZI.10982', 'DataRF/ZI.11219', 'DataRF/EM.IDI13', 'DataRF/ZH.SE10', 'DataRF/ZI.11017', 'DataRF/ZI.11013', 'DataRF/ZI.10944', 'DataRF/ZI.10175', 'DataRF/XZ.TAP01', 'DataRF/ZH.SS05', 'DataRF/ZI.10620', 'DataRF/ZI.11139', 'DataRF/YF.N05', 'DataRF/XZ.TLM09', 'DataRF/XZ.TSM19', 'DataRF/UU.QOGD', 'DataRF/UU.NOQ3', 'DataRF/IE.CNCI', 'DataRF/XJ.BLM', 'DataRF/5A.NV220', 'DataRF/MB.NCM', 'DataRF/ZH.SW205', 'DataRF/ZI.11035', 'DataRF/UU.QDPS', 'DataRF/SY.O18A', 'DataRF/ZH.SM58', 'DataRF/XT.D19', 'DataRF/SY.F09A', 'DataRF/ZI.10640', 'DataRF/SY.K19A', 'DataRF/UU.LCU', 'DataRF/ZI.10305', 'DataRF/WY.YCJ', 'DataRF/XZ.SPK1', 'DataRF/UU.HLJ', 'DataRF/ZH.SN23', 'DataRF/ZI.10885', 'DataRF/UW.SPK5', 'DataRF/XS.Y22', 'DataRF/EM.IDJ10', 'DataRF/ZH.SN06', 'DataRF/UU.BES', 'DataRF/SY.J17A', 'DataRF/UU.NAIU', 'DataRF/ZI.11217', 'DataRF/NP.7232', 'DataRF/ZI.11107', 'DataRF/ZH.SS16', 'DataRF/RE.MOOW', 'DataRF/ZH.SM22', 'DataRF/ZI.10730', 'DataRF/ZH.GBSW', 'DataRF/EM.WYL21', 'DataRF/UU.HRU', 'DataRF/ZI.11050', 'DataRF/UU.GRD', 'DataRF/SY.F11A', 'DataRF/MB.HBMT', 'DataRF/ZH.SW27', 'DataRF/UU.MLI', 'DataRF/YH.L28', 'DataRF/ZH.SM49', 'DataRF/ZI.10968', 'DataRF/ZI.10115', 'DataRF/ZI.11122', 'DataRF/ZI.10948', 'DataRF/UU.CFS', 'DataRF/ZI.10065', 'DataRF/ZH.SW04', 'DataRF/UU.WRP', 'DataRF/SY.J12A', 'DataRF/ZI.10365', 'DataRF/SY.M09A', 'DataRF/YJ.WMU2', 'DataRF/ZH.SM36', 'DataRF/SY.L14A', 'DataRF/SY.H21A', 'DataRF/XZ.TLM16', 'DataRF/ZI.10025', 'DataRF/ZI.10937', 'DataRF/XZ.TLC07', 'DataRF/SY.N24A', 'DataRF/EM.IDJ13', 'DataRF/EM.MTG15', 'DataRF/ZI.10925', 'DataRF/YH.L16', 'DataRF/SY.M14A', 'DataRF/UU.GMU', 'DataRF/IM.PD05', 'DataRF/ZI.11071', 'DataRF/ZH.SW28', 'DataRF/ZI.10120', 'DataRF/ZI.10865', 'DataRF/XZ.CHP14', 'DataRF/SY.BMO', 'DataRF/UU.SCY', 'DataRF/UU.EPU', 'DataRF/MB.MSO', 'DataRF/SY.E20A', 'DataRF/SY.F13A', 'DataRF/ZH.RPCW', 'DataRF/ZI.10957', 'DataRF/ZI.10695', 'DataRF/ZI.10931', 'DataRF/ZI.10165', 'DataRF/EM.MTD19', 'DataRF/SY.F16A', 'DataRF/SY.I14A', 'DataRF/ZH.GBCS', 'DataRF/MB.BUT', 'DataRF/ZI.10905', 'DataRF/ZI.11072', 'DataRF/ZH.SN15', 'DataRF/EM.IDI16', 'DataRF/ZI.11066', 'DataRF/ZH.SE05', 'DataRF/XZ.TLM32', 'DataRF/SY.J25A', 'DataRF/XZ.TSM08', 'DataRF/XN.PS10', 'DataRF/ZI.11202', 'DataRF/SY.M18A', 'DataRF/ZI.11064', 'DataRF/SY.M22A', 'DataRF/YJ.BGU3', 'DataRF/UU.NOQ4', 'DataRF/EM.NVN09', 'DataRF/ZI.10080', 'DataRF/ZI.10335', 'DataRF/ZI.11171', 'DataRF/ZH.SN05', 'DataRF/ZH.SS08', 'DataRF/ZI.11077', 'DataRF/SY.N18A', 'DataRF/X6.ROSS', 'DataRF/ZI.10710', 'DataRF/ZI.10947', 'DataRF/ZI.10190', 'DataRF/UU.AMF', 'DataRF/UU.BGU', 'DataRF/SY.M12A', 'DataRF/ZH.SN32', 'DataRF/PB.B207', 'DataRF/ZI.10585', 'DataRF/UU.BBU', 'DataRF/ZI.10870', 'DataRF/ZI.10060', 'DataRF/ZI.10505', 'DataRF/SY.BOZ', 'DataRF/SY.F21A', 'DataRF/EM.MTF14', 'DataRF/EM.IDK15', 'DataRF/ZI.10240', 'DataRF/XN.PS03', 'DataRF/ZI.11093', 'DataRF/UU.LGC', 'DataRF/UU.MOUT', 'DataRF/ZH.RPWE', 'DataRF/EM.IDL14', 'DataRF/SY.E12A', 'DataRF/ZI.10997', 'DataRF/ZI.10985', 'DataRF/ZH.SM15', 'DataRF/EM.NVN12', 'DataRF/XZ.CHP06', 'DataRF/SY.C25A', 'DataRF/YH.L32', 'DataRF/5A.NV320', 'DataRF/X6.800', 'DataRF/ZI.10215', 'DataRF/ZI.11060', 'DataRF/ZH.SM27', 'DataRF/UU.QSUN', 'DataRF/ZI.10715', 'DataRF/ZI.10185', 'DataRF/ZI.11180', 'DataRF/UU.BCS', 'DataRF/X6.C4100', 'DataRF/ZH.SN11', 'DataRF/XZ.TLM26', 'DataRF/SY.K22A', 'DataRF/ZI.10725', 'DataRF/ZI.11149', 'DataRF/ZH.SE07', 'DataRF/SY.E22A', 'DataRF/ZI.11197', 'DataRF/YH.L48', 'DataRF/EM.ORK09', 'DataRF/UU.SJF', 'DataRF/YH.L05', 'DataRF/ZI.11080', 'DataRF/EM.WYI18', 'DataRF/ZI.10330', 'DataRF/YH.L30', 'DataRF/EM.IDI10', 'DataRF/ZI.10580', 'DataRF/XZ.TLM20', 'DataRF/ZI.10260', 'DataRF/YH.L20', 'DataRF/ZH.SS185', 'DataRF/5A.NV280', 'DataRF/UU.CAPU', 'DataRF/XZ.TSM18', 'DataRF/YJ.HWU3', 'DataRF/5A.NV290', 'DataRF/EM.MTC12', 'DataRF/ZI.10655', 'DataRF/WY.YUF', 'DataRF/EM.WYJ21', 'DataRF/ZI.11125', 'DataRF/ZI.10987', 'DataRF/ZI.11027', 'DataRF/GS.WWHL', 'DataRF/UU.SCS', 'DataRF/X6.RRDG', 'DataRF/XZ.TAN02', 'DataRF/ZI.11005', 'DataRF/SY.J15A', 'DataRF/WY.YHB', 'DataRF/ZI.10315', 'DataRF/SY.PLID', 'DataRF/SY.LOHW', 'DataRF/EM.WYH20', 'DataRF/SY.G15A', 'DataRF/XZ.CHP05', 'DataRF/RE.TRXW', 'DataRF/SY.SNOW', 'DataRF/SY.L09A', 'DataRF/X6.A4100', 'DataRF/MB.QLMT', 'DataRF/EM.WYJ17', 'DataRF/SY.D19A', 'DataRF/EM.COO20', 'DataRF/ZH.SW16', 'DataRF/UU.BMUT', 'DataRF/SY.N12A', 'DataRF/ZI.10570', 'DataRF/SY.IMW', 'DataRF/EM.WYI20', 'DataRF/UU.WES', 'DataRF/ZI.11172', 'DataRF/ZH.GBCN', 'DataRF/UU.PCR', 'DataRF/ZI.11216', 'DataRF/SY.E24A', 'DataRF/ZI.10380', 'DataRF/UW.SNIO', 'DataRF/ZI.10700', 'DataRF/XU.GREP', 'DataRF/SY.M11A', 'DataRF/PB.B208', 'DataRF/UU.WHS', 'DataRF/ZI.11131', 'DataRF/EM.WYYS2', 'DataRF/EM.WYJ19', 'DataRF/ZI.11025', 'DataRF/ZI.10135', 'DataRF/UU.HONU', 'DataRF/UU.NOQ6', 'DataRF/ZI.11051', 'DataRF/ZI.10735', 'DataRF/ZI.10775', 'DataRF/EM.WYK19', 'DataRF/SY.D15A', 'DataRF/ZI.10650', 'DataRF/YJ.BGU4', 'DataRF/SY.O22A', 'DataRF/ZH.SM16', 'DataRF/SY.D18A', 'DataRF/ZI.11187', 'DataRF/YH.L21', 'DataRF/ZH.SN36', 'DataRF/ZI.10946', 'DataRF/MB.MCMT', 'DataRF/SY.DLMT', 'DataRF/ZI.11230', 'DataRF/EM.MTC18', 'DataRF/SY.N26A', 'DataRF/YH.L12', 'DataRF/SY.RRI2', 'DataRF/ZH.SE13', 'DataRF/ZI.11220', 'DataRF/YH.L25', 'DataRF/ZI.11148', 'DataRF/ZI.10785', 'DataRF/SY.L24A', 'DataRF/UW.SOPS', 'DataRF/SY.N23A', 'DataRF/ZH.SS13', 'DataRF/YH.L41', 'DataRF/ZI.10095', 'DataRF/ZI.10995', 'DataRF/YH.L08', 'DataRF/5A.NV200', 'DataRF/ZI.10958', 'DataRF/UU.KLJ', 'DataRF/SY.K24A', 'DataRF/EM.WYK21', 'DataRF/ZI.10960', 'DataRF/EM.ORH09', 'DataRF/ZI.10210', 'DataRF/SY.G16A', 'DataRF/MB.CHMT', 'DataRF/X6.TPK', 'DataRF/ZI.11008', 'DataRF/ZI.11184', 'DataRF/UU.QLIN', 'DataRF/MB.SLMT', 'DataRF/EM.ORG09', 'DataRF/SY.PPRMH', 'DataRF/PB.B950', 'DataRF/YJ.EPU1', 'DataRF/UU.QKSL', 'DataRF/XZ.TLM19', 'DataRF/UU.SAIU', 'DataRF/UU.MID', 'DataRF/ZI.10665', 'DataRF/RE.SNOW', 'DataRF/ZH.SW14', 'DataRF/UU.QMDS', 'DataRF/EM.MTG20', 'DataRF/ZI.11157', 'DataRF/SY.M23A', 'DataRF/UW.JORV', 'DataRF/5A.NV080', 'DataRF/UU.HVU', 'DataRF/ZI.11097', 'DataRF/XZ.TSC01', 'DataRF/ZI.11061', 'DataRF/ZI.10910', 'DataRF/UU.VNL', 'DataRF/ZI.11030', 'DataRF/ZI.11124', 'DataRF/YH.L52', 'DataRF/UU.ALT', 'DataRF/SY.N21A', 'DataRF/IE.HHAI', 'DataRF/ZH.SN07', 'DataRF/RE.BEAW', 'DataRF/ZH.SE14', 'DataRF/ZH.SS19', 'DataRF/EM.NVO09', 'DataRF/UU.JRP', 'DataRF/ZI.10890', 'DataRF/ZI.11118', 'DataRF/XZ.CHP01', 'DataRF/UU.TCU', 'DataRF/SY.G21A', 'DataRF/XZ.TSM05', 'DataRF/NN.WNMCA', 'DataRF/ZI.11135', 'DataRF/MB.ELMT', 'DataRF/ZI.10835', 'DataRF/ZI.11048', 'DataRF/5A.NV260', 'DataRF/ZH.RPSE', 'DataRF/ZI.10830', 'DataRF/ZI.11211', 'DataRF/ZI.11101', 'DataRF/UU.MPU', 'DataRF/YH.L17', 'DataRF/ZI.11084', 'DataRF/YJ.EPU3', 'DataRF/YH.L10', 'DataRF/MB.VCMT', 'DataRF/YH.A05', 'DataRF/X6.C2000', 'DataRF/ZI.11090', 'DataRF/IE.EMI', 'DataRF/IE.LJI', 'DataRF/XZ.TLM24', 'DataRF/ZI.11186', 'DataRF/SY.F25A', 'DataRF/ZI.11214', 'DataRF/ZI.10045', 'DataRF/SY.C12A', 'DataRF/ZI.10425', 'DataRF/XZ.TLM11', 'DataRF/XZ.TLM37', 'DataRF/ZI.10945', 'DataRF/GS.WWKW', 'DataRF/YH.L22', 'DataRF/ZI.10933', 'DataRF/UU.HEB', 'DataRF/ZH.SM10', 'DataRF/XU.GRNW', 'DataRF/MB.NQBU', 'DataRF/ZI.11227', 'DataRF/SY.I09A', 'DataRF/ZI.11086', 'DataRF/ZH.SM44', 'DataRF/ZI.10941', 'DataRF/ZI.10750', 'DataRF/SY.E13A', 'DataRF/SY.H13A', 'DataRF/ZI.11162', 'DataRF/ZI.11057', 'DataRF/UU.LMU', 'DataRF/EM.WYH21', 'DataRF/XZ.SPK5', 'DataRF/ZH.RPCE', 'DataRF/ZH.SS12', 'DataRF/ZI.10989', 'DataRF/SY.G09A', 'DataRF/EM.NVO10', 'DataRF/WY.YPM', 'DataRF/ZI.10675', 'DataRF/UU.RSUT', 'DataRF/ZH.SN14', 'DataRF/ZI.11045', 'DataRF/EM.MTF13', 'DataRF/EM.WAD10', 'DataRF/ZI.10943', 'DataRF/ZI.11142', 'DataRF/ZI.10220', 'DataRF/UW.QZOE', 'DataRF/ZI.11036', 'DataRF/ZI.10967', 'DataRF/ZH.SM56', 'DataRF/ZI.10100', 'DataRF/ZI.10295', 'DataRF/ZI.11235', 'DataRF/ZI.10755', 'DataRF/ZH.SE06', 'DataRF/ZH.SW08', 'DataRF/UU.SPS', 'DataRF/ZH.SM63', 'DataRF/ZI.11221', 'DataRF/UU.LHUT', 'DataRF/UU.EOCU', 'DataRF/ZI.10605', 'DataRF/ZI.11153', 'DataRF/ZI.10973', 'DataRF/ZH.SW18', 'DataRF/ZI.10590', 'DataRF/YH.L19', 'DataRF/ZI.11155', 'DataRF/ZI.11133', 'DataRF/SY.D16A', 'DataRF/ZI.10525', 'DataRF/ZI.10160', 'DataRF/ZI.10005', 'DataRF/ZH.SN26', 'DataRF/UU.QPAY', 'DataRF/UU.LTU', 'DataRF/UU.DAU', 'DataRF/IE.LLRI', 'DataRF/MB.TPMT', 'DataRF/EM.MTF20', 'DataRF/MB.OVMT', 'DataRF/ZH.SW25', 'DataRF/ZI.10035', 'DataRF/ZI.10962', 'DataRF/UU.ELE', 'DataRF/ZI.11231', 'DataRF/ZH.SM125', 'DataRF/ZH.SW17', 'DataRF/SY.O12A', 'DataRF/EM.WYL20', 'DataRF/YJ.HWU2', 'DataRF/UU.TRS', 'DataRF/ZH.SN105', 'DataRF/ZH.SW05', 'DataRF/ZH.SN31', 'DataRF/ZI.10250', 'DataRF/ZI.11009', 'DataRF/XZ.TLM40', 'DataRF/SY.F15A', 'DataRF/UU.SNUT', 'DataRF/MB.LCCM', 'DataRF/EM.IDK13', 'DataRF/ZI.10350', 'DataRF/SY.H22A', 'DataRF/SY.DCID1', 'DataRF/UU.QSTV', 'DataRF/ZH.SE04', 'DataRF/XZ.TSM09', 'DataRF/ZH.SW235', 'DataRF/ZI.10235', 'DataRF/IE.ARNI', 'DataRF/SY.K15A', 'DataRF/ZI.11178', 'DataRF/SY.H19A', 'DataRF/ZI.10460', 'DataRF/ZI.11103', 'DataRF/SY.L20A', 'DataRF/ZI.10690', 'DataRF/ZI.11054', 'DataRF/UU.TPU', 'DataRF/ZI.11138', 'DataRF/ZH.SE09', 'DataRF/XJ.MHO', 'DataRF/MB.SWMT', 'DataRF/ZI.10977', 'DataRF/MB.BSMT', 'DataRF/ZI.10390', 'DataRF/MB.MOMT', 'DataRF/SY.K11A', 'DataRF/ZI.11110', 'DataRF/ZI.10205', 'DataRF/ZI.11117', 'DataRF/RE.JLDW', 'DataRF/EM.NVO11', 'DataRF/YH.L23', 'DataRF/ZH.SM38', 'DataRF/XG.CR01', 'DataRF/UU.MCU', 'DataRF/UU.UHP', 'DataRF/ZI.11204', 'DataRF/RE.TARW', 'DataRF/PB.B944', 'DataRF/EM.ORJ09', 'DataRF/SY.J26A', 'DataRF/XZ.TLM28', 'DataRF/ZI.11039', 'DataRF/ZI.11062', 'DataRF/SY.J22A', 'DataRF/EM.WYK17', 'DataRF/SY.M16A', 'DataRF/ZI.11014', 'DataRF/ZH.SM34', 'DataRF/NP.2286', 'DataRF/YH.L03', 'DataRF/ZH.RCNW', 'DataRF/SY.F24A', 'DataRF/GD.MSOL', 'DataRF/UU.BYU', 'DataRF/X6.1700', 'DataRF/ZI.10760', 'DataRF/5A.NV020', 'DataRF/XZ.TSM17', 'DataRF/YJ.HWU4', 'DataRF/SY.RLMT', 'DataRF/ZI.11239', 'DataRF/SY.K21A', 'DataRF/ZI.11191', 'DataRF/ZH.SM32', 'DataRF/SY.J11A', 'DataRF/ZI.10015', 'DataRF/MB.BGMT', 'DataRF/ZI.11179', 'DataRF/ZI.10934', 'DataRF/SY.E16A', 'DataRF/ZI.11007', 'DataRF/ZI.11123', 'DataRF/EM.IDJ12', 'DataRF/YH.L13', 'DataRF/ZI.10475', 'DataRF/YH.L49', 'DataRF/WY.YMS', 'DataRF/EM.WYL19', 'DataRF/ZH.SM51', 'DataRF/ZI.11022', 'DataRF/EM.MTG14', 'DataRF/UU.HDU', 'DataRF/ZH.SW22', 'DataRF/EM.IDL16', 'DataRF/ZI.10880', 'DataRF/ZI.10645', 'DataRF/EM.MTF15', 'DataRF/XZ.TLC03', 'DataRF/ZI.10953', 'DataRF/ZI.11225', 'DataRF/ZI.10875', 'DataRF/EM.IDK12', 'DataRF/PB.B945', 'DataRF/UU.FTT', 'DataRF/ZI.10155', 'DataRF/5A.NV180', 'DataRF/YH.L04', 'DataRF/ZO.UTTR3', 'DataRF/UU.QSPA', 'DataRF/ZI.10993', 'DataRF/YF.N07', 'DataRF/YH.L54', 'DataRF/XJ.BRK', 'DataRF/ZH.SM20', 'DataRF/ZI.10445', 'DataRF/EM.ORG10', 'DataRF/XK.N15', 'DataRF/YH.A10', 'DataRF/UU.LRG', 'DataRF/XK.N13', 'DataRF/SY.BRAN', 'DataRF/UW.QPID', 'DataRF/ZH.SS03', 'DataRF/MB.MKMT', 'DataRF/EM.MTC16', 'DataRF/SY.D10A', 'DataRF/YH.L55', 'DataRF/SY.J24A', 'DataRF/ZH.SN25', 'DataRF/ZI.11019', 'DataRF/SY.L10A', 'DataRF/YF.N01', 'DataRF/ZH.SN21', 'DataRF/YH.L47', 'DataRF/ZI.11218', 'DataRF/ZH.SM06', 'DataRF/XK.N14A', 'DataRF/XZ.CHP09', 'DataRF/WY.YMV', 'DataRF/ZI.10992', 'DataRF/EM.NVM12', 'DataRF/SY.C14A', 'DataRF/EM.IDG11', 'DataRF/ZI.11195', 'DataRF/MB.SXM', 'DataRF/ZI.10986', 'DataRF/GS.WTCW', 'DataRF/ZI.10983', 'DataRF/ZO.UTTR1', 'DataRF/ZI.10938', 'DataRF/XZ.SPK3', 'DataRF/IW.WUWY', 'DataRF/UU.QNRL', 'DataRF/XS.Y07', 'DataRF/SY.H14A', 'DataRF/SY.L21A', 'DataRF/ZI.11100', 'DataRF/UU.MHD', 'DataRF/XZ.TSM15', 'DataRF/UU.RDMU', 'DataRF/IM.PD13', 'DataRF/ZI.11199', 'DataRF/EM.MTE15', 'DataRF/ZH.RCSW', 'DataRF/ZI.11075', 'DataRF/XU.GRWE', 'DataRF/RC.CMI', 'DataRF/EM.WYL18', 'DataRF/SY.D12A', 'DataRF/5A.NV300', 'DataRF/UW.QSKF', 'DataRF/YJ.WMU1', 'DataRF/ZI.10560', 'DataRF/SY.K23A', 'DataRF/UU.NOQ', 'DataRF/XG.SF3H', 'DataRF/SY.K14A', 'DataRF/ZI.11114', 'DataRF/SY.D17A', 'DataRF/ZI.10955', 'DataRF/ZI.10090', 'DataRF/ZI.11094', 'DataRF/ZH.SM19', 'DataRF/ZI.11079', 'DataRF/SY.G23A', 'DataRF/5A.NV010', 'DataRF/ZI.11111', 'DataRF/XJ.BOI', 'DataRF/SY.O19A', 'DataRF/UU.CWU', 'DataRF/ZI.11154', 'DataRF/SY.I13A', 'DataRF/ZI.10285', 'DataRF/ZH.SM55', 'DataRF/UU.BSUT', 'DataRF/SY.O11A', 'DataRF/EM.IDJ16', 'DataRF/SY.H20A', 'DataRF/SY.M24A', 'DataRF/NN.SPCK', 'DataRF/SY.J23A', 'DataRF/ZI.10455', 'DataRF/ZI.10170', 'DataRF/YH.L07', 'DataRF/ZH.SM50', 'DataRF/ZO.UTTR2', 'DataRF/IM.PD04', 'DataRF/XZ.TLM21', 'DataRF/EM.IDE11', 'DataRF/ZH.SN13', 'DataRF/XZ.TSM12', 'DataRF/5A.NV140', 'DataRF/SY.H24A', 'DataRF/ZI.10535', 'DataRF/XZ.TLM07', 'DataRF/ZH.RCCE', 'DataRF/SY.I25A', 'DataRF/EM.MTD17', 'DataRF/ZI.11164', 'DataRF/EM.NVN10', 'DataRF/SY.M21A', 'DataRF/XZ.TLM23', 'DataRF/UU.VEC', 'DataRF/EM.MBB06', 'DataRF/XZ.CHP10']
#Additional functionality should be added to make this read from a text file

#-----------------------Download Function-------------------------------------------------------
def download_data(start, end, argv):

    # Station paramaters - (I chose the small box around Yellowstone given by Schmandt et al.(2012))
	#(Box D, see second page of paper)
    lonmin = -118 # longitude and latitude bounds for stations
    lonmax = -103
    latmin = 40
    latmax = 48
	
	#convert between date types
    starttime = UTCDateTime(start)
    endtime = UTCDateTime(end)

	# event parameters (as justified in Jennifer Jenkin's Thesis)
    radmin=30 # Minimum radius for teleseismic earthquakes
    radmax=90 # Maximum radius (further distances interact with the core-mantle boundary
    minmag=5.5 # Minumum magnitude of quake
    maxmag =8.0 # Maximum magnitude of quake
    lengthoftrace=30.*60. # 30 min

    client=IRISClient("IRIS") ####client = Client("IRIS")

    try:
        inventory = client.get_stations( minlatitude=latmin, maxlatitude=latmax,\
 minlongitude=lonmin, maxlongitude=lonmax, starttime=starttime, endtime=endtime)
    except:
        time.sleep(60)
        print('Failed to get inventory, retrying...')
        inventory = client.get_stations( minlatitude=latmin, maxlatitude=latmax,\
 minlongitude=lonmin, maxlongitude=lonmax, starttime=starttime, endtime=endtime)
        #A small number of Downloads might fail here causing code to crash, hence try except loop

#These variables are just for monitoring how the download script performed (and show progression of code at crash)
    Count =0
    Total_Station_Count=0
    Useful_Station_Count=0
    Network_Count = 0

    for nw in inventory:
        Network_Count += Network_Count
        #Get rid of the useless networks
        if nw.code in Useless_Networks:
            print('The Network', nw, 'is thought to be useless, so will not iterate through it')
        else:
            for sta in nw:
                Total_Station_Count += Total_Station_Count
                name= nw.code+'.'+sta.code
                # Make directories for data

                direc= 'DataRF/'+name
                if direc in Useless_List:
                    print('This station',name ,' is in the useless list, will not iterate through it')
                else:
                    if not os.path.exists(direc):
                        os.makedirs(direc)
                    direc=direc+'/Originals'
                    if not os.path.exists(direc):
                        os.makedirs(direc)   
                    # Find events
                    print(sta.code,nw.code)
                    mintime=sta.start_date
                    if mintime< starttime:
                        mintime=starttime
                    maxtime=sta.end_date
                    if maxtime> endtime:
                        maxtime = endtime

                        #get catalogue of events for the seismic station
#-----------------------------A very hacky way of trying to prevent a catastrophic download failure-------------------
                    try:	
                        cat=client.get_events(latitude=sta.latitude, longitude=sta.longitude,\
                                              minradius=radmin, maxradius=radmax, starttime=mintime,\
                                              endtime=maxtime,minmagnitude=minmag)
                    except: 
                        time.sleep(60)
                        print('Failed to get catalogue, retrying...')
                        print(sys.exc_info())
                        try:
                            Cat=client.get_events(latitude=sta.latitude, longitude=sta.longitude,\
                                                  minradius=radmin, maxradius=radmax, starttime=mintime,\
                                                  endtime=maxtime,minmagnitude=minmag)
                        except:
                            print('tried twice to get the catalogue, failed twice')
                            print('Currently failing on:', nw, name, 'Network Number: ', Network_Count,\
                                  'Station Number: ', Total_Station_Count)
                            time.sleep(600)
                            Cat=client.get_events(latitude=sta.latitude,longitude=sta.longitude,\
                                                  minradius = radmin, maxradius = radmax, starttime = mintime,\
                                                  endtime=maxtime,minmagnitude = minmag)
#---------------------------------------------------------------------------------------------------------------------------------

                    print('There are', len(cat), 'in the event catalogue')
                    ev_count = 0 # a variable for used for counting only the first useful download of a station
                    for ev in cat:
                        evtime=ev.origins[0].time
                        seis=[]
                        try:
                                #OK
                            print('downloading',nw.code, sta.code, "*", "BH*", evtime, evtime + lengthoftrace)
                            seis = client.get_waveforms(nw.code, sta.code, "*", "BH*", evtime,\
                                                            evtime + lengthoftrace, attach_response=True)
                        except:
                            print('Failed at waveform',nw.code, sta.code, "*", "BH*?", evtime, evtime + lengthoftrace)
                            print(sys.exc_info())

                                #Most Downloads fail here when trying to download the waveform as wrong data type
                        if len(seis)>1:
                            try:
                                evtlatitude=ev.origins[0]['latitude']
                                evtlongitude=ev.origins[0]['longitude']
                                evtdepth=ev.origins[0]['depth']/1.e3 # convert to km from m

                                # compute distances azimuth and backazimuth
                                distm, az, baz = obspy.geodetics.base.gps2dist_azimuth(evtlatitude,\
        evtlongitude,sta.latitude,sta.longitude)
                                distdg = distm/(6371.e3*np.pi/180.)

                                # remove station instrument response.
                                # + Output seismograms in displacement and filter with corner frequences fl2, fl3
                                try:
                                    fl1 = 0.005
                                    fl2 = 0.01
                                    fl3 = 2.
                                    fl4 = 20
                                    seis.remove_response(output='DISP', pre_filt=[fl1,fl2,fl3,fl4])

                                except:
                                    print('failed to remove response')
                                    print(sys.exc_info())



                                # Put in various event and station characteristics into the 'stats'-dictionairy
                                seis[0].stats['evla']=evtlatitude
                                seis[0].stats['evlo']=evtlongitude
                                seis[0].stats['evdp']=evtdepth #Might be needed for travel times
                                seis[0].stats['stla']=sta.latitude
                                seis[0].stats['stlo']=sta.longitude
                                seis[0].stats['dist']=distdg #Needed to compute travel times
                                seis[0].stats['az']=az
                                seis[0].stats['baz']=baz
                                seis[0].stats['station']=sta.code
                                seis[0].stats['network']=nw.code
                                seis[0].stats['event']=ev


                                # Write out to file
                                filename=direc+'/'+str(seis[0].stats.starttime)+'.PICKLE'
                                print('writing to ', filename)
                                Count = Count +1 # Add one to the seimograms
                                print(Count)
                                seis.write(filename,format='PICKLE')
                                ts = time.time()
                                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:S')
                                monitor = open('Output_Files/' + argv[0]+'-'+argv[1]+'.txt', 'w')
                                monitor.write('At\t'+ str(st)+'\tdownloaded\t'+str(name)+'\t' + 'Network_Count'+\
                                              str(Network_Count)+'\t'+'Count'+str(Count) +\
                                              'Station_Number'+ str(Total_Station_Count))
                                monitor.close
                                if ev_count == 0:
                                    ev_count += ev_count
                                    Useful_Station_Count += Useful_Station_Count
                            except: #failed for a seis >1
                                print('failed at ~at writing stage',nw.code, sta.code, "*", "BH*", evtime, evtime + lengthoftrace)
                                print(sys.exc_info())
        

	#all the loops have finished for the year
    print('Download Function Finished For:', starttime, endtime,'Seismograms:', str(Count),'Stations:', str(Total_Station_Count))
    print('There were', Network_Count, 'networks, which yielded a total of', Useful_Station_Count, 'Useful Stations')
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:S')
    monitor.write('At'+ str(st)+'Download Function Finished For:'+ str(starttime)+ str(endtime) +'Seismograms:'+\
                  str(Count)+'Stations:\t'+ str(Total_Station_Count)+'There were\t'+ str(Network_Count)+ \
                  'networks, which yielded a total of\t'+str(Useful_Station_Count)+ 'Useful Stations')
    monitor.close

#---------------------------Command Structure----------------------------------------------------------

def main(argv):
    print('Start Year:', argv[0], '\t End at beginning of Year:', argv[1]) #double check inputs match
    Start_Year_Int = int(argv[0]) #Convert between data types
    End_Year_Int = int(argv[1])
    Year_Range = End_Year_Int - Start_Year_Int
    print('Downloading over that', str(Year_Range), 'year range') #A further check
    print('Will output current station/network to', 'Output_Files/'+ \
          argv[0]+'-'+argv[1]+'.txt')
    for x in range(Year_Range):
         print(str(Start_Year_Int + x)+'-01-01', str(Start_Year_Int + x + 1)+'-01-01' ) #check if dates correct
    for x in range(Year_Range):
         download_data(str(Start_Year_Int + x)+'-01-01', str(Start_Year_Int + x + 1)+'-01-01', argv) #run program


if __name__ == "__main__": #this is required for command line arguments to work
    main(sys.argv[1:])

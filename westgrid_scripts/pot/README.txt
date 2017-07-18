Stuff here is related to extraction of POT numbers for _anal_ trees,
which can be done as follows:
./get_pot_from_list.sh anal production006/A/rdp/verify/v11r19/ND280/00008000_00008999 anal8_7005tmp.list > pot_7005.list

It calls root with get_pot_for_file.cpp script inside. The following lists were produced using _anal_ files of
verificatio production 6A, nd280 Software v11r19, Runs 2, 3:

pot6_2829.list	   6xxx range
pot7_4372.list	   7xxx range
pot8_7005.list	   8xxx range
pot8_7005ext.list  8xxx range with additional info: if there was a beam according to IRODS
		   ($ cat pot8_7005.list | ./pot2ext.awk > pot8_7005ext.list)
pot_run23.list     6xxx-8xxx range

pot_per_run.txt	   summary for comparison with DQ group POT table at http://www.t2k.org/nd280/runco/data/quality/inforuns
		   (cat pot_run23.list | ./pot_summ.awk >> pot_per_run.txt)

Aid scripts (see above for usage):
pot2ext.awk 	-add IRODS info
pot_summ.awk    -make summary

DV. Nov, 2013.



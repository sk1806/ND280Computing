class ProductionCondition:
    Name = "ProductionCondition"
    # __init__ is a class constructor
    def __init__(self):
        # These values are created
        # when the class is instantiated.
	self.software = "v11r21"
        self.production = "production005" #"production005"
        self.respin = "F" #"F" #"A"
        self.waterair = "water"  # air/water
        self.baskmagn = "magnet" # basket/magnet
        self.specialized = "" #nue/ncpizero/ccpizero/ncpiplus/ccpiplus/tpcgas
        self.verify = True
        self.oldneut = False  #False #True
        self.newoldneut = True
        self.nubar = False
        self.beam = 4 # run1, run2, run3, run4 

        if self.oldneut:
            self.generator = "old_neut" #"old-neut" #"neut_5.1.4.2"  (Thomas chose the name, I preferred the version one) (or old-neut)
        elif self.newoldneut:
            self.generator = "neut_5.1.4.3"
        else:
            self.generator = "neut"    #"neut_5.3.1" or neut_5.3.2
        if self.nubar:
            self.generator = "anti-" + self.generator  
        self.verify = "" #FOR PreProd: "verify/v11r21"
        self.geometry = "2010-11" #"2010-11"
        #self.comment = "prod6" + self.baskmagn + "201011" + self.waterair + "c" #"c"
        self.comment = "prod5" + self.baskmagn + "201002" + self.waterair + "c" #"c"
        if self.nubar:
            self.comment = "nubar_prod6a" + self.baskmagn + "201011" + self.waterair + "d" #"c"
        self.ram_disk = "/dev/shm/tfeusels/"
        self.base_dir = "/scratch/t/tanaka/T2K/neut_production"
        self.flux_dir = "/scratch/t/tanaka/T2K/neut_prod_tests/flux_files"        
        if self.baskmagn == "basket":
            self.flux_area = "5"
            if self.oldneut:
                #self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd5_flukain.0-499_neut_evtrate_2010-11-air_preprod6.root"
                #self.maxint_file_local = self.ram_disk + "nu.nd5_flukain.0-499_neut_evtrate_2010-11-air_preprod6.root"
                self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd5_flukain.0-199_neut5.1.4.2_evtrate_2010-11-water_prod6a.root"
                self.maxint_file_local = self.ram_disk + "nu.nd5_flukain.0-199_neut5.1.4.2_evtrate_2010-11-water_prod6a.root"
            else:
                if self.waterair == "water":
                    self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd5_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root"
                    self.maxint_file_local = self.ram_disk + "nu.nd5_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root"
                elif self.waterair == "air":
                    self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd5_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
                    self.maxint_file_local = self.ram_disk + "nu.nd5_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
                    if self.specialized == "tpcgas":
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd5_flukain.0-199_neut5.3.2.1_evtrate_tpcgas_half_prod6.root"
                        self.maxint_file_local = self.ram_disk + "nu.nd5_flukain.0-199_neut5.3.2.1_evtrate_tpcgas_half_prod6.root"
            #nubar:
            # nubar.nd5_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root
            # nubar.nd5_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root

            # current fluxfiles
            self.flux_base = "fluka_13a_nom_sk_nd5_250ka_iseq0-199_fix.root"
            #self.flux_base = "fluka_13a_nom_sk_nd5_m250ka_iseq0-199_fix.root"
        elif self.baskmagn == "magnet":
            self.flux_area = "6"
            if self.oldneut:
                #self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-499_neut_evtrate_2010-11-air_preprod6.root"
                #self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-499_neut_evtrate_2010-11-air_preprod6.root"
                self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.1.4.2_evtrate_2010-11-air_prod6a.root"
                self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.1.4.2_evtrate_2010-11-air_prod6a.root"
                if self.nubar:
                    if self.waterair == "water":
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nubar.nd6_flukain.0-199_neut5.1.4.2_evtrate_2010-11-water_preprod6c_newfluxfiles.root"
                        self.maxint_file_local = self.ram_disk + "nubar.nd6_flukain.0-199_neut5.1.4.2_evtrate_2010-11-water_preprod6c_newfluxfiles.root"
                    elif self.waterair == "air":
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nubar.nd6_flukain.0-199_neut5.1.4.2_evtrate_2010-11-air_preprod6c_newfluxfiles.root"
                        self.maxint_file_local = self.ram_disk + "nubar.nd6_flukain.0-199_neut5.1.4.2_evtrate_2010-11-air_preprod6c_newfluxfiles.root"
            elif self.newoldneut:
                if self.waterair == "water":
                    if self.geometry == "2010-02":
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.1.4.3_evtrate_2010-02-water_prod5f_flux11a.root"
                        self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.1.4.3_evtrate_2010-02-water_prod5f_flux11a.root"
                    else:
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.1.4.3_evtrate_2010-11-water_prod5f_flux11a.root"
                        self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.1.4.3_evtrate_2010-11-water_prod5f_flux11a.root"    
                elif self.waterair == "air":
                    self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.1.4.3_evtrate_2010-11-air_prod5f_flux11a.root"
                    self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.1.4.3_evtrate_2010-11-air_prod5f_flux11a.root"    
            else:
                if self.waterair == "water":
                    if self.nubar:
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nubar.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root"
                        self.maxint_file_local = self.ram_disk + "nubar.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root"
                    else:
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root"
                        self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-water_prod6a.root"
                        if self.geometry == "2010-02":
                            self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.3.2_evtrate_2010-02-water_prod6a.root"
                            self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.3.2_evtrate_2010-02-water_prod6a.root"
                elif self.waterair == "air":
                    if self.nubar:
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nubar.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
                        self.maxint_file_local = self.ram_disk + "nubar.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
                    else:
                        self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
                        self.maxint_file_local = self.ram_disk + "nu.nd6_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
            if self.nubar:
                self.flux_base = "fluka_13a_nom_nd6_m250ka_new_iseq0-199_fix.root"
            elif self.newoldneut:
                self.flux_base = "fluka_11a_nom_nd6_iseq0-249.root"
            else:
                self.flux_base = "fluka_13a_nom_nd6_250ka_new_iseq0-199_fix.root"
                #self.flux_base = "fluka_13a_nom_nd6_250ka_iseq0-199.root" #TODO : REPLACE BY _NEW

        
        thisrun = 90000000
        if self.nubar:
            thisrun -= 10000000
        if self.generator == "genie" :
            thisrun += 1000000
        elif self.generator == "old-neut":
            thisrun += 2000000
            #if self.beam == "beamc":
        thisrun += (self.beam * 100000) #Run1: 100000, Run2: 200000, Run3: 300000, Run4: 400000
            #else: print "self.beam == " + self.beam + " is not supported!!! "
            
        if self.waterair == "water" : 
            thisrun += 10000
        if self.baskmagn == "basket": 
            thisrun += 1000
            
        # 2000: nue, 3000: NC1pi0, 4000: CC1pi0, 5000: NC1pi+, 6000: CC1pi+)
        if self.specialized == "nue":
            thisrun += 1000
        elif self.specialized == "ncpizero":
            thisrun += 2000
        elif self.specialized == "ccpizero":
            thisrun += 3000
        elif self.specialized == "ncpiplus":
            thisrun += 4000
        elif self.specialized == "ccpiplus":
            thisrun += 5000
        elif self.specialized == "tpcgas":
            thisrun += 6000
        
        self.run = thisrun

        self.sample_dir = (self.base_dir + "/" + self.production + "/" + self.respin
                           + "/mcp/" + self.verify + "/"  + self.generator + "/" + self.geometry + "-" + self.waterair
                           #+ "/" + self.baskmagn + "/run" + str(self.beam))
                           + "/" + self.baskmagn)

        self.grid_dir = (self.production + "/" + self.respin
                           + "/mcp/" + self.verify + "/"  + self.generator + "/" + self.geometry + "-" + self.waterair
                         #+ "/" + self.baskmagn + "/run" + str(self.beam))
                         + "/" + self.baskmagn)
        
        if self.specialized == "":
            self.sample_dir += "/run" + str(self.beam)
            self.grid_dir += "/run" + str(self.beam)
        else:
            self.sample_dir += "/" + str(self.specialized)
            self.grid_dir += "/" + str(self.specialized)

        self.numcdir = self.sample_dir + "/numc"
        self.g4analdir = self.sample_dir + "/g4anal"

# A class for handling submission scripts.
class SubmissionScript:
    Name = "SubmissionScript"
    # __init__ is a class constructor                                                                            
    def __init__(self,directory,run,subrun,walltime,conditions,numc):
        # These values are created                                                                               
        # when the class is instantiated.                                                                        
        self.conditions = conditions
        self.numc = numc
        self.filename = directory + "/neut_numc_submit_" + str(run) + "_" + str(subrun) +".sh"
        self.fileContents = "#!/bin/bash \n" 

        if numc == True :
            self.fileContents += "#PBS -l nodes=1:ppn=8,walltime=" + walltime +"\n"  
        else :
            self.fileContents += "#PBS -l nodes=1:m32g:ppn=8,walltime=" + walltime +"\n"
            
        self.fileContents += "#PBS -N prod006neut."+str(run)+"."+str(subrun)+"\n"
        self.fileContents += "source /home/s/soser/tfeusels/setup_"+conditions.software + ".sh\n"
        self.fileContents += "cd " + directory + "\n"
        
        self.fileContents += "mkdir -p " + conditions.ram_disk + "\n"        
        if numc == True : 
            self.fileContents += "cp " + conditions.flux_dir + "/"+ conditions.flux_base + "    " +conditions.ram_disk + "/. \n"
            self.fileContents += "cp " + conditions.maxint_file + "    " +conditions.ram_disk + "/. \n"
            self.fileContents += "cd " + conditions.ram_disk +"\n"


        self.fileContents += """
ssh -N -f -L 11111:t2kcaldb.triumf.ca:3306 datamover1
ssh -N -f -L 22222:neut08.triumf.ca:3306 datamover1
export ENV_TSQL_URL=mysql://127.0.0.1:11111/nd280calib
export ENV_GSC_TSQL_URL=mysql://127.0.0.1:22222/t2kgscND280
function cleanup_ramdisk {
    echo -n "Cleaning up ramdisk directory /dev/shm/tfeusels on "
    date
    rm -rf /dev/shm/tfeusels
    echo -n "done at "
    date
}
trap "cleanup_ramdisk" TERM
"""

    def add_thread(self,cfg_dir,cfg_file,global_inputfile,local_inputfile):
        
        self.fileContents += "(\n"
        self.fileContents += "cd " + cfg_dir +"\n"
        self.fileContents += "cp " + global_inputfile + " " + local_inputfile + "\n"
        self.fileContents += "runND280 -c " + cfg_file  #+">& /dev/null \n"
        self.fileContents += ")&\n"

    def add_numc_thread(self,cfg_dir,cfg_file,ram_dir,subrun):

        self.fileContents += "(\n"
        #self.fileContents += "cd " + cfg_dir +"\n"
        #self.fileContents += "cd " + ram_dir +"\n"  #where I added the subrun to ram_dir...if I want 8*900 files on ram_disk

        self.fileContents += "cp " + cfg_dir + "/" + cfg_file + " " + ram_dir + "\n"
        if self.conditions.baskmagn == "basket":
            if self.conditions.specialized == "ncpiplus" or self.conditions.specialized == "tpcgas":
                self.fileContents += "timeout 6000 runND280 -c " + cfg_file  # output is in .log file
            else:
                #self.fileContents += "timeout 2000 runND280 -c " + cfg_dir + "/" + cfg_file
                self.fileContents += "timeout 2000 runND280 -c " + cfg_file  # output is in .log file

        elif self.conditions.baskmagn == "magnet":
            #self.fileContents += "timeout 6200 runND280 -c " + cfg_dir + "/" + cfg_file  # output is in .log file
            self.fileContents += "timeout 6200 runND280 -c " + cfg_file

        self.fileContents += ")&\n"
        # attempt to prevent stuck jobs, because maybe they access the same flux-and 
        # eventrate file at exactly the same time, some offset using sleep might solve this
        self.fileContents += "sleep 20\n" 


    def add_wait(self):
        self.fileContents += "wait\n"

    def add_wait_and_check_exitcode(self):
        # Maybe too complicated to a) check whether job exists/is still running
        #                          b) wait until it's finished and return exit code
        # Goal: check elegantly which of the eight jobs actually timed out and print the name
        self.fileContents += "for JOB in `seq 1 8`\n"
        self.fileContents += "do\n"
        self.fileContents += "  jobs %${JOB} &> /dev/null\n"
        self.fileContents += "  if [ `echo $?` == 0 ]\n"   #job is (still) running
        self.fileContents += "  then \n"
        self.fileContents += "    JOB_NAME=`jobs %${JOB}`\n"
        self.fileContents += "    wait %${JOB}\n"          #wait until it's finished and return exit code of job
        self.fileContents += "    if [ `echo $?` == 124 ]\n"
        self.fileContents += "    then \n"
        self.fileContents += "      echo \"${JOB_NAME}: TIMED OUT\"\n"
        self.fileContents += "    fi\n"
        self.fileContents += "  JOB_NAME=\"\"\n"           #reset var
        self.fileContents += "  fi\n"
        self.fileContents += "done\n"

    def clean_softlinks(self,path,subrun):
        # when the wait is done: clean all the directories (or fail the disk quota on total nr of files)
        # new Neut does produce a lot of symlinks...
        self.fileContents += "rm %s/%i/Nieves_* \n" %(path,subrun)
        self.fileContents += "rm %s/%i/s*.dat \n" %(path,subrun)
        self.fileContents += "rm %s/%i/cc* \n" %(path,subrun)
        self.fileContents += "rm %s/%i/ncel* \n" %(path,subrun)
        self.fileContents += "rm %s/%i/nuc* \n" %(path,subrun)
        self.fileContents += "rm %s/%i/9*.dat \n" %(path,subrun)
        
    def clean_directory(self,path,subrun):
        self.fileContents += "rm %s/%i/oa_nt*.root \n" %(path,subrun)
        self.fileContents += "rm %s/%i/oa_nt*.dat \n" %(path,subrun)
        self.fileContents += "rm %s/%i/oa_nt*.log \n" %(path,subrun)
        self.fileContents += "rm %s/%i/neut.card \n" %(path,subrun)
        
    def copy_output(self,ram_dir,path,run,subrun):
        #### TODO: replace by rsync !!!!
        self.fileContents += "cp %s/oa_nt*_%i-%04i_*.root %s/%i \n" % (ram_dir,run,subrun,path,subrun) 
        self.fileContents += "cp %s/oa_nt*_%i-%04i_*.log %s/%i \n" % (ram_dir,run,subrun,path,subrun) 
        self.fileContents += "cp %s/oa_nt*_%i-%04i_*_catalogue.dat %s/%i \n" % (ram_dir,run,subrun,path,subrun) 
        self.fileContents += "cp %s/neut.card %s/%i \n" % (ram_dir,path,subrun) 



    def write_file(self):
        self.fileContents += """                                                                                
wait
"""

        self.fileContents += "cleanup_ramdisk \n"



        try:
            subFile = open(self.filename,"w")
            subFile.write(self.fileContents)

        except:
            print "can't write submission script: " + self.filename

        return self.filename


class ProductionCondition:
    Name = "ProductionCondition"
    # __init__ is a class constructor
    def __init__(self):
        # These values are created
        # when the class is instantiated.
	self.software = "v11r31"
        self.production = "production006"
        self.respin = "B"
        self.waterair = "air"
        #self.waterair = "water"
        self.verify = True
        self.beam = "beamc"
        self.beamdir = "run3"
       	#self.generator = "old-neut"
        #self.generator = "neut"
        self.generator = "anti-neut"
        #self.verify = "verify/v11r21"
        self.verify = ""
        self.geometry = "2010-11"
        self.comment = "prod6sand201011"+ self.waterair + "run3"
        self.ram_disk = "/dev/shm/lindner/"
        self.base_dir = "/scratch/t/tanaka/T2K/sand_production"
        #self.maxint_file = "/scratch/t/tanaka/T2K/sand_muon_tests/sand_output/neut_nd280_world_setup_flux_sand_0-499.root"
        #self.maxint_file_local = self.ram_disk + "neut_nd280_world_setup_flux_sand_0-499.root"
        if(self.generator == "old-neut"):
            self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd13_world_setup_flukain.0-199_neut5.1.4.2_evtrate_2010-11-air_prod6a.root"
            self.maxint_file_local = self.ram_disk + "nu.nd13_world_setup_flukain.0-199_neut5.1.4.2_evtrate_2010-11-air_prod6a.root"
            
            self.genev_setup = "/project/t/tanaka/T2K/neut/branches/5.1.4.2_nd280_ROOTv5r34p09n01/src/neutgeom/setup.sh"
	if(self.generator == "neut"):
		self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nu.nd13_world_setup_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
		self.maxint_file_local = self.ram_disk + "nu.nd13_world_setup_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"

		self.genev_setup = "/project/t/tanaka/T2K/neut/branches/5.1.4.2_nd280_ROOTv5r34p09n01/src/neutgeom/setup.sh"

	if(self.generator == "anti-neut"):
		self.maxint_file = "/scratch/t/tanaka/T2K/neut_prod_tests/eventrate_files/nubar.nd13_world_setup_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"
		self.maxint_file_local = self.ram_disk + "nubar.nd13_world_setup_flukain.0-199_neut5.3.2_evtrate_2010-11-air_prod6a.root"

		self.genev_setup = "/project/t/tanaka/T2K/neut/branches/5.1.4.2_nd280_ROOTv5r34p09n01/src/neutgeom/setup.sh"

        #self.flux_dir = "/scratch/t/tanaka/T2K/sand_muon_tests/flux_files/"
        self.flux_dir = "/scratch/t/tanaka/T2K/neut_prod_tests/flux_files/"

        self.flux_base = "nu.nd13_flukain"
	#        self.flux_file = "fluka_11a_nom_nd13_250ka_0-99.root"
	self.flux_file = "fluka_13a_nom_nd13_250ka_iseq0-199_fix.root"
        if(self.generator == "anti-neut"):
            self.flux_file = "fluka_13a_nom_nd13_m250ka_iseq0-199_fix.root"
        
        thisrun = 90007000
	if self.generator == "old-neut":
            thisrun += 2000000
	if self.generator == "anti-neut":
            thisrun = 80007000
        if self.generator == "genie" :
            thisrun += 1000000
        if self.beam == "beamc":
            thisrun += 300000
        else:
            print "self.beam == " + self.beam + " is not supported!!! "
            
        if self.waterair == "water" : 
            thisrun += 10000
 

        self.run = thisrun

        self.sample_dir = (self.base_dir + "/" + self.production + "/" + self.respin
                           + "/mcp/" + self.verify + "/"  + self.generator + "/" + self.geometry + "-" + self.waterair
                           + "/sand/" + self.beamdir)

        self.numcdir = self.sample_dir + "/numc"
        self.g4analdir = self.sample_dir + "/g4anal"

        self.grid_dir = (self.production + "/" + self.respin
                           + "/mcp/" + self.verify + "/"  + self.generator + "/" + self.geometry + "-" + self.waterair
                           + "/sand/" + self.beamdir)




# A class for handling submission scripts.
class SubmissionScript:
    Name = "SubmissionScript"
    # __init__ is a class constructor                                                                            
    def __init__(self,directory,run,subrun,walltime,conditions,numc):
        # These values are created                                                                               
        # when the class is instantiated.                                                                        
        self.conditions = conditions
        self.numc = numc
        self.filename = directory + "/sand_numc_submit_" + str(run) + "_" + str(subrun) +".sh"
        self.fileContents = "#!/bin/bash \n" 

        if numc == True :
            self.fileContents += "#PBS -l nodes=1:ppn=8,walltime=" + walltime +"\n"  
        else :
            #self.fileContents += "#PBS -l nodes=1:m32g:ppn=8,walltime=" + walltime +"\n"
            self.fileContents += "#PBS -l nodes=1:ppn=8,walltime=" + walltime +"\n"
        self.fileContents += "#PBS -N prod005sand."+str(run)+"."+str(subrun)+"\n"
        self.fileContents += "source /home/s/soser/tlindner/sand_tests/setup_"+conditions.software + ".sh\n"
        self.fileContents += "cd " + directory + "\n"
        
        self.fileContents += "mkdir -p /dev/shm/lindner\n"        
        if numc == True : 
            self.fileContents += "cp " + conditions.maxint_file + " " + conditions.maxint_file_local +"\n"
            self.fileContents += "cp " + conditions.flux_dir + "/" + conditions.flux_file + " /dev/shm/lindner/.\n"

        self.fileContents += """
ssh -N -f -L 11111:t2kcaldb.triumf.ca:3306 datamover1
ssh -N -f -L 22222:neut08.triumf.ca:3306 datamover1
export ENV_TSQL_URL=mysql://127.0.0.1:11111/nd280calib
export ENV_GSC_TSQL_URL=mysql://127.0.0.1:22222/t2kgscND280
function cleanup_ramdisk {
    echo -n "Cleaning up ramdisk directory /dev/shm/lindner on "
    date
    rm -rf /dev/shm/lindner
    echo -n "done at "
    date
}
trap "cleanup_ramdisk" TERM
"""

    def add_thread(self,cfg_dir,cfg_file,global_inputfile,local_inputfile):
        
        self.fileContents += "(\n"
        self.fileContents += "cd " + cfg_dir +"\n"
        self.fileContents += "cp " + global_inputfile + " " + local_inputfile + "\n"
        self.fileContents += "runND280 -c " + cfg_file +">& /dev/null \n"
        self.fileContents += ")&\n"

    def add_numc_thread(self,cfg_dir,cfg_file,ram_dir):

        self.fileContents += "(\n"
        #self.fileContents += "mkdir -p " + ram_dir +"\n"
        #self.fileContents += "cd " + ram_dir +"\n"
        self.fileContents += "cd " + cfg_dir +"\n"
        #self.fileContents += "cp " + global_inputfile + " " + local_inputfile +"\n"
        self.fileContents += "runND280 -c " + cfg_file +">& /dev/null \n"
#        self.fileContents += "cp " + ram_dir + "/* " + cfg_dir + "/.  \n"
	self.fileContents += "rm [0-9,a-n,p-z]*dat \n"
        self.fileContents += ")&\n"
	


    def write_file(self,numc):
 



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


#!/usr/bin/env python

import ND280Configs
## cfg = ND280Configs.ND280Config('gnmc','test_gnmc.cfg')
## cfg.ListOptions()
## ##     comment = 
## ##     cmtpath = environmet
## ##     random_seed = 
## ##     p0d_water_fill = 
## ##     neutrino_type = beam
## ##     genie_paths = 
## ##     cmtroot = environment
## ##     flux_file = 
## ##     flux_tree = h3002
## ##     run_number = 
## ##     baseline = 
## ##     genie_setup_script = /data/t2k/ND280_soft//GENIE/setup.sh
## ##     nd280ver = 
## ##     master_volume = 
## ##     subrun = 
## ##     genie_xs_table = 
## ##     pot = 
## cfg.options['random_seed']='3456532423'
## cfg.options['p0d_water_fill']='1'      
## cfg.options['genie_paths']='/some/path/geniepaths.root'
## cfg.options['flux_file']='/data/still/FluxFiles/10a/nd6/flux_10a_nd6_1/nu.nd6_horn250ka.1.root'
## cfg.options['genie_paths']='/data/still/GENIE/test/genie_nd280_Magnet_paths_2.6.0.xml'
## cfg.options['run_number']='91000099'
## cfg.options['subrun']='0'
## cfg.options['genie_xs_table']='/data/still/GENIE/test/gxspl-t2k-v2.6.0.xml'
## cfg.options['baseline']='2010-02'
## cfg.options['master_volume']='Magnet'
## cfg.options['nd280ver']='v7r21p1'
## cfg.options['pot']='5E+17'
## cfg.CreateConfig()

cfg2 =  ND280Configs.ND280Config('raw','test_raw.cfg')
cfg2.ListOptions()
## Defaults
## cfg2.options['module_list'] = 'oaUnpack oaCalib oaRecon oaAnalysis'
## cfg2.options['cmtpath'] = 'environmet'
## cfg2.options['register_catalogue_files'] = '0'
## cfg2.options['use_grid'] = '1'
## cfg2.options['cmtroot'] = 'environment'
## cfg2.options['register_files'] = '1'

cfg2.options['comment'] = ''
cfg2.options['event_select'] = 'beam'
cfg2.options['storage_address'] = 'srm://se03.esc.qmul.ac.uk' 
cfg2.options['midas_file'] = '/grid/t2k.org/nd280/raw/ND280/ND280/00004000_00004999/nd280_00004999_0001.daq.mid.gz'
cfg2.options['register_address'] = '/grid/t2k.org/nd280/v7r19p1/cali/ND280/ND280/00004000_00004999/'
cfg2.options['nd280ver'] = 'v7r19p1'
cfg2.CreateConfig()

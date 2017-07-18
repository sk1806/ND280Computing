/* Usage example:
$ root -l -n -q 'get_pot_for_file.cpp("/global/scratch/t2k/production006/A/rdp/verify/v11r19/ND280/00008000_00008999/anal/oa_nd_spl_00008550-0010_igsfovtqcyra_anal_000_v11r19-wg-bugaboo-bsdv01_2.root")'
*/

void get_pot_for_file(std::string name){

  TFile *f = new TFile(name.c_str());


    TTree *t = (TTree*)f->Get("HeaderDir/BeamSummaryData;1");
    TTree *t2 = (TTree*)f->Get("HeaderDir/BasicDataQuality;1");
    
    if(!t || !t2)return;

    std::cout << "Got it! " << std::endl;
    
    double pot;
    //gROOT->MakeProject("BeamSummaryData");
    //f->MakeProject("libDir","*","update+");

    gSystem->Load("libDir/libDir.so");
    
    TClonesArray *pointer = new TClonesArray("ND::TBeamSummaryDataModule::TBeamSummaryData",100);
    t->SetBranchAddress("BeamSummaryData",&pointer);
    
    int ND280OffFlag;
    t2->SetBranchAddress("ND280OffFlag",&ND280OffFlag);

    double total_pot = 0, total_pot_with_dataquality = 0;
    
    for(int i = 0; i < t->GetEntries(); i++){
      t->GetEntry(i);
      t2->GetEntry(i);
      //std::cout << pot << std::endl;
      ND::TBeamSummaryDataModule::TBeamSummaryData * data = (ND::TBeamSummaryDataModule::TBeamSummaryData*)pointer->At(0);
      if(data && data->GoodSpillFlag){
        total_pot += data->CT5ProtonsPerSpill;
        if(ND280OffFlag==0)
          total_pot_with_dataquality += data->CT5ProtonsPerSpill;
                 
      }
    }

    std::cout << "Total POT for file: " << total_pot << std::endl;
    std::cout << "Total POT with data quality (ND280OffFlag==0) " << total_pot_with_dataquality << std::endl;
    std::cout << total_pot << " " << total_pot_with_dataquality << std::endl;
  }



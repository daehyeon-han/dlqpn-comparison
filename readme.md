This repository contains the source code, pre-trained models, and dataset of the paper 'Key factors for quantitative precipitation nowcasting using ground weather radar data based on deep learning'. 

### data.zip: 
There are two dataset; CAPPI (constant altitude plan position indicator) radar precipitation and HSR-based (hybrid surface rainfall) MAPLE prediction up to 120 minutes in mm/h for 05-10 Aug. 2020 KST. CAPPI radar dataset was used to evaluate the performances over the heavy rainfall event, and MAPLE was used just for visual comparison. Both datasets were provided by KMA and Korea Public Data Portal. 

https://radar.kma.go.kr

https://www.data.go.kr/en/data/15068574/fileData.do



### models.zip: 
Pre-trained models can be used to generate the future precipitation sequence. The meaning of file name is as follows.

-model_lbAA_fctBB_modeCC_DD_fc_EEmin.py

AA: input sequence length in minutes (30, 60, 90, 120)

BB: output sequence length in minutes (30, 60, 90, 120)

CC: prediction design. 10 - single target prediction; 11 - recursive prediction, 20 - multi target prediction

DD: model type (unet or convlstm)

EE: lead time in minutes (10-120)


### models.py
It contains the implementation of U-Net and ConvLSTM models used in the study.

requirements: Tensorflow 2.4.0


The detailed description about the code and data can be found in the preprints to be uploaded soon when GMD discussion starts.


Please visit Zenodo repository to download the dataset (5.3GB) and pre-trained models (15.9GB).
https://doi.org/10.5281/zenodo.7312779
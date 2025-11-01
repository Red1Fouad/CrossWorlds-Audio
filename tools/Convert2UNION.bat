@echo OFF
:Start
echo (Sonic Racing: Crossworlds v1.1.2)
echo.
echo Enter the name of the .acb you're modifying (without file extension, case sensitive)
echo Example: BGM_STG1001
echo.
echo Type "Help" for a list of acb files
echo.
set /p input= acb file name: 
goto option-%input%

:option-BGM
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13437671753685516182
pause
exit
:option-BGM_BONUS01
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5403683782915097180
pause
exit
:option-BGM_BONUS02
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6922027834726244234
pause
exit
:option-BGM_EXTND04
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 278538860811558654
pause
exit
:option-BGM_EXTND05
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5393367454849679208
pause
exit
:option-BGM_EXTND10
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14635606071112671560
pause
exit
:option-BGM_EXTND11
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 11240118043429644306
pause
exit
:option-BGM_EXTND12
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13441957704310774890
pause
exit
:option-BGM_EXTND23
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3555604298289421126
pause
exit
:option-BGM_GP_01_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6160901282803046330
pause
exit
:option-BGM_GP_02_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9881225061630473182
pause
exit
:option-BGM_GP_03_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8041200513530155376
pause
exit
:option-BGM_GP_04_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 478124547315176610
pause
exit
:option-BGM_GP_05_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4942948040289925702
pause
exit
:option-BGM_GP_06_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13823274777452393750
pause
exit
:option-BGM_GP_07_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 7827766345515880648
pause
exit
:option-BGM_GP_08_FINAL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8274136641905236186
pause
exit
:option-BGM_JBM0001
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 7027872705325931320
pause
exit
:option-BGM_JBM0002
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10648005092403820396
pause
exit
:option-BGM_JBM0003
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17223048755760679712
pause
exit
:option-BGM_JBM0004
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2312872515155355060
pause
exit
:option-BGM_JBM0005
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3943608779731507632
pause
exit
:option-BGM_JBM0006
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10309600992019062454
pause
exit
:option-BGM_JBM0007
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16563104225221900232
pause
exit
:option-BGM_JBM0008
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1342834578298001876
pause
exit
:option-BGM_JBM0009
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10695063949650790808
pause
exit
:option-BGM_JBM0010
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13281989669573639792
pause
exit
:option-BGM_JBM0011
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14356978613715510940
pause
exit
:option-BGM_JBM0012
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15617231097940621792
pause
exit
:option-BGM_JBM0013
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16925156170457573750
pause
exit
:option-BGM_JBM0014
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6295810644648937562
pause
exit
:option-BGM_JBM0015
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8619088084455312560
pause
exit
:option-BGM_JBM0016
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9946278284878209860
pause
exit
:option-BGM_JBM0017
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 18105236188019112076
pause
exit
:option-BGM_JBM0018
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 476993851545146748
pause
exit
:option-BGM_JBM0019
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16529753783350437378
pause
exit
:option-BGM_JBM0020
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2452304660081365740
pause
exit
:option-BGM_JBM0021
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 739274603436730132
pause
exit
:option-BGM_JBM0022
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17892178918594847302
pause
exit
:option-BGM_JBM0023
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10345966622610604940
pause
exit
:option-BGM_JBM0024
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6917505051646124786
pause
exit
:option-BGM_JBM0025
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 7704304007505437250
pause
exit
:option-BGM_JBM0026
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12509039195224984100
pause
exit
:option-BGM_JBM0027
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10940857929901647742
pause
exit
:option-BGM_JBM0028
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17648786396019199306
pause
exit
:option-BGM_JBM0029
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9882215691265353830
pause
exit
:option-BGM_JBM0030
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16347645498122426520
pause
exit
:option-BGM_JBM0031
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 721140171300814652
pause
exit
:option-BGM_JBM0032
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13359383779971993426
pause
exit
:option-BGM_JBM0033
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4380039646645455152
pause
exit
:option-BGM_JBM0034
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6295056847468917654
pause
exit
:option-BGM_JBM0035
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12640933368350795700
pause
exit
:option-BGM_JBM0036
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 11410262340097048162
pause
exit
:option-BGM_JBM0037
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16292768536804958600
pause
exit
:option-BGM_JBM0038
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 985919147187318500
pause
exit
:option-BGM_JBM0039
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2549200730840525456
pause
exit
:option-BGM_JBM0040
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13697551047901890628
pause
exit
:option-BGM_JBM0041
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16306993916905625326
pause
exit
:option-BGM_JBM0042
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17574407474340925304
pause
exit
:option-BGM_JBM0043
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13333711376035878866
pause
exit
:option-BGM_JBM0044
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15196393139352231600
pause
exit
:option-BGM_JBM0045
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9607120387313432010
pause
exit
:option-BGM_JBM0046
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9949810438323448660
pause
exit
:option-BGM_JBM0047
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14249766214890933252
pause
exit
:option-BGM_JBM0048
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12741598425010054956
pause
exit
:option-BGM_JBM0051
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5755796298675362680
pause
exit
:option-BGM_JBM0052
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15875085833071797254
pause
exit
:option-BGM_JBM0053
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10531843893738715338
pause
exit
:option-BGM_JBM0054
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1812615887083412250
pause
exit
:option-BGM_JBM0061
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 408785373442181224
pause
exit
:option-BGM_JBM0062
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6479049625646978282
pause
exit
:option-BGM_JBM0063
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14643284109048019854
pause
exit
:option-BGM_JBM0064
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 18327479089738764960
pause
exit
:option-BGM_JBM0065
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5955898949904139804
pause
exit
:option-BGM_JBM0066
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 7369668893020778848
pause
exit
:option-BGM_JBM0067
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12021123454303658246
pause
exit
:option-BGM_JBM0073
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3555604298289421126
pause
exit
:option-BGM_STG1001
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 11066441593317001650
pause
exit
:option-BGM_STG1003
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9460010204452073036
pause
exit
:option-BGM_STG1005
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9123113698427354910
pause
exit
:option-BGM_STG1016
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14598863541931119120
pause
exit
:option-BGM_STG1017
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5275321763234524380
pause
exit
:option-BGM_STG1018
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1087995031886906046
pause
exit
:option-BGM_STG1020
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4312961864312519490
pause
exit
:option-BGM_STG1021
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3020252801531114906
pause
exit
:option-BGM_STG1022
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5966355344104706990
pause
exit
:option-BGM_STG1023
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 129921083590159864
pause
exit
:option-BGM_STG1024
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4405712050581569712
pause
exit
:option-BGM_STG1025
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8672080552822730710
pause
exit
:option-BGM_STG1026
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14142413749931206350
pause
exit
:option-BGM_STG1027
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1661736718321953736
pause
exit
:option-BGM_STG1028
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12707257353503711454
pause
exit
:option-BGM_STG1029
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 11854888209671503144
pause
exit
:option-BGM_STG1030
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1640210198875948670
pause
exit
:option-BGM_STG1031
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9568730197636690540
pause
exit
:option-BGM_STG1032
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14928458908610498906
pause
exit
:option-BGM_STG1033
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8079967601796906800
pause
exit
:option-BGM_STG1034
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14230641153120137124
pause
exit
:option-BGM_STG1035
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9402118054414525484
pause
exit
:option-BGM_STG1036
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10732700342147512370
pause
exit
:option-BGM_STG1037
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12632361467100278284
pause
exit
:option-BGM_STG2001
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10820787679201293930
pause
exit
:option-BGM_STG2002
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14110710968554932526
pause
exit
:option-BGM_STG2003
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2828581985417705984
pause
exit
:option-BGM_STG2004
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5137634045123414256
pause
exit
:option-BGM_STG2005
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14069165524022962210
pause
exit
:option-BGM_STG2007
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 201898547593224928
pause
exit
:option-BGM_STG2009
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1847613989450064134
pause
exit
:option-BGM_STG2010
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15929962794389265174
pause
exit
:option-BGM_STG2011
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3646469991608421578
pause
exit
:option-BGM_STG2012
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15776305269362587768
pause
exit
:option-BGM_STG2014
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17482411085251894990
pause
exit
:option-BGM_STG2015
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1658204564876714936
pause
exit
:option-BGM_STG2016
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2098921382415921164
pause
exit
:option-BGM_STG2017
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5764228133790730882
pause
exit
:option-BGM_STG2019
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13632734657109014690
pause
exit

:option-SE_ADV
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 14329938681554505778
pause
exit
:option-SE_COURSE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 16116076897972236312
pause
exit
:option-SE_DSH_51_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 9510978113734292202
pause
exit
:option-SE_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 14759068409123114958
pause
exit
:option-SE_EXTND03_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9216240783286415086
pause
exit
:option-SE_EXTND03_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 9510978113734292202
pause
exit
:option-SE_EXTND03_HORN
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10878679829238841482
pause
exit
:option-SE_EXTND04_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9374184258938351200
pause
exit
:option-SE_EXTND04_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 8178371266916106332
pause
exit
:option-SE_EXTND04_HORN
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16776161494646165006
pause
exit
:option-SE_EXTND04_STG1503
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 633052834247033092
pause
exit
:option-SE_EXTND05_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15745076152896035424
pause
exit
:option-SE_EXTND05_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 13976415337753911988
pause
exit
:option-SE_EXTND05_HORN
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12610221216609402524
pause
exit
:option-SE_EXTND05_STG1506
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15941032919634703054
pause
exit
:option-SE_EXTND10_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10633919778438302884
pause
exit
:option-SE_EXTND10_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 8611410046519964266
pause
exit
:option-SE_EXTND10_HORN
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3519992464877898548
pause
exit
:option-SE_EXTND11_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 7915476783979652254
pause
exit
:option-SE_EXTND11_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 12387224517709729732
pause
exit
:option-SE_EXTND11_HORN
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8161507596685369928
pause
exit
:option-SE_EXTND12_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 12609090520839372662
pause
exit
:option-SE_EXTND12_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 2694189588296973920
pause
exit
:option-SE_EXTND12_HORN
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4485507618655132284
pause
exit
:option-SE_ITEM
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 14573568036585014514
pause
exit
:option-SE_MACHINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 8898469339032493088
pause
exit
:option-SE_MENU
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 7234382632584877662
pause
exit
:option-SE_MOVIE_SOUND
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 6626159808508337256
pause
exit
:option-SE_OBJ_COMMON
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 12952157470439399266
pause
exit
:option-SE_OBJ_STG1001
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 12108973958902579066
pause
exit
:option-SE_OBJ_STG1003
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 11523268283906924374
pause
exit
:option-SE_OBJ_STG1005
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 2916809388606636758
pause
exit
:option-SE_OBJ_STG1016
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10340173077625306416
pause
exit
:option-SE_OBJ_STG1017
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 14650962146983368148
pause
exit
:option-SE_OBJ_STG1018
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10228437895720609280
pause
exit
:option-SE_OBJ_STG1020
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 15171851431186146902
pause
exit
:option-SE_OBJ_STG1021
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 2250694414492548800
pause
exit
:option-SE_OBJ_STG1022
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10475222505606346862
pause
exit
:option-SE_OBJ_STG1023
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 895193520003467262
pause
exit
:option-SE_OBJ_STG1024
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 7894327163123657142
pause
exit
:option-SE_OBJ_STG1025
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10035873216292031236
pause
exit
:option-SE_OBJ_STG1026
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 17499651654072641348
pause
exit
:option-SE_OBJ_STG1027
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 13547285610185302808
pause
exit
:option-SE_OBJ_STG1028
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 11350108798519440886
pause
exit
:option-SE_OBJ_STG1029
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 17967688536043151166
pause
exit
:option-SE_OBJ_STG1030
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 17410056722658819972
pause
exit
:option-SE_OBJ_STG1031
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 12513325145850242808
pause
exit
:option-SE_OBJ_STG1032
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 2762258000264790230
pause
exit
:option-SE_OBJ_STG1033
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 4448625023338430630
pause
exit
:option-SE_OBJ_STG1034
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10573626170725546394
pause
exit
:option-SE_OBJ_STG1035
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 13561370924150820320
pause
exit
:option-SE_OBJ_STG1036
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 1642988555141167562
pause
exit
:option-SE_OBJ_STG1037
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 7287235034817146598
pause
exit
:option-SE_OBJ_STG2001
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 5739826491759795398
pause
exit
:option-SE_OBJ_STG2002
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 13680547311536005010
pause
exit
:option-SE_OBJ_STG2003
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10086227394529379708
pause
exit
:option-SE_OBJ_STG2004
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 12341533188687649922
pause
exit
:option-SE_OBJ_STG2005
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 704416567205227462
pause
exit
:option-SE_OBJ_STG2007
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 10542677186529292478
pause
exit
:option-SE_OBJ_STG2009
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 7421767498073027876
pause
exit
:option-SE_OBJ_STG2010
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 17994728468204156328
pause
exit
:option-SE_OBJ_STG2011
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 8535900429071660402
pause
exit
:option-SE_OBJ_STG2012
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 568613342044167108
pause
exit
:option-SE_OBJ_STG2014
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 18262662698945889022
pause
exit
:option-SE_OBJ_STG2015
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 14132474320455798332
pause
exit
:option-SE_OBJ_STG2016
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 13719314399802756434
pause
exit
:option-SE_OBJ_STG2017
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 11095269252108345056
pause
exit
:option-SE_OBJ_STG2019
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 15536304834097029358
pause
exit
:option-SE_POW_51_ENGINE
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 6487481460762346484
pause
exit
:option-SE_PRIME_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3539634491373853844
pause
exit
:option-SE_SYS
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 6207346409005146048
pause
exit
:option-SE_WER_CHARA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10368246939236629914
pause
exit
:option-VIB_COMMON
VGAudioCli.exe -b -i input -o output --out-format adx --keycode 14086029194253698614
pause
exit

:option-VOICE_AMY
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6404293805378694326
pause
exit
:option-VOICE_AMYAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14923559226940369504
pause
exit
:option-VOICE_ANNOUNCE
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9343095208606948070
pause
exit
:option-VOICE_BIG
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14078868121043509488
pause
exit
:option-VOICE_BIGAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5891459457701273820
pause
exit
:option-VOICE_BLA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17961894991057852642
pause
exit
:option-VOICE_BLAAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9083969711570593532
pause
exit
:option-VOICE_CBT
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4384702495860723814
pause
exit
:option-VOICE_CHA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2922602933591935282
pause
exit
:option-VOICE_CHAAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16886765980780832280
pause
exit
:option-VOICE_CRE
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 11692421950939447582
pause
exit
:option-VOICE_CREAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14595848353211039488
pause
exit
:option-VOICE_DOD
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15114336179738609304
pause
exit
:option-VOICE_EGG
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9816785569427607198
pause
exit
:option-VOICE_EGGAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 15836835709530204998
pause
exit
:option-VOICE_EGP
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10803547110380547572
pause
exit
:option-VOICE_EGPAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 6514801525193650074
pause
exit
:option-VOICE_ESP
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16624388462569537370
pause
exit
:option-VOICE_ESPAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9594919566297964268
pause
exit
:option-VOICE_JET
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14445582915494451668
pause
exit
:option-VOICE_JETAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16821712757533095602
pause
exit
:option-VOICE_KNU
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5312818089596096728
pause
exit
:option-VOICE_KNUAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10457088073470431382
pause
exit
:option-VOICE_MET
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16757650163920239572
pause
exit
:option-VOICE_METAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1433560205481853114
pause
exit
:option-VOICE_OBT
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14292679187647794170
pause
exit
:option-VOICE_OCH
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17352918369801292328
pause
exit
:option-VOICE_OME
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14032799893431419724
pause
exit
:option-VOICE_OMEAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 7802707672624636782
pause
exit
:option-VOICE_ROU
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 9893802781235950878
pause
exit
:option-VOICE_ROUAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 10795869072445199278
pause
exit
:option-VOICE_SAG
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17822322779996692748
pause
exit
:option-VOICE_SAGAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3649625246463650424
pause
exit
:option-VOICE_SHA
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 5619142510014570892
pause
exit
:option-VOICE_SHAAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 2577651491041858908
pause
exit
:option-VOICE_SIL
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3867205298968034646
pause
exit
:option-VOICE_SILAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 17730843355632821602
pause
exit
:option-VOICE_SON
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14652986706068567132
pause
exit
:option-VOICE_SONAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 11835386249310697062
pause
exit
:option-VOICE_STO
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1138962941169125212
pause
exit
:option-VOICE_STOAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 4419420465957077270
pause
exit
:option-VOICE_TAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3190773996788528716
pause
exit
:option-VOICE_TAIAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 3064296470058005686
pause
exit
:option-VOICE_VEC
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13495046938997904566
pause
exit
:option-VOICE_VECAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 14222963115184788830
pause
exit
:option-VOICE_WAV
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 16971084331934514300
pause
exit
:option-VOICE_WAVAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 1643742352321187470
pause
exit
:option-VOICE_ZAV
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 13519588647163989264
pause
exit
:option-VOICE_ZAVAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 60441843582015264
pause
exit
:option-VOICE_ZAZ
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 967170984006532326
pause
exit
:option-VOICE_ZAZAI
VGAudioCli.exe -b -i input -o output --out-format hca --keycode 8756398903976412730
pause
exit

:option-Help
echo.
echo BGM
echo BGM_BONUS01
echo BGM_BONUS02
echo BGM_EXTND04
echo BGM_EXTND05
echo BGM_EXTND10
echo BGM_EXTND11
echo BGM_EXTND12
echo BGM_EXTND23
echo BGM_GP_01_FINAL
echo BGM_GP_02_FINAL
echo BGM_GP_03_FINAL
echo BGM_GP_04_FINAL
echo BGM_GP_05_FINAL
echo BGM_GP_06_FINAL
echo BGM_GP_07_FINAL
echo BGM_GP_08_FINAL
echo BGM_JBM0001
echo BGM_JBM0002
echo BGM_JBM0003
echo BGM_JBM0004
echo BGM_JBM0005
echo BGM_JBM0006
echo BGM_JBM0007
echo BGM_JBM0008
echo BGM_JBM0009
echo BGM_JBM0010
echo BGM_JBM0011
echo BGM_JBM0012
echo BGM_JBM0013
echo BGM_JBM0014
echo BGM_JBM0015
echo BGM_JBM0016
echo BGM_JBM0017
echo BGM_JBM0018
echo BGM_JBM0019
echo BGM_JBM0020
echo BGM_JBM0021
echo BGM_JBM0022
echo BGM_JBM0023
echo BGM_JBM0024
echo BGM_JBM0025
echo BGM_JBM0026
echo BGM_JBM0027
echo BGM_JBM0028
echo BGM_JBM0029
echo BGM_JBM0030
echo BGM_JBM0031
echo BGM_JBM0032
echo BGM_JBM0033
echo BGM_JBM0034
echo BGM_JBM0035
echo BGM_JBM0036
echo BGM_JBM0037
echo BGM_JBM0038
echo BGM_JBM0039
echo BGM_JBM0040
echo BGM_JBM0041
echo BGM_JBM0042
echo BGM_JBM0043
echo BGM_JBM0044
echo BGM_JBM0045
echo BGM_JBM0046
echo BGM_JBM0047
echo BGM_JBM0048
echo BGM_JBM0051
echo BGM_JBM0052
echo BGM_JBM0053
echo BGM_JBM0054
echo BGM_JBM0061
echo BGM_JBM0062
echo BGM_JBM0063
echo BGM_JBM0064
echo BGM_JBM0065
echo BGM_JBM0066
echo BGM_JBM0067
echo BGM_JBM0073
echo BGM_STG1001
echo BGM_STG1003
echo BGM_STG1005
echo BGM_STG1016
echo BGM_STG1017
echo BGM_STG1018
echo BGM_STG1020
echo BGM_STG1021
echo BGM_STG1022
echo BGM_STG1023
echo BGM_STG1024
echo BGM_STG1025
echo BGM_STG1026
echo BGM_STG1027
echo BGM_STG1028
echo BGM_STG1029
echo BGM_STG1030
echo BGM_STG1031
echo BGM_STG1032
echo BGM_STG1033
echo BGM_STG1034
echo BGM_STG1035
echo BGM_STG1036
echo BGM_STG1037
echo BGM_STG2001
echo BGM_STG2002
echo BGM_STG2003
echo BGM_STG2004
echo BGM_STG2005
echo BGM_STG2007
echo BGM_STG2009
echo BGM_STG2010
echo BGM_STG2011
echo BGM_STG2012
echo BGM_STG2014
echo BGM_STG2015
echo BGM_STG2016
echo BGM_STG2017
echo BGM_STG2019
echo SE_ADV
echo SE_COURSE
echo SE_DSH_51_ENGINE
echo SE_ENGINE
echo SE_EXTND03_CHARA
echo SE_EXTND03_ENGINE
echo SE_EXTND03_HORN
echo SE_EXTND04_CHARA
echo SE_EXTND04_ENGINE
echo SE_EXTND04_HORN
echo SE_EXTND04_STG1503
echo SE_EXTND05_CHARA
echo SE_EXTND05_ENGINE
echo SE_EXTND05_HORN
echo SE_EXTND05_STG1506
echo SE_EXTND10_CHARA
echo SE_EXTND10_ENGINE
echo SE_EXTND10_HORN
echo SE_EXTND11_CHARA
echo SE_EXTND11_ENGINE
echo SE_EXTND11_HORN
echo SE_EXTND12_CHARA
echo SE_EXTND12_ENGINE
echo SE_EXTND12_HORN
echo SE_ITEM
echo SE_MACHINE
echo SE_MENU
echo SE_MOVIE_SOUND
echo SE_OBJ_COMMON
echo SE_OBJ_STG1001
echo SE_OBJ_STG1003
echo SE_OBJ_STG1005
echo SE_OBJ_STG1016
echo SE_OBJ_STG1017
echo SE_OBJ_STG1018
echo SE_OBJ_STG1020
echo SE_OBJ_STG1021
echo SE_OBJ_STG1022
echo SE_OBJ_STG1023
echo SE_OBJ_STG1024
echo SE_OBJ_STG1025
echo SE_OBJ_STG1026
echo SE_OBJ_STG1027
echo SE_OBJ_STG1028
echo SE_OBJ_STG1029
echo SE_OBJ_STG1030
echo SE_OBJ_STG1031
echo SE_OBJ_STG1032
echo SE_OBJ_STG1033
echo SE_OBJ_STG1034
echo SE_OBJ_STG1035
echo SE_OBJ_STG1036
echo SE_OBJ_STG1037
echo SE_OBJ_STG2001
echo SE_OBJ_STG2002
echo SE_OBJ_STG2003
echo SE_OBJ_STG2004
echo SE_OBJ_STG2005
echo SE_OBJ_STG2007
echo SE_OBJ_STG2009
echo SE_OBJ_STG2010
echo SE_OBJ_STG2011
echo SE_OBJ_STG2012
echo SE_OBJ_STG2014
echo SE_OBJ_STG2015
echo SE_OBJ_STG2016
echo SE_OBJ_STG2017
echo SE_OBJ_STG2019
echo SE_POW_51_ENGINE
echo SE_PRIME_CHARA
echo SE_SYS
echo SE_WER_CHARA
echo VIB_COMMON
echo VOICE_AMY
echo VOICE_AMYAI
echo VOICE_ANNOUNCE
echo VOICE_BIG
echo VOICE_BIGAI
echo VOICE_BLA
echo VOICE_BLAAI
echo VOICE_CBT
echo VOICE_CHA
echo VOICE_CHAAI
echo VOICE_CRE
echo VOICE_CREAI
echo VOICE_DOD
echo VOICE_EGG
echo VOICE_EGGAI
echo VOICE_EGP
echo VOICE_EGPAI
echo VOICE_ESP
echo VOICE_ESPAI
echo VOICE_JET
echo VOICE_JETAI
echo VOICE_KNU
echo VOICE_KNUAI
echo VOICE_MET
echo VOICE_METAI
echo VOICE_OBT
echo VOICE_OCH
echo VOICE_OME
echo VOICE_OMEAI
echo VOICE_ROU
echo VOICE_ROUAI
echo VOICE_SAG
echo VOICE_SAGAI
echo VOICE_SHA
echo VOICE_SHAAI
echo VOICE_SIL
echo VOICE_SILAI
echo VOICE_SON
echo VOICE_SONAI
echo VOICE_STO
echo VOICE_STOAI
echo VOICE_TAI
echo VOICE_TAIAI
echo VOICE_VEC
echo VOICE_VECAI
echo VOICE_WAV
echo VOICE_WAVAI
echo VOICE_ZAV
echo VOICE_ZAVAI
echo VOICE_ZAZ
echo VOICE_ZAZAI
echo.
pause
goto Start
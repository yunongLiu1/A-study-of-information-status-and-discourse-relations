# A study of information status and discourse relations
 This is a repo is for the python script and executable file for the project.

# Instructions
## To run the executable file
1. Download the executable file **app.zip** from the repo.
2. Open terminal and navigate to the directory where the app.zip is located.
3. run the executable file with the following command : 
```
./app <PATH_TO_PDTB> <PATH_TO_decorated_Ss_with_preposed_NP-or-PP_no_blank>
```


For example:
```
./app ./data/PDTB-3.0-version2 ./data/decorated_Ss_with_preposed_NP-or-PP_no_blank.txt 
```
The output file will be generated in the same directory as the executable file with the name "full_set_DRels_preposed_constits.txt". 

OR

run the following command to get the output file with customized name and location:
```
./app <PATH_TO_PDTB> <PATH_TO_decorated_Ss_with_preposed_NP-or-PP_no_blank> <PATH_TO_OUTPUT_FILE>
```

For example:
```
./app ./data/PDTB-3.0-version2 ./data/decorated_Ss_with_preposed_NP-or-PP_no_blank.txt ./data/output.txt
```

1. The number of DRel and path of the output file will be displayed in the terminal.

![sample output]( /figure/terminal_output.png)



## Sample output file
The output file will be generated in the same directory as the executable file or the directory specified in the command line. The output file will be in the following format:

![out_file](/figure/sample_output_file.png)
